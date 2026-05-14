#!/usr/bin/env bash
# Run all ablation configurations sequentially on the smoke set.
# Each config takes ~25 min. Total: ~2 hours for 5 configs.
# set -e disabled: individual bench commands may return non-zero, we want to continue

export PYTHONIOENCODING=utf-8
export ISABELLE_VERIFY_TIMEOUT_S=30

MODEL="qwen2.5-coder:14b"
GOALS="goals/smoke.txt"
T=180

mkdir -p logs

run() {
    local tag="$1"; shift
    echo ""
    echo "==== START $tag $(date +%H:%M:%S) ===="
    python -m planner.experiments bench \
        --file "$GOALS" \
        --model "$MODEL" \
        --timeout "$T" \
        --mode auto \
        --verify \
        "$@" \
        2>&1 | tee "logs/ablation_${tag}.log"
    echo "==== END   $tag $(date +%H:%M:%S) ===="
}

# Baseline (full system) - re-run for direct comparison
run "full"

# Ablations - each removes one component
run "no_repairs"    --no-repairs
run "no_premises"   --no-premises
run "no_context"    --no-context
run "outline_only"  --mode outline

echo ""
echo "==== ALL ABLATIONS DONE $(date +%H:%M:%S) ===="
