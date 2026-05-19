"""
Micro RAG: lightweight retrieval over the HOL standard library.

Implements the assignment specification's "Micro RAG extracted from AFP"
feature in scaled-down form, indexing standard HOL theories (List, Nat,
Set, etc.) plus sentence-transformer dense-embedding similarity retrieval.

Optional cross-encoder re-ranking layer: when use_cross_encoder=True,
bi-encoder retrieves top_k_dense (default 20) candidates and a trained
cross-encoder re-ranks them; only the top k are returned. This improves
precision at the cost of approximately one extra second per goal.

Usage:
    from planner.micro_rag import MicroRAG
    rag = MicroRAG(use_cross_encoder=True)  # opt-in re-ranking
    rag.build_or_load()
    hits = rag.retrieve("length (rev xs) = length xs", k=5)
"""

from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

DEFAULT_THEORY_NAMES = [
    "List", "Nat", "Set", "Map", "Finite_Set", "Real", "Num",
]

# AFP scanning: if AFP_HOME env var is set, the build also scans all .thy files
# under $AFP_HOME/thys/<entry>/*.thy. Used for Tier 3 (full-AFP) Micro RAG.
AFP_HOME_ENV = "AFP_HOME"

INDEX_DIR = Path("models/micro_rag")
# Index version. Bump when corpus selection changes (e.g., HOL-only → HOL+AFP).
# This avoids silently loading a stale cache after a corpus change.
INDEX_VERSION = "v2"  # v1 was HOL-only (2,113 lemmas); v2 includes full AFP
CORPUS_FILE = INDEX_DIR / f"corpus.{INDEX_VERSION}.jsonl"
EMBEDDINGS_FILE = INDEX_DIR / f"embeddings.{INDEX_VERSION}.npy"
METADATA_FILE = INDEX_DIR / f"micro_rag.{INDEX_VERSION}.json"

# Default location of the trained cross-encoder (from premise selection training)
DEFAULT_CROSS_ENCODER_DIR = Path("models/premises")
CROSS_ENCODER_META_FILE = "premises_reranker.json"

LEMMA_RE = re.compile(
    r'(?:\b(?:lemma|theorem|corollary|proposition))\s+'
    r'([a-zA-Z_][\w\.\']*)\s*'
    r'(?:\[[^\]]{0,200}\])?\s*'
    r':\s*'
    r'"([^"]{10,500})"',
    re.MULTILINE | re.DOTALL,
)

COMMENT_RE = re.compile(r'\(\*.*?\*\)', re.DOTALL)
WHITESPACE_RE = re.compile(r'\s+')


def _strip_comments(text: str) -> str:
    return COMMENT_RE.sub(' ', text)


def _normalise_statement(stmt: str) -> str:
    return WHITESPACE_RE.sub(' ', stmt).strip()


def parse_theory_file(path: str) -> List[Dict]:
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return []
    content = _strip_comments(content)
    theory_name = Path(path).stem
    results: List[Dict] = []
    seen_names = set()
    for match in LEMMA_RE.finditer(content):
        name = match.group(1)
        statement = _normalise_statement(match.group(2))
        if not statement or len(statement) < 10 or len(statement) > 500:
            continue
        full_name = f"{theory_name}.{name}"
        if full_name in seen_names:
            continue
        seen_names.add(full_name)
        results.append({
            'name': full_name,
            'statement': statement,
            'theory': theory_name,
        })
    return results


