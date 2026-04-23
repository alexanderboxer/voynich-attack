"""Line-terminal rate calibration.

Compute:
1. Baseline line-terminal rate across the full VMS (what fraction of all
   token occurrences are the last on their line).
2. Line-terminal rate for c,M,c,9 (and a handful of comparable high-frequency
   tokens for context), with an approximate significance check.
"""

from __future__ import annotations

import math
from collections import Counter

from voynpy.corpora import vms


def _token_cols(df):
    return [c for c in df.columns if c.startswith("t") and c[1:].isdigit()]


def scan(rt):
    """Return (total_tokens, per_token_counts, per_token_line_terminal_counts)."""
    df = rt.df
    cols = _token_cols(df)
    total = 0
    cnt = Counter()
    last = Counter()
    for _, row in df.iterrows():
        tokens = [row[c] for c in cols]
        tokens = [t for t in tokens if isinstance(t, str) and t != "$"]
        if not tokens:
            continue
        for t in tokens:
            cnt[t] += 1
            total += 1
        last[tokens[-1]] += 1
    return total, cnt, last


def binomial_pvalue(k, n, p):
    """Two-sided-ish: prob of seeing k or more hits in n trials if rate is p.
    Normal approximation (n*p > 5 etc.).
    """
    mu = n * p
    sd = math.sqrt(n * p * (1 - p))
    if sd == 0:
        return 1.0
    z = (k - mu) / sd
    return z


total, cnt, last = scan(vms)
n_lines = sum(last.values())
baseline = n_lines / total

print(f"VMS totals: {total:,} tokens across {n_lines:,} lines")
print(f"Baseline line-terminal rate: {100*baseline:.2f}% "
      f"(avg tokens per line = {total/n_lines:.2f})")
print()

targets = [
    "c,M,c,9", "cc,o,Z", "cc,o,x", "8,a,m", "4,o,x", "o,M,cc,9",
    "c^c,o,x", "o,M,8,a,m", "cc,9", "8,9",
]
print(f"{'token':>14} | {'n':>6} {'line-term':>10} {'rate':>6} {'ratio':>7} {'z':>6}")
print("-" * 60)
for t in targets:
    n = cnt.get(t, 0)
    lt = last.get(t, 0)
    rate = lt / n if n else 0
    ratio = rate / baseline if baseline else float('inf')
    z = binomial_pvalue(lt, n, baseline) if n else 0
    print(f"{t:>14} | {n:>6} {lt:>10} {100*rate:>5.1f}% {ratio:>6.2f}x {z:>6.1f}")
