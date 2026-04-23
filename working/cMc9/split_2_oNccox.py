"""Does `2,o,N,cc,o,x` parse better as a single token, or as `2` + `o,N,cc,o,x`?

Measure:
1. How often `2` appears as a standalone VMS token.
2. How often `o,N,cc,o,x` appears as a standalone token.
3. How often `2,o,N,cc,o,x` appears (as the joined form).
4. How often `2` is a PREFIX on other tokens generally.
5. Variant forms: 2,o,... and how 2 behaves structurally.
"""

from __future__ import annotations

from collections import Counter

from voynpy.corpora import vms


def _token_cols(df):
    return [c for c in df.columns if c.startswith("t") and c[1:].isdigit()]


def tokens_of(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        for c in cols:
            t = row[c]
            if isinstance(t, str) and t != "$":
                yield t


cnt = Counter(tokens_of(vms))

targets = [
    "2",
    "o,N,cc,o,x",
    "2,o,N,cc,o,x",
    # closely related forms worth seeing
    "o,N,c,o,x",
    "2,o,N,c,o,x",
    "2,o,N,cc,9",
    "2,o,x",
    "2,o,Z",
]
print(f"{'token':>20} | standalone count")
print("-" * 45)
for t in targets:
    print(f"{t!r:>20} | {cnt.get(t, 0):>5}")

# How often does `2` appear as a PREFIX at all?
tokens_with_2_prefix = [t for t in cnt if t.startswith("2,")]
total_with_2 = sum(cnt[t] for t in tokens_with_2_prefix)
print(f"\nDistinct tokens starting with '2,': {len(tokens_with_2_prefix)}")
print(f"Total occurrences of `2,X` tokens: {total_with_2}")

print("\nTop 12 `2,X` tokens:")
for t in sorted(tokens_with_2_prefix, key=lambda x: -cnt[x])[:12]:
    print(f"  {t!r:>20}  {cnt[t]}")

# And how often is `o,N,cc,o,x` a prefix itself (with or without something after)?
print(f"\nTokens starting with 'o,N,cc,o,x':")
for t in sorted(cnt):
    if t.startswith("o,N,cc,o,x"):
        print(f"  {t!r:>24}  {cnt[t]}")

# How often is `2` a standalone token followed by `o,N,cc,o,x` as the NEXT token?
# Need to walk the token stream in order.
def ordered_tokens(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        for c in cols:
            t = row[c]
            if isinstance(t, str) and t != "$":
                yield t

seq_2_oNccox = 0
prev = None
for t in ordered_tokens(vms):
    if prev == "2" and t == "o,N,cc,o,x":
        seq_2_oNccox += 1
    prev = t
print(f"\nAdjacent pairs `2` then `o,N,cc,o,x` across VMS: {seq_2_oNccox}")

# Pairs of `2` then anything
pair_cnt = Counter()
prev = None
for t in ordered_tokens(vms):
    if prev == "2":
        pair_cnt[t] += 1
    prev = t
print(f"\nTop 10 tokens that follow standalone `2`:")
for t, n in pair_cnt.most_common(10):
    print(f"  {t!r:>22}  {n}")
