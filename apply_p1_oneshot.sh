#!/usr/bin/env bash
# P-1: Sledgehammer-first one-shot patterns
#
# Adds a pre-pass to plan_and_fill that tries trivial one-shot proofs
# before the LLM is invoked to generate a structured outline. If any
# pattern verifies, we skip the whole outline/fill/repair machinery.
#
# Patterns tried (in order):
#   lemma "{goal}" by simp
#   lemma "{goal}" by auto
#   lemma "{goal}" by (simp add: ac_simps)
#   lemma "{goal}" by (simp add: algebra_simps)
#   lemma "{goal}" by linarith
#   For each free variable v of presumed inductive type:
#     lemma "{goal}" by (induct v) auto
#     lemma "{goal}" by (induct v) simp_all
#     If multi-var goal, also: by (induct v arbitrary: <others>) auto
#
# Each attempt budgets 8 seconds; total budget across all patterns is 60s.
# Cheap to try, returns first success.

set -e

if [ ! -f planner/driver.py ]; then
    echo "ERROR: must run from repo root" >&2
    exit 1
fi

cp planner/driver.py planner/driver.py.bak.p1
echo "[p1] backup: planner/driver.py.bak.p1"

python - << 'PYEOF'
import re

with open('planner/driver.py', 'r') as f:
    text = f.read()

# ============================================================
# Part 1: Add the _try_oneshot_proof helper function
# Inserted right after _extract_session_id helper definition
# ============================================================

helper_marker = '    raise RuntimeError(f"Could not extract session_id from response: {responses!r}")\n'
if helper_marker not in text:
    raise SystemExit("Could not find _extract_session_id end marker - file structure changed")

oneshot_helper = '''

# ---------------------------------------------------------------------------
# P-1: One-shot pre-pass before outline generation
# ---------------------------------------------------------------------------
_INDUCTIVE_VAR_RE = re.compile(r"\\b([a-z][a-zA-Z0-9_]{0,9})\\b")
_NON_INDUCTIVE_TOKENS = {
    "True", "False", "if", "then", "else", "let", "in", "case", "of",
    "do", "fun", "lemma", "by", "and", "or", "not", "the", "some",
    "lambda", "Suc", "rev", "length", "map", "filter", "concat",
    "hd", "tl", "take", "drop", "sum_list", "fold", "foldr", "foldl",
    "min", "max", "abs", "fst", "snd", "id", "comp",
}

def _free_inductive_vars(goal: str):
    """Heuristic extractor of free variables likely to be inductive.

    Looks for lowercase identifiers in the goal text that are not in a
    blocklist of common function/keyword names. The order of returned
    vars reflects appearance in the goal (which is usually the order a
    human would induct on).
    """
    seen = []
    for m in _INDUCTIVE_VAR_RE.finditer(goal):
        v = m.group(1)
        if v in _NON_INDUCTIVE_TOKENS:
            continue
        if v.startswith("_"):
            continue
        if v not in seen:
            seen.append(v)
    return seen

def _try_oneshot_proof(isa, session: str, goal: str, *,
                       budget_s: float = 60.0,
                       per_attempt_s: int = 8,
                       trace: bool = False):
    """Try a small set of one-shot proofs before generating an outline.

    Returns (proof_text, True) on the first success, or (None, False) if
    no pattern works within the budget. Each verify uses the same path
    as the rest of the pipeline (_verify_full_proof), so a True return
    means the result is genuinely verified.
    """
    t0 = time.monotonic()
    def left() -> float: return budget_s - (time.monotonic() - t0)

    # Build the candidate list. Trivial tactics first, then induction patterns.
    candidates = []
    for tac in ["by simp", "by auto", "by (simp add: ac_simps)",
                "by (simp add: algebra_simps)", "by linarith",
                "by force", "by blast"]:
        candidates.append(f'lemma "{goal}"\\n  {tac}')

    fv = _free_inductive_vars(goal)
    if trace and fv:
        print(f"[oneshot] free vars: {fv}")
    if fv:
        v0 = fv[0]
        for inner in ["auto", "simp_all"]:
            candidates.append(f'lemma "{goal}"\\n  by (induct {v0}) {inner}')
        if len(fv) >= 2:
            others = " ".join(fv[1:])
            for inner in ["auto", "simp_all"]:
                candidates.append(f'lemma "{goal}"\\n  by (induct {v0} arbitrary: {others}) {inner}')

    for idx, cand in enumerate(candidates):
        if left() <= 0:
            if trace:
                print(f"[oneshot] budget exhausted after {idx} attempts")
            break
        try:
            ok = _verify_full_proof(isa, session, cand)
        except (TimeoutError, _FuturesTimeout, ValueError):
            ok = None
        if ok is True:
            if trace:
                short = cand.replace("\\n  ", " | ")
                print(f"[oneshot] PROVED: {short}")
            return cand, True
    if trace:
        print(f"[oneshot] no pattern matched ({len(candidates)} attempts)")
    return None, False

'''

# Insert after the helper end marker
text = text.replace(helper_marker, helper_marker + oneshot_helper, 1)

# ============================================================
# Part 2: Insert the oneshot-first call into plan_and_fill
# Look for "    try:\n        # Generate outline\n"
# ============================================================

call_marker = '    try:\n        # Generate outline\n'
call_insert = '''    try:
        # P-1: try one-shot proofs before invoking the outline LLM
        oneshot_text, oneshot_ok = _try_oneshot_proof(isa, session, goal, trace=trace)
        if oneshot_ok:
            return PlanAndFillResult(True, oneshot_text, [], [])

        # Generate outline
'''

if call_marker not in text:
    raise SystemExit("Could not find outline-generation marker in plan_and_fill")
text = text.replace(call_marker, call_insert, 1)

with open('planner/driver.py', 'w') as f:
    f.write(text)

print("[p1] driver.py: oneshot helper added, plan_and_fill pre-pass inserted")
PYEOF

# Verify the file still parses
python -c "import planner.driver; print('[p1] driver.py imports OK')"

# Show what changed (semantic diff)
echo ""
echo "[p1] Change summary:"
diff planner/driver.py.bak.p1 planner/driver.py | grep -cE "^>" | xargs -I {} echo "  Lines added: {}"
diff planner/driver.py.bak.p1 planner/driver.py | grep -cE "^<" | xargs -I {} echo "  Lines removed: {}"

echo ""
echo "[p1] DONE - ready to bench"
