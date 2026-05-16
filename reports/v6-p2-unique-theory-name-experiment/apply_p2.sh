#!/usr/bin/env bash
# P-2: Per-call unique theory names in run_theory
#
# The bug: every run_theory call uses theories=["Scratch"] with a file
# named Scratch.thy. Isabelle treats consecutive calls in the same session
# as reloads of the same theory, so state from prior calls (theorems
# registered, namespace pollution) affects subsequent verifies.
#
# Symptom: oneshot's _verify_full_proof and the bench's _verify_full_isar
# return different results on the same proof text in the same session.
#
# Fix: each run_theory call generates a unique theory name (e.g. Scratch_xxx)
# and:
#   - rewrites "theory Scratch" in the input text to "theory <unique>"
#   - writes the file as <unique>.thy
#   - passes theories=[<unique>] to use_theories
#
# This is purely additive at the call boundary. Upstream code (build_theory,
# _header) is unchanged - we substitute at the run_theory layer.

set -e

if [ ! -f prover/isabelle_api.py ]; then
    echo "ERROR: must run from repo root" >&2
    exit 1
fi

cp prover/isabelle_api.py prover/isabelle_api.py.bak.p2
echo "[p2] backup: prover/isabelle_api.py.bak.p2"

python - << 'PYEOF'
import re

with open('prover/isabelle_api.py', 'r') as f:
    text = f.read()

# Replace the body of run_theory to use a unique theory name per call.
# We anchor on the existing tmpdir + open block and the two use_theories
# call sites.

old = '''    tmpdir = tempfile.TemporaryDirectory()
    try:
        p = os.path.join(tmpdir.name, "Scratch.thy")
        with open(p, "w", encoding="utf-8") as f:
            f.write(theory_text)

        # Resolve wall-clock timeout (seconds)
        if timeout_s is None:
            timeout_s = int(ISABELLE_USE_THEORIES_TIMEOUT_S or 0)
        else:
            try:
                timeout_s = int(timeout_s)
            except Exception:
                timeout_s = 0
        if timeout_s > 0:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(
                    _use_theories_call,
                    isabelle,
                    session_id=session_id,
                    master_dir=_to_cygwin_path(tmpdir.name),   # <-- changed
                    timeout_s=timeout_s,
                )
                try:
                    return fut.result(timeout=timeout_s)
                except FuturesTimeout:
                    global _use_timeouts
                    _use_timeouts += 1
                    _last_call_timed_out = True
                    return []

        # No timeout requested → direct call
        return list(isabelle.use_theories(
            theories=["Scratch"],
            session_id=session_id,
            master_dir=_to_cygwin_path(tmpdir.name),
        ))
    finally:
        tmpdir.cleanup()'''

new = '''    # P-2: per-call unique theory name to avoid Isabelle session-state
    # contamination across consecutive use_theories calls.
    import uuid as _uuid
    _theory_name = f"Scratch_{_uuid.uuid4().hex[:12]}"
    _patched_text = re.sub(r"\\\\btheory\\\\s+Scratch\\\\b", f"theory {_theory_name}", theory_text, count=1)

    tmpdir = tempfile.TemporaryDirectory()
    try:
        p = os.path.join(tmpdir.name, f"{_theory_name}.thy")
        with open(p, "w", encoding="utf-8") as f:
            f.write(_patched_text)

        # Resolve wall-clock timeout (seconds)
        if timeout_s is None:
            timeout_s = int(ISABELLE_USE_THEORIES_TIMEOUT_S or 0)
        else:
            try:
                timeout_s = int(timeout_s)
            except Exception:
                timeout_s = 0
        if timeout_s > 0:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(
                    _use_theories_call_named,
                    isabelle,
                    theory_name=_theory_name,
                    session_id=session_id,
                    master_dir=_to_cygwin_path(tmpdir.name),
                    timeout_s=timeout_s,
                )
                try:
                    return fut.result(timeout=timeout_s)
                except FuturesTimeout:
                    global _use_timeouts
                    _use_timeouts += 1
                    _last_call_timed_out = True
                    return []

        # No timeout requested → direct call
        return list(isabelle.use_theories(
            theories=[_theory_name],
            session_id=session_id,
            master_dir=_to_cygwin_path(tmpdir.name),
        ))
    finally:
        tmpdir.cleanup()'''

if old not in text:
    print("ERROR: could not find run_theory body to patch")
    raise SystemExit(1)

text = text.replace(old, new, 1)

# Also add a _use_theories_call_named helper right after _use_theories_call.
# Easiest: insert right after the existing _use_theories_call definition.

old_helper = '''def _use_theories_call(isabelle, *, session_id: str, master_dir: str, timeout_s: Optional[int] = None) -> List[IsabelleResponse]:
    """Internal: best-effort pass through native timeout kwargs (if supported)."""
    if timeout_s is not None and int(timeout_s or 0) > 0:
        # Try native timeout kwarg spellings first (best-effort). Some clients ignore these,
        # so the caller still enforces a wall-clock timeout via Future.result(...).
        for kw in _TIMEOUT_KWARGS:
            try:
                return list(
                    isabelle.use_theories(
                        theories=["Scratch"], session_id=session_id, master_dir=master_dir, **{kw: int(timeout_s)}
                    )
                )
            except TypeError:
                continue
            except Exception:
                return []
    return list(isabelle.use_theories(theories=["Scratch"], session_id=session_id, master_dir=master_dir))'''

new_helper = old_helper + '''


def _use_theories_call_named(isabelle, *, theory_name: str, session_id: str, master_dir: str, timeout_s: Optional[int] = None) -> List[IsabelleResponse]:
    """Internal: like _use_theories_call but with a caller-provided theory name."""
    if timeout_s is not None and int(timeout_s or 0) > 0:
        for kw in _TIMEOUT_KWARGS:
            try:
                return list(
                    isabelle.use_theories(
                        theories=[theory_name], session_id=session_id, master_dir=master_dir, **{kw: int(timeout_s)}
                    )
                )
            except TypeError:
                continue
            except Exception:
                return []
    return list(isabelle.use_theories(theories=[theory_name], session_id=session_id, master_dir=master_dir))'''

if old_helper not in text:
    print("ERROR: could not find _use_theories_call helper to extend")
    raise SystemExit(1)

text = text.replace(old_helper, new_helper, 1)

with open('prover/isabelle_api.py', 'w') as f:
    f.write(text)

print("[p2] isabelle_api.py: run_theory now uses per-call unique theory names")
PYEOF

# Verify it still imports
python -c "import prover.isabelle_api; print('[p2] isabelle_api.py imports OK')"

# Summary diff
echo ""
echo "[p2] Change summary:"
diff prover/isabelle_api.py.bak.p2 prover/isabelle_api.py | grep -cE "^>" | xargs -I {} echo "  Lines added: {}"
diff prover/isabelle_api.py.bak.p2 prover/isabelle_api.py | grep -cE "^<" | xargs -I {} echo "  Lines removed: {}"

echo ""
echo "[p2] DONE - ready to test on n+0 solo to verify, then list_nat"
