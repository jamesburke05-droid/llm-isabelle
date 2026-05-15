# Option 9 / 9b Finisher-Pool Expansion Experiment

## Hypothesis
Expanding the candidate finisher pool with stronger tactics (by force,
by linarith, by (simp add: ac_simps), by (simp add: algebra_simps))
would rescue stable-failure goals such as sum_list whose residual is
an associativity rewrite.

## Patches applied (now rolled back)
- prover/tactics.py: _case_finishers expanded 3 -> 9 finishers
- prover/llm.py: base_default expanded 9 -> 12 finishers
- prover/prover.py: 5 extra finishers injected into merged pool

## Results
- bench_smoke_option9 (Option 9, tactics.py + llm.py only): 8/10
- bench_smoke_option9b (Option 9 + injection into prover.py merged pool): 8/10

Both results are within the smoke-set stochastic range (5-run variance:
6-9/10). 0 goals were rescued by the new extras: never closed any goal
in the verified-success column.

## Root cause of null result
Investigation showed the failure mode on goals like sum_list is not
in the fill phase (where the candidate pool operates) but in the
*outline phase*: the LLM commits to "show ?case ... by simp" at
outline-generation time, and that line is a fixed part of the
proof body, not a sorry hole. Fill never touches it. Repair sometimes
targets the wrong block (rewriting an upstream "have" rather than
the failing "show ?case" line).

## Conclusion
Expanding the fill-phase candidate pool cannot fix outline-phase
tactic commitments. Rolled back to HEAD. Reported in Section 7.2
of the main report as a null experiment.
