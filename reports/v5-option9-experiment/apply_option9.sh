#!/usr/bin/env bash
# Option 9: Expand the finisher candidate pools.
#
# Two changes:
#   1. prover/tactics.py _case_finishers: 3 -> 9 base finishers
#      Adds: by force, by fastforce, by (simp add: ac_simps),
#            by (simp add: algebra_simps), by arith, by linarith
#   2. prover/llm.py base_default: 9 -> 12 finishers
#      Adds: by force, by linarith, by (simp add: algebra_simps)
#
# This is purely additive: every existing tactic is preserved.
# Adding candidates costs nothing if Isabelle rejects them.

set -e

if [ ! -f prover/tactics.py ] || [ ! -f prover/llm.py ]; then
    echo "ERROR: must run from repo root" >&2
    exit 1
fi

# Backup
cp prover/tactics.py prover/tactics.py.bak
cp prover/llm.py prover/llm.py.bak
echo "[option9] backups: prover/tactics.py.bak, prover/llm.py.bak"

# Change 1: tactics.py _case_finishers base list
python3 - << 'PYEOF'
import re

with open('prover/tactics.py', 'r') as f:
    text = f.read()

# Match exactly the current 3-tactic base = [...] in _case_finishers
old = '    base = ["by simp", "by auto", "by blast"]'
new = ('    base = ["by simp", "by auto", "by blast", "by force", "by fastforce",\n'
       '            "by (simp add: ac_simps)", "by (simp add: algebra_simps)",\n'
       '            "by arith", "by linarith"]')

if old not in text:
    print("ERROR: could not find tactics.py _case_finishers base list")
    print("Expected to find: " + repr(old))
    raise SystemExit(1)

count = text.count(old)
if count != 1:
    print(f"ERROR: expected exactly 1 occurrence in tactics.py, found {count}")
    raise SystemExit(1)

text = text.replace(old, new)
with open('prover/tactics.py', 'w') as f:
    f.write(text)

print("[option9] tactics.py _case_finishers: 3 -> 9 finishers")
PYEOF

# Change 2: llm.py base_default
python3 - << 'PYEOF'
import re

with open('prover/llm.py', 'r') as f:
    text = f.read()

old = ('    base_default = ["by simp", "by auto", "by clarsimp",\n'
       '                    "by arith", "by presburger", "by fastforce", "by blast", "by meson", "by (metis)"]')

new = ('    base_default = ["by simp", "by auto", "by clarsimp",\n'
       '                    "by arith", "by presburger", "by fastforce", "by blast", "by meson", "by (metis)",\n'
       '                    "by force", "by linarith", "by (simp add: algebra_simps)"]')

if old not in text:
    print("ERROR: could not find llm.py base_default list")
    print("Expected to find: " + repr(old))
    raise SystemExit(1)

count = text.count(old)
if count != 1:
    print(f"ERROR: expected exactly 1 occurrence in llm.py, found {count}")
    raise SystemExit(1)

text = text.replace(old, new)
with open('prover/llm.py', 'w') as f:
    f.write(text)

print("[option9] llm.py base_default: 9 -> 12 finishers")
PYEOF

# Verify both files still parse
python3 -c "import prover.tactics; import prover.llm; print('[option9] both files parse OK')"

echo "[option9] DONE"
