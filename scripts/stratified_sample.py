#!/usr/bin/env python3
"""Stratified sampler: extract one representative goal per pattern.

The lecturer's corpus files (hol_main_easy_goals.txt, hol_main_mid_goals.txt,
hol_main_hard_goals.txt) contain large numbers of goals that are renamings of
a smaller set of patterns. Each pattern occurs 100-500 times, with identifier
suffixes (P0, x12, R5) numbered differently across the variants.

For benching we want a representative sample, not the full 23,000+ goals.
The natural sample is one goal per normalized pattern.

  hol_main_easy_goals.txt:   2,900 goals -> 114 patterns
  hol_main_mid_goals.txt:    5,000 goals -> 147 patterns
  hol_main_hard_goals.txt:  23,000 goals ->  93 patterns

Usage:
    python3 scripts/stratified_sample.py datasets/hol_main_hard_goals.txt \
                                         datasets/hol_main_hard_sample.txt
"""

import re
import sys
from collections import OrderedDict


def normalize(line: str) -> str:
    """Strip numeric suffixes from identifiers so renamings collapse.

    Examples:
        'P0 x0' -> 'PN xN'
        'P12 x5' -> 'PN xN'
        'foo bar' -> 'foo bar'  (unchanged; no digits)

    The transform is conservative: only identifiers that look like
    base-letters-followed-by-digits (P0, x12, R5) are normalized. Standalone
    digits (e.g. '0', '1', '2' as numeric literals) and tokens without
    a numeric suffix are left untouched.
    """
    return re.sub(r'\b([A-Za-z]+)\d+\b', r'\1N', line)


def main(src_path: str, dst_path: str) -> None:
    with open(src_path, 'r', encoding='utf-8') as f:
        raw_lines = [ln.rstrip('\r\n') for ln in f]
    lines = [ln.strip() for ln in raw_lines if ln.strip()]

    # OrderedDict preserves the first occurrence of each pattern.
    # This is deterministic: the same input always produces the same sample.
    samples = OrderedDict()
    for ln in lines:
        key = normalize(ln)
        if key not in samples:
            samples[key] = ln

    sampled = list(samples.values())

    print(f"Source:    {src_path}")
    print(f"Lines in:  {len(lines):>7d}")
    print(f"Patterns:  {len(sampled):>7d}")
    print(f"Reduction: {len(lines)/max(1,len(sampled)):.1f}x")

    with open(dst_path, 'w', encoding='utf-8') as f:
        for goal in sampled:
            f.write(goal + '\n')
    print(f"Wrote:     {dst_path}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
