"""
Mine (goal, premise_used) positive pairs from AFP + HOL proof files.

Strategy: line-by-line walk. Recognise lemma headers via a single anchored
pattern. Within the next N lines (up to next top-level keyword), extract
premise names from 'using ...', 'unfolding ...', and 'by (rule ...)' clauses.
Emit one (goal, premise) record per reference.

Output: training/positives.jsonl with one JSON record per line:
  {"goal_statement": str, "premise_name": str}
"""
import re
import json
import os
from pathlib import Path

AFP_HOME = Path(os.environ.get("AFP_HOME", "/content/afp"))
ISABELLE_HOME = Path(os.environ.get("ISABELLE_HOME", "/content/Isabelle2025-2"))
HOL_HOME = ISABELLE_HOME / "src" / "HOL"

# Top-of-line lemma header. Statement may be on the same line (quoted) or
# may begin with 'assumes' / 'fixes' / 'shows' (structured form).
LEMMA_HEADER_RE = re.compile(
    r'^(?P<kw>lemma|theorem|corollary|proposition)\s+'
    r'(?P<name>[\w\']+)?'             # optional name
    r'(?:\s*\[[^\]]*\])?'             # optional attribute brackets
    r'\s*:\s*'                        # mandatory colon
    r'"(?P<stmt>[^"]+(?:\\.[^"]*)*)"'  # quoted statement
)

# Where the proof block ends (top-level keyword on a new line).
PROOF_END_RE = re.compile(
    r'^(?:lemma|theorem|corollary|proposition|definition|fun|primrec|'
    r'inductive|coinductive|class|locale|datatype|abbreviation|notation|'
    r'context|section|subsection|paragraph|end\b|declare\b|instantiation\b)'
)

# Premise references inside proof body
USING_RE = re.compile(r'\busing\s+([^\n]+?)(?=\s+(?:by|apply|unfolding|with|proof)\b|$)')
UNFOLDING_RE = re.compile(r'\bunfolding\s+([^\n]+?)(?=\s+(?:by|apply|using|with|proof)\b|$)')
BY_RULE_RE = re.compile(r'\b(?:by|apply)\s*\(\s*(?:rule|intro|elim|dest|fact)\s+([\w\'\.\s,]+?)\s*\)')

# Stop-words and pseudo-identifiers that aren't premise names
EXCLUDE = {
    "this", "that", "assms", "True", "False", "Cons", "Nil",
    "Suc", "Some", "None", "Pair", "if", "then", "else",
    "let", "in", "case", "of", "do", "od", "where", "and", "or", "not",
    "OF", "of", "symmetric", "simp", "auto", "blast",
}

MIN_STMT_LEN = 10
MAX_STMT_LEN = 1000


def clean_name(token):
    """Strip [...] suffixes, trailing punctuation."""
    token = token.split("[")[0]
    token = token.strip(".,;()[]{}")
    return token


def extract_names(clause_text):
    """Extract identifier names from a using/unfolding clause text."""
    names = set()
    for tok in re.split(r'[\s,]+', clause_text):
        n = clean_name(tok)
        if not n or n in EXCLUDE or n.startswith("?"):
            continue
        if re.fullmatch(r"[A-Za-z][\w']*(?:\.[\w']+)*", n) and len(n) > 1:
            names.add(n)
    return names


def extract_pairs_from_file(thy_path):
    """Walk file line by line. Yield (goal_statement, premise_name) pairs."""
    try:
        with open(thy_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return

    current_goal = None
    proof_lines_remaining = 0

    for line in lines:
        # Did we find a new lemma header?
        header_match = LEMMA_HEADER_RE.search(line)
        if header_match:
            stmt = header_match.group("stmt").strip()
            if MIN_STMT_LEN <= len(stmt) <= MAX_STMT_LEN:
                current_goal = stmt
                proof_lines_remaining = 40  # scan next 40 lines for premises
            else:
                current_goal = None
                proof_lines_remaining = 0
            continue

        # Reached next top-level definition → reset state
        if PROOF_END_RE.match(line):
            current_goal = None
            proof_lines_remaining = 0
            continue

        # Are we inside a proof body that we're tracking?
        if current_goal is None or proof_lines_remaining <= 0:
            continue
        proof_lines_remaining -= 1

        # Extract premise references from this line
        for m in USING_RE.finditer(line):
            for name in extract_names(m.group(1)):
                yield current_goal, name
        for m in UNFOLDING_RE.finditer(line):
            for name in extract_names(m.group(1)):
                yield current_goal, name
        for m in BY_RULE_RE.finditer(line):
            for name in extract_names(m.group(1)):
                yield current_goal, name


def collect_thy_files():
    files = []
    if HOL_HOME.exists():
        files.extend(HOL_HOME.glob("*.thy"))
    if AFP_HOME.exists():
        thys = AFP_HOME / "thys"
        if thys.exists():
            files.extend(thys.glob("*/**/*.thy"))
    return files


def main():
    out_path = Path("training/positives.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    files = collect_thy_files()
    print(f"Mining from {len(files)} .thy files")
    print(f"  HOL:  {HOL_HOME}")
    print(f"  AFP:  {AFP_HOME / 'thys' if AFP_HOME.exists() else '(missing)'}")
    print()

    n_pairs = 0
    n_unique_goals = set()
    seen = set()

    with out_path.open("w", encoding="utf-8") as f:
        for i, thy_path in enumerate(files):
            for stmt, prem in extract_pairs_from_file(thy_path):
                key = (stmt, prem)
                if key in seen:
                    continue
                seen.add(key)
                n_unique_goals.add(stmt)
                f.write(json.dumps({"goal_statement": stmt, "premise_name": prem}) + "\n")
                n_pairs += 1

            if (i + 1) % 500 == 0:
                print(f"  parsed {i+1}/{len(files)} files | {n_pairs} pairs | {len(n_unique_goals)} unique goals")

    print()
    print(f"DONE")
    print(f"  total pairs: {n_pairs}")
    print(f"  unique goals: {len(n_unique_goals)}")
    print(f"  output: {out_path}")


if __name__ == "__main__":
    main()
