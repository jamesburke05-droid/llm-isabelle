"""
Build (goal, candidate, label) training examples for cross-encoder fine-tuning.

For each goal:
  - Resolve premise names to actual statement text via the v2 corpus
  - Emit (goal, premise_stmt, label=1) positive examples
  - Sample K hard negatives via bi-encoder top-K retrieval, excluding positives
  - Emit (goal, negative_stmt, label=0) examples

Output: training/train.jsonl, training/val.jsonl  (90/10 split, shuffled)
"""
import json
import random
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, "/content/llm-isabelle")

# Import the existing Micro RAG to reuse its bi-encoder + corpus loader.
from planner.micro_rag import MicroRAG, CORPUS_FILE

random.seed(42)
NEGATIVES_PER_POSITIVE = 3
TRAIN_VAL_SPLIT = 0.9


def load_corpus_index():
    """Build {name: statement} lookup from the v2 corpus.jsonl."""
    print(f"Loading corpus from {CORPUS_FILE}...")
    name_to_stmt = {}
    with open(CORPUS_FILE) as f:
        for line in f:
            entry = json.loads(line)
            name_to_stmt[entry["name"]] = entry["statement"]
    print(f"  loaded {len(name_to_stmt)} corpus entries")
    return name_to_stmt


def load_positives():
    """Group positives by goal: {goal_statement: set(premise_names)}."""
    print("Loading mined positives...")
    goal_to_premises = defaultdict(set)
    n_pairs = 0
    with open("training/positives.jsonl") as f:
        for line in f:
            p = json.loads(line)
            goal_to_premises[p["goal_statement"]].add(p["premise_name"])
            n_pairs += 1
    print(f"  {n_pairs} pairs across {len(goal_to_premises)} unique goals")
    return goal_to_premises


def resolve_premise(name, name_to_stmt):
    """Look up premise statement.
    Try exact match first; the v2 corpus uses 'Theory.name' format so we
    also try suffix-matching against the bare name.
    """
    if name in name_to_stmt:
        return name_to_stmt[name]
    # Suffix match: 'append.assoc' may be stored as 'List.append.assoc'
    for key in name_to_stmt:
        if key.endswith("." + name) or key == name:
            return name_to_stmt[key]
    return None


def main():
    name_to_stmt = load_corpus_index()
    goal_to_premises = load_positives()

    print("Loading Micro RAG bi-encoder for hard-negative sampling...")
    rag = MicroRAG(use_cross_encoder=False)
    rag.build_or_load()
    print("  ready")

    train_examples = []
    n_unresolved = 0
    n_no_positives = 0

    for i, (goal, premise_names) in enumerate(goal_to_premises.items()):
        # Positive examples — only those where we can resolve to a statement
        pos_statements = []
        for pname in premise_names:
            stmt = resolve_premise(pname, name_to_stmt)
            if stmt:
                pos_statements.append(stmt)
            else:
                n_unresolved += 1

        if not pos_statements:
            n_no_positives += 1
            continue

        # Dedupe positives by statement text (multiple premise names may have same body)
        pos_set = set(pos_statements)
        for ps in pos_set:
            train_examples.append({"goal": goal, "candidate": ps, "label": 1})

        # Hard negatives: bi-encoder top-K retrievals that aren't in positive set
        try:
            hits = rag.retrieve(goal, k=20)
        except Exception as e:
            continue  # skip goals that fail retrieval

        target_negs = NEGATIVES_PER_POSITIVE * len(pos_set)
        neg_count = 0
        for h in hits:
            if h["statement"] not in pos_set:
                train_examples.append({
                    "goal": goal,
                    "candidate": h["statement"],
                    "label": 0
                })
                neg_count += 1
                if neg_count >= target_negs:
                    break

        if (i + 1) % 2000 == 0:
            print(f"  processed {i+1}/{len(goal_to_premises)} goals | "
                  f"{len(train_examples)} examples")

    # Shuffle and split
    random.shuffle(train_examples)
    split = int(len(train_examples) * TRAIN_VAL_SPLIT)

    Path("training").mkdir(exist_ok=True)
    with open("training/train.jsonl", "w") as f:
        for ex in train_examples[:split]:
            f.write(json.dumps(ex) + "\n")
    with open("training/val.jsonl", "w") as f:
        for ex in train_examples[split:]:
            f.write(json.dumps(ex) + "\n")

    n_pos = sum(1 for e in train_examples if e["label"] == 1)
    n_neg = sum(1 for e in train_examples if e["label"] == 0)

    print()
    print("DONE")
    print(f"  total examples: {len(train_examples)}")
    print(f"    positives: {n_pos}")
    print(f"    negatives: {n_neg}")
    print(f"    pos:neg ratio: 1:{n_neg/max(n_pos,1):.2f}")
    print(f"  unresolved premise names (no corpus match): {n_unresolved}")
    print(f"  goals dropped (zero resolvable positives): {n_no_positives}")
    print(f"  train: {split} -> training/train.jsonl")
    print(f"  val:   {len(train_examples)-split} -> training/val.jsonl")


if __name__ == "__main__":
    main()
