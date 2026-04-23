"""Compare the prefix distributions on cc,o,x vs cc,o,Z.

If both encode 'i' (same letter), their prefix distributions should be
similar in both rank-order and share. If they encode different letters,
the distributions may diverge.

For each prefix, compute:
- count on cc,o,x containers
- count on cc,o,Z containers
- share of total containers for each side
- rank on each side
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


def prefix_dist_for_base(base: str):
    """Return Counter of prefix -> count for VMS tokens ending in `,base`
    or equal to base. <NONE> = bare."""
    base_glyphs = base.split(",")
    m = len(base_glyphs)
    pc = Counter()
    for tok, n in cnt.items():
        glyphs = tok.split(",")
        if glyphs == base_glyphs:
            pc["<NONE>"] += n
        elif len(glyphs) > m and glyphs[-m:] == base_glyphs:
            pc[",".join(glyphs[:-m])] += n
    return pc


pc_x = prefix_dist_for_base("cc,o,x")
pc_Z = prefix_dist_for_base("cc,o,Z")
tot_x = sum(pc_x.values())
tot_Z = sum(pc_Z.values())

print(f"{'prefix':>18} | {'on cc,o,x':>10} {'share':>6} | {'on cc,o,Z':>10} {'share':>6} | diff (pp)")
print("-" * 90)
all_prefixes = set(pc_x) | set(pc_Z)
rows = []
for p in all_prefixes:
    nx = pc_x.get(p, 0)
    nZ = pc_Z.get(p, 0)
    sx = 100 * nx / tot_x if tot_x else 0
    sZ = 100 * nZ / tot_Z if tot_Z else 0
    rows.append((p, nx, sx, nZ, sZ, sx - sZ))
# sort by combined count
rows.sort(key=lambda r: -(r[1] + r[3]))
for p, nx, sx, nZ, sZ, diff in rows[:25]:
    label = p if p else "<bare>"
    print(f"{label!r:>18} | {nx:>10} {sx:>5.1f}% | {nZ:>10} {sZ:>5.1f}% | {diff:+5.1f}")

# Summary metrics
# 1. Spearman-ish rank correlation over common prefixes
import math

def rank_correlation(a_ranks, b_ranks):
    # a_ranks, b_ranks are dicts prefix -> rank (1 = most common)
    keys = set(a_ranks) & set(b_ranks)
    if len(keys) < 3:
        return float('nan'), 0
    n = len(keys)
    a_rs = [a_ranks[k] for k in keys]
    b_rs = [b_ranks[k] for k in keys]
    a_mean = sum(a_rs) / n
    b_mean = sum(b_rs) / n
    num = sum((a_rs[i] - a_mean) * (b_rs[i] - b_mean) for i in range(n))
    den = math.sqrt(sum((v - a_mean) ** 2 for v in a_rs) * sum((v - b_mean) ** 2 for v in b_rs))
    return (num / den if den > 0 else float('nan')), n

# rank prefixes on each side (excluding <NONE>)
ranks_x = {}
for i, (p, n) in enumerate(sorted(pc_x.items(), key=lambda kv: -kv[1]), start=1):
    if p == "<NONE>":
        continue
    ranks_x[p] = i
ranks_Z = {}
for i, (p, n) in enumerate(sorted(pc_Z.items(), key=lambda kv: -kv[1]), start=1):
    if p == "<NONE>":
        continue
    ranks_Z[p] = i

r, n = rank_correlation(ranks_x, ranks_Z)
print(f"\nPrefix-rank correlation (over {n} shared non-empty prefixes): {r:.3f}")

# 2. Shared vs unique prefixes
shared = set(pc_x) & set(pc_Z) - {"<NONE>"}
only_x = set(pc_x) - set(pc_Z) - {"<NONE>"}
only_Z = set(pc_Z) - set(pc_x) - {"<NONE>"}
print(f"\nPrefixes appearing on BOTH bases: {len(shared)}")
print(f"Prefixes appearing ONLY on cc,o,x: {len(only_x)}")
print(f"Prefixes appearing ONLY on cc,o,Z: {len(only_Z)}")
print(f"\nTop prefixes only on cc,o,x:")
for p in sorted(only_x, key=lambda k: -pc_x[k])[:8]:
    print(f"  {p!r:>18}  {pc_x[p]}")
print(f"\nTop prefixes only on cc,o,Z:")
for p in sorted(only_Z, key=lambda k: -pc_Z[k])[:8]:
    print(f"  {p!r:>18}  {pc_Z[p]}")