def collect_theory_paths(theory_names: List[str]) -> List[str]:
    """Resolve theory names to absolute paths.

    Returns paths from:
    1. ISABELLE_HOME/src/HOL/<name>.thy for each name in theory_names
    2. If AFP_HOME is set, every .thy file under AFP_HOME/thys/
    """
    paths: List[str] = []

    # 1. HOL standard library
    isabelle_home = os.environ.get("ISABELLE_HOME", "")
    if not isabelle_home:
        raise RuntimeError(
            "ISABELLE_HOME not set. Set it to your Isabelle installation root."
        )
    for name in theory_names:
        candidate = Path(isabelle_home) / "src" / "HOL" / f"{name}.thy"
        if candidate.exists():
            paths.append(str(candidate))
        else:
            print(f"[micro_rag] warning: HOL theory file not found: {candidate}")

    # 2. Optional AFP
    afp_home = os.environ.get(AFP_HOME_ENV, "")
    if afp_home:
        afp_thys = Path(afp_home) / "thys"
        if afp_thys.exists():
            afp_thy_files = sorted(afp_thys.glob("*/**/*.thy"))
            print(f"[micro_rag] AFP detected at {afp_home}: "
                  f"{len(afp_thy_files)} .thy files across "
                  f"{len(list(afp_thys.iterdir()))} entries")
            paths.extend(str(p) for p in afp_thy_files)
        else:
            print(f"[micro_rag] warning: AFP_HOME set but {afp_thys} does not exist")

    return paths


