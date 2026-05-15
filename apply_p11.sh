#!/usr/bin/env bash
# P-1.1: Extend the oneshot pre-pass with library-lemma metis patterns.
#
# Goal: rescue cases where the goal is an instance of a named HOL library
# lemma but the LLM doesn't surface the lemma name. Adds 8 metis patterns
# covering common list/map/rev/length identities.
#
# This is incremental on top of apply_p1_oneshot.sh.

set -e

if [ ! -f planner/driver.py ]; then
    echo "ERROR: must run from repo root" >&2
    exit 1
fi

if ! grep -q "_try_oneshot_proof" planner/driver.py; then
    echo "ERROR: oneshot helper not present. Apply apply_p1_oneshot.sh first." >&2
    exit 1
fi

cp planner/driver.py planner/driver.py.bak.p11
echo "[p1.1] backup: planner/driver.py.bak.p11"

python - << 'PYEOF'
with open('planner/driver.py', 'r') as f:
    text = f.read()

# Find the list of trivial tactics in _try_oneshot_proof and extend it.
# Currently the list is:
#   "by simp", "by auto", "by (simp add: ac_simps)",
#   "by (simp add: algebra_simps)", "by linarith",
#   "by force", "by blast"
# We add 8 metis patterns for common library lemmas.

old = '''    candidates = []
    for tac in ["by simp", "by auto", "by (simp add: ac_simps)",
                "by (simp add: algebra_simps)", "by linarith",
                "by force", "by blast"]:
        candidates.append(f'lemma "{goal}"\\n  {tac}')'''

new = '''    candidates = []
    for tac in ["by simp", "by auto", "by (simp add: ac_simps)",
                "by (simp add: algebra_simps)", "by linarith",
                "by force", "by blast",
                # P-1.1: library-lemma metis patterns. Each names a single
                # HOL library lemma; metis will succeed when the goal is
                # an instance of (or trivially derivable from) that lemma.
                # These cover the most common list / map / rev / length
                # identities; rare and easy to extend.
                "by (metis rev_map)",
                "by (metis map_append)",
                "by (metis rev_append)",
                "by (metis append_assoc)",
                "by (metis length_rev)",
                "by (metis length_map)",
                "by (metis length_append)",
                "by (metis rev_rev_ident)"]:
        candidates.append(f'lemma "{goal}"\\n  {tac}')'''

if old not in text:
    print("ERROR: could not find candidate-list block in _try_oneshot_proof")
    print("Expected to find the 'by simp, by auto, ...' block")
    raise SystemExit(1)

count = text.count(old)
if count != 1:
    print(f"ERROR: expected 1 occurrence, found {count}")
    raise SystemExit(1)

text = text.replace(old, new)

with open('planner/driver.py', 'w') as f:
    f.write(text)

print("[p1.1] driver.py: extended _try_oneshot_proof with 8 metis library patterns")
PYEOF

# Verify it still imports
python -c "import planner.driver; print('[p1.1] driver.py imports OK')"

# Summary diff
echo ""
echo "[p1.1] Change summary:"
diff planner/driver.py.bak.p11 planner/driver.py | grep -cE "^>" | xargs -I {} echo "  Lines added: {}"
diff planner/driver.py.bak.p11 planner/driver.py | grep -cE "^<" | xargs -I {} echo "  Lines removed: {}"

echo ""
echo "[p1.1] DONE - ready to bench"
