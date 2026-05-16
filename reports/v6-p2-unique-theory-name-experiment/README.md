# P-2: Per-Call Unique Theory Names (rolled back)

## Hypothesis
The bench-side verifier sometimes rejects proofs that the planner's
internal verifier accepted, in the same session. We suspected Isabelle
session-state contamination: every run_theory call uses theories=["Scratch"]
in the same session, so consecutive calls might be treated as theory
reloads that leave residual state.

## Patch (now rolled back)
In prover/isabelle_api.py, generate a unique theory name per
run_theory call (Scratch_<12-char-hex>), rewrite "theory Scratch" in
the theory text, write the file with the new name, and pass the new
name to use_theories.

## Result
list_nat (in-order, with P-2 + p1.1):  14/20 = 70%
Previously without P-2:                15/20 to 19/20 (variable)

P-2 did not improve the situation and may have made it slightly worse.
Three goals failed with verified_ok=False on simp-closable lemmas
(length (xs @ xs) = 2 * length xs, sum_list (map f []) = 0, xs @ [] = xs).
Investigation showed the bug we were chasing was actually two distinct
issues:

1. A bench-accounting bug where verified_ok defaulted to True on
   planner crash. Fixed separately as P-3.
2. Transient Ollama 500 errors during outline generation that
   propagated as hard goal failures. Mitigated by P-3's retry logic.

The Scratch-theory-name hypothesis was wrong; rolled back to HEAD.

## Files
- apply_p2.sh: the patch script
- 20260516-101836: list_nat with P-2 active (14/20)
- 20260516-103135: n+0=n solo sanity check (1/1, confirmed P-2
  didn't break basic operation)
- 20260516-113156: list_nat with P-2 active second run (15/20)
