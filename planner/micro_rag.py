"""
Micro RAG: lightweight retrieval over the HOL standard library.

Implements the assignment specification's "Micro RAG extracted from AFP"
feature in scaled-down form, indexing standard HOL theories (List, Nat,
Set, etc.) plus sentence-transformer dense-embedding similarity retrieval.

Usage:
    from planner.micro_rag import MicroRAG
    rag = MicroRAG()
    rag.build_or_load()
    hits = rag.retrieve("length (rev xs) = length xs", k=5)
    # hits = [{'name': 'List.length_rev', 'statement': '...', 'theory': 'List', 'score': 0.82}, ...]
"""

from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Optional

# Default HOL theories to index. Paths constructed from ISABELLE_HOME at runtime.
DEFAULT_THEORY_NAMES = [
    "List",
    "Nat",
    "Set",
    "Map",
    "Finite_Set",
    "Real",
    "Num",
]

# Default index cache location (under repo, gitignored if you wish)
INDEX_DIR = Path("models/micro_rag")
CORPUS_FILE = INDEX_DIR / "corpus.jsonl"
EMBEDDINGS_FILE = INDEX_DIR / "embeddings.npy"
METADATA_FILE = INDEX_DIR / "micro_rag.json"

# Regex to extract theorem-like declarations from .thy files.
# Captures: keyword, name, optional attribute brackets, then quoted statement.
# Supports multi-line quoted statements via DOTALL.
LEMMA_RE = re.compile(
    r'(?:\b(?:lemma|theorem|corollary|proposition))\s+'
    r'([a-zA-Z_][\w\.\']*)\s*'         # name (allow dots and primes)
    r'(?:\[[^\]]{0,200}\])?\s*'         # optional attribute brackets
    r':\s*'
    r'"([^"]{10,500})"',                # quoted statement, 10-500 chars
    re.MULTILINE | re.DOTALL,
)

COMMENT_RE = re.compile(r'\(\*.*?\*\)', re.DOTALL)
WHITESPACE_RE = re.compile(r'\s+')


def _strip_comments(text: str) -> str:
    """Remove Isabelle (* ... *) comments. Non-nested only (simple version)."""
    return COMMENT_RE.sub(' ', text)


def _normalise_statement(stmt: str) -> str:
    """Collapse whitespace, trim. Keep symbolic content intact."""
    return WHITESPACE_RE.sub(' ', stmt).strip()


def parse_theory_file(path: str) -> List[Dict]:
    """Extract lemma declarations from a single .thy file.

    Returns list of dicts with keys: name, statement, theory.
    """
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
        # Dedupe within file (same name appearing twice)
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
    """Resolve theory names to absolute file paths under ISABELLE_HOME."""
    isabelle_home = os.environ.get("ISABELLE_HOME", "")
    if not isabelle_home:
        raise RuntimeError(
            "ISABELLE_HOME not set. Set it to your Isabelle installation root "
            "(e.g. C:/Isabelle2025-2/Isabelle2025-2 on Windows)."
        )
    paths = []
    for name in theory_names:
        candidate = Path(isabelle_home) / "src" / "HOL" / f"{name}.thy"
        if candidate.exists():
            paths.append(str(candidate))
        else:
            print(f"[micro_rag] warning: theory file not found: {candidate}")
    return paths


class MicroRAG:
    """Retrieval over the HOL standard library using dense embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.corpus: List[Dict] = []
        self.embeddings = None
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def build_index(self, theory_names: Optional[List[str]] = None) -> None:
        """Parse theories, embed statements, save corpus + embeddings to disk."""
        import numpy as np

        theory_names = theory_names or DEFAULT_THEORY_NAMES
        theory_paths = collect_theory_paths(theory_names)
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        # Parse each theory file
        all_entries: List[Dict] = []
        for path in theory_paths:
            entries = parse_theory_file(path)
            all_entries.extend(entries)
            print(f"[micro_rag] parsed {Path(path).stem}: {len(entries)} lemmas")

        if not all_entries:
            print("[micro_rag] WARNING: no lemmas extracted; check theory paths and regex")
            return

        print(f"[micro_rag] total corpus: {len(all_entries)} lemmas")

        # Embed
        model = self._load_model()
        statements = [e['statement'] for e in all_entries]
        print(f"[micro_rag] encoding {len(statements)} statements...")
        embeddings = model.encode(
            statements,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        print(f"[micro_rag] embedding shape: {embeddings.shape}")

        # Save corpus + embeddings + metadata
        with open(CORPUS_FILE, 'w', encoding='utf-8') as f:
            for e in all_entries:
                f.write(json.dumps(e) + '\n')
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
        print(f"[micro_rag] index saved to {INDEX_DIR}/")

    def load_index(self) -> bool:
        """Load existing index from disk. Returns True on success."""
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
        """Load cached index if present, otherwise build from scratch."""
        if not self.load_index():
            self.build_index(theory_names)
        else:
            print(f"[micro_rag] loaded cached index: {len(self.corpus)} lemmas")

    def retrieve(self, goal_text: str, k: int = 5) -> List[Dict]:
        """Return top-K nearest indexed lemmas to the goal text."""
        import numpy as np
        if self.embeddings is None or not self.corpus:
            return []
        model = self._load_model()
        q_emb = model.encode(
            [goal_text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]
        # Embeddings are unit-normalised so dot-product equals cosine similarity
        sims = self.embeddings @ q_emb
        top_idx = np.argsort(-sims)[:k]
        return [
            dict(self.corpus[i], score=float(sims[i]))
            for i in top_idx
        ]

    def format_for_prompt(self, retrieved: List[Dict]) -> str:
        """Format retrieval results as a prompt section."""
        if not retrieved:
            return ""
        lines = ["Relevant library lemmas:"]
        for r in retrieved:
            lines.append(f"  {r['name']}: {r['statement']}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Standalone smoke test - build index and demo a retrieval
    rag = MicroRAG()
    rag.build_or_load()
    print()
    print("=== Retrieval demo ===")
    for query in [
        "length (rev xs) = length xs",
        "rev (rev xs) = xs",
        "Suc n + m = Suc (n + m)",
    ]:
        hits = rag.retrieve(query, k=5)
        print(f"\nQuery: {query}")
        for h in hits:
            print(f"  [{h['score']:.3f}] {h['name']}: {h['statement'][:80]}")