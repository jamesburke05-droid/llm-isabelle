"""
Fine-tune the existing cross-encoder on AFP-augmented training data.

Warm-start from models/premises/rerank/ so we retain HOL knowledge.
Save the fine-tuned model to models/premises/rerank_v2/.
"""
import json
import os
import torch
from pathlib import Path
from sentence_transformers import CrossEncoder, InputExample
from sentence_transformers.cross_encoder.evaluation import CEBinaryClassificationEvaluator
from torch.utils.data import DataLoader

BASE_MODEL_DIR = "models/premises/rerank"
OUTPUT_DIR = "models/premises/rerank_v2"
TRAIN_PATH = "training/train.jsonl"
VAL_PATH = "training/val.jsonl"

# Hyperparameters
BATCH_SIZE = 32
EPOCHS = 2
LR = 2e-5
WARMUP_STEPS_FRAC = 0.1
MAX_LENGTH = 256


def load_jsonl(path):
    examples = []
    with open(path) as f:
        for line in f:
            ex = json.loads(line)
            examples.append(InputExample(
                texts=[ex["goal"], ex["candidate"]],
                label=float(ex["label"])
            ))
    return examples


def main():
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  device: {torch.cuda.get_device_name(0)}")
        print(f"  memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB total")

    print(f"\nLoading {TRAIN_PATH}...")
    train_examples = load_jsonl(TRAIN_PATH)
    print(f"  {len(train_examples)} train examples")

    print(f"Loading {VAL_PATH}...")
    val_examples = load_jsonl(VAL_PATH)
    print(f"  {len(val_examples)} val examples")

    print(f"\nLoading base model from {BASE_MODEL_DIR}...")
    model = CrossEncoder(BASE_MODEL_DIR, num_labels=1, max_length=MAX_LENGTH)

    train_loader = DataLoader(train_examples, shuffle=True, batch_size=BATCH_SIZE)

    val_pairs = [(ex.texts[0], ex.texts[1]) for ex in val_examples]
    val_labels = [int(ex.label) for ex in val_examples]
    evaluator = CEBinaryClassificationEvaluator(
        sentence_pairs=val_pairs,
        labels=val_labels,
        name="afp_aug_val"
    )

    n_steps = len(train_loader) * EPOCHS
    warmup_steps = int(n_steps * WARMUP_STEPS_FRAC)

    print(f"\nTraining config:")
    print(f"  epochs: {EPOCHS}")
    print(f"  batch_size: {BATCH_SIZE}")
    print(f"  total steps: {n_steps}")
    print(f"  warmup steps: {warmup_steps}")
    print(f"  learning rate: {LR}")
    print(f"  mixed precision: True")
    print()

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    model.fit(
        train_dataloader=train_loader,
        epochs=EPOCHS,
        warmup_steps=warmup_steps,
        evaluator=evaluator,
        evaluation_steps=2000,
        output_path=OUTPUT_DIR,
        optimizer_params={"lr": LR},
        use_amp=True,
        show_progress_bar=True,
    )

    print(f"\nDONE — model saved to {OUTPUT_DIR}")
    print("Files written:")
    for f in sorted(Path(OUTPUT_DIR).iterdir()):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"  {f.name}: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
