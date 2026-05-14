#!/usr/bin/env bash
# Run the two non-smoke datasets sequentially.
# Total runtime estimate: ~90 minutes.

export PYTHONIOENCODING=utf-8
export ISABELLE_VERIFY_TIMEOUT_S=30

MODEL="qwen2.5-coder:14b"
T=180

mkdir -p logs

run_dataset() {
    local tag="$1"
    local goals_file="$2"
    echo ""
    echo "==== START $tag $(date +%H:%M:%S) ===="
    python -m planner.experiments bench \
        --file "$goals_file" \
        --model "$MODEL" \
        --timeout "$T" \
        --mode auto \
        --verify \
        --trace \
        2>&1 | tee "logs/bench_${tag}.log"
    echo "==== END   $tag $(date +%H:%M:%S) ===="
}

run_dataset "list_nat" "goals/list_nat_induction.txt"
run_dataset "minif2f"  "goals/minif2f_induction.txt"

echo ""
echo "==== ALL DATASET BENCHES DONE $(date +%H:%M:%S) ===="