class MicroRAG:
    """Retrieval over the HOL standard library using dense embeddings.

    Optional second stage: when use_cross_encoder=True, a trained
    sentence-transformers CrossEncoder re-ranks the bi-encoder's top
    candidates for higher-precision final retrieval.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_cross_encoder: bool = False,
        cross_encoder_model_dir: Optional[str] = None,
        top_k_dense: int = 20,
    ):
        self.model_name = model_name
        self.corpus: List[Dict] = []
        self.embeddings = None
        self._model = None
        # Cross-encoder re-ranking
        self.use_cross_encoder = bool(use_cross_encoder)
        self.cross_encoder_model_dir = (
            cross_encoder_model_dir or str(DEFAULT_CROSS_ENCODER_DIR)
        )
        self.top_k_dense = int(top_k_dense)
        self._cross_encoder = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _load_cross_encoder(self):
        """Lazy-load the trained cross-encoder from disk.

        Reads metadata from models/premises/premises_reranker.json which
        identifies the cross-encoder subdirectory. Caches the predict callable.
        Returns None if loading fails (caller falls back to bi-encoder only).
        """
        if self._cross_encoder is not None:
            return self._cross_encoder
        if not self.use_cross_encoder:
            return None
        try:
            meta_path = Path(self.cross_encoder_model_dir) / CROSS_ENCODER_META_FILE
            if not meta_path.exists():
                print(f"[micro_rag] cross-encoder metadata not found at {meta_path}; "
                      "falling back to bi-encoder only")
                self.use_cross_encoder = False
                return None
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if str(meta.get("type", "")) != "sbert-cross":
                print(f"[micro_rag] unsupported cross-encoder type in {meta_path}; "
                      "falling back to bi-encoder only")
                self.use_cross_encoder = False
                return None
            rel = meta.get("model_relpath", "rerank")
            mdir = str(Path(self.cross_encoder_model_dir) / rel)
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(mdir)
            def _score_pairs(pairs: List[Tuple[str, str]]) -> List[float]:
                return model.predict(pairs).tolist()
            self._cross_encoder = _score_pairs
            print(f"[micro_rag] cross-encoder re-ranking enabled "
                  f"(top_k_dense={self.top_k_dense}, model_dir={mdir})")
            return self._cross_encoder
        except Exception as ex:
            print(f"[micro_rag] cross-encoder load failed: {ex}; "
                  "falling back to bi-encoder only")
            self.use_cross_encoder = False
            return None

    def build_index(self, theory_names: Optional[List[str]] = None) -> None:
        import numpy as np
        theory_names = theory_names or DEFAULT_THEORY_NAMES
        theory_paths = collect_theory_paths(theory_names)
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        all_entries: List[Dict] = []
        for path in theory_paths:
            entries = parse_theory_file(path)
            all_entries.extend(entries)
            print(f"[micro_rag] parsed {Path(path).stem}: {len(entries)} lemmas")
        if not all_entries:
            print("[micro_rag] WARNING: no lemmas extracted")
            return
        print(f"[micro_rag] total corpus: {len(all_entries)} lemmas")
        model = self._load_model()
        statements = [e['statement'] for e in all_entries]
        print(f"[micro_rag] encoding {len(statements)} statements...")
        embeddings = model.encode(
            statements, batch_size=32, show_progress_bar=True,
            convert_to_numpy=True, normalize_embeddings=True,
        )
        with open(CORPUS_FILE, 'w', encoding='utf-8') as f:
            for e in all_entries:
                f.write(json.dumps(e) + '\n')
        import numpy as np
        np.save(EMBEDDINGS_FILE, embeddings)
        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'model_name': self.model_name,
                'corpus_size': len(all_entries),
                'embedding_dim': int(embeddings.shape[1]),
                'theory_names': theory_names,
                'normalize_embeddings': True,
            }, f, indent=2)
        self.corpus = all_entries
        self.embeddings = embeddings

    def load_index(self) -> bool:
        import numpy as np
        if not (CORPUS_FILE.exists() and EMBEDDINGS_FILE.exists()):
            return False
        self.corpus = []
        with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    self.corpus.append(json.loads(line))
        self.embeddings = np.load(EMBEDDINGS_FILE)
        return True

    def build_or_load(self, theory_names: Optional[List[str]] = None) -> None:
        if not self.load_index():
            self.build_index(theory_names)
        else:
            print(f"[micro_rag] loaded cached index: {len(self.corpus)} lemmas")

    def retrieve(self, goal_text: str, k: int = 5) -> List[Dict]:
        """Return top-k nearest indexed lemmas to the goal text.

        When use_cross_encoder=True, retrieves top_k_dense candidates from
        the bi-encoder, re-ranks them with the trained cross-encoder, and
        returns the top k re-ranked. The 'score' field reflects the
        re-ranked cross-encoder score.

        When use_cross_encoder=False (default), returns top k by bi-encoder
        cosine similarity directly.
        """
        import numpy as np
        if self.embeddings is None or not self.corpus:
            return []

        model = self._load_model()
        q_emb = model.encode(
            [goal_text], convert_to_numpy=True, normalize_embeddings=True,
        )[0]
        # Normalised embeddings → dot product equals cosine similarity
        sims = self.embeddings @ q_emb

        # Without cross-encoder: simple top-k by bi-encoder similarity
        if not self.use_cross_encoder:
            top_idx = np.argsort(-sims)[:k]
            return [
                dict(self.corpus[i], score=float(sims[i]))
                for i in top_idx
            ]

        # With cross-encoder: bi-encoder retrieves top_k_dense, cross-encoder re-ranks
        cross = self._load_cross_encoder()
        if cross is None:
            # Loading failed; fall back to bi-encoder only
            top_idx = np.argsort(-sims)[:k]
            return [
                dict(self.corpus[i], score=float(sims[i]))
                for i in top_idx
            ]

        dense_top = np.argsort(-sims)[: self.top_k_dense]
        pairs = [
            (goal_text, self.corpus[i]['statement'])
            for i in dense_top
        ]
        try:
            ce_scores = cross(pairs)
        except Exception as ex:
            print(f"[micro_rag] cross-encoder predict failed: {ex}; "
                  "falling back to bi-encoder scores")
            top_idx = np.argsort(-sims)[:k]
            return [
                dict(self.corpus[i], score=float(sims[i]))
                for i in top_idx
            ]

        # Sort the dense_top candidates by cross-encoder score, descending
        scored = list(zip(dense_top.tolist(), ce_scores))
        scored.sort(key=lambda x: -x[1])
        final_top = scored[:k]

        return [
            dict(self.corpus[i], score=float(s))
            for i, s in final_top
        ]


if __name__ == "__main__":
    # Standalone smoke test
    import sys
    use_ce = "--cross-encoder" in sys.argv
    print(f"=== Micro RAG smoke test (use_cross_encoder={use_ce}) ===")
    rag = MicroRAG(use_cross_encoder=use_ce)
    rag.build_or_load()
    print()
    for query in [
        "length (rev xs) = length xs",
        "rev (rev xs) = xs",
        "Suc n + m = Suc (n + m)",
    ]:
        hits = rag.retrieve(query, k=5)
        print(f"Query: {query}")
        for h in hits:
            print(f"  [{h['score']:.3f}] {h['name']}: {h['statement'][:80]}")
        print()