"""Compare the standalone-neighbor distributions of cc,o,x and cc,o,Z.

If both encode the same letter, the tokens that appear adjacent to each
(paragraph-level, across line boundaries) should come from a similar
distribution. Measure:
- Top preceding tokens for each base.
- Top following tokens for each base.
- Rank correlation of shared neighbors.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import math

from voynpy.corpora import vms


def _token_cols(df):
    return [c for c in df.columns if c.startswith("t") and c[1:].isdigit()]


def paragraphs(rt):
    df = rt.df
    cols = _token_cols(df)
    groups: dict = defaultdict(list)
    order: list = []
    for _, row in df.iterrows():
        tokens = [row[c] for c in cols]
        tokens = [t for t in tokens if isinstance(t, str) and t != "$"]
        key = (row["folio"], row.get("par"))
        if key not in groups:
            order.append(key)
        groups[key].append((int(row.get("line")), tokens))
    for key in order:
        flat = [t for _, toks in sorted(groups[key], key=lambda x: x[0]) for t in toks]
        yield key[0], key[1], flat


def neighbors(target):
    before = Counter()
    after = Counter()
    for _, _, flat in paragraphs(vms):
        for i, t in enumerate(flat):
            if t != target:
                continue
            before[flat[i - 1] if i > 0 else "<START>"] += 1
            after[flat[i + 1] if i + 1 < len(flat) else "<END>"] += 1
    return before, after


before_x, after_x = neighbors("cc,o,x")
before_Z, after_Z = neighbors("cc,o,Z")


def side_by_side(label, dist_x, dist_Z):
    total_x = sum(dist_x.values())
    total_Z = sum(dist_Z.values())
    all_keys = set(dist_x) | set(dist_Z)
    rows = []
    for k in all_keys:
        nx = dist_x.get(k, 0)
        nZ = dist_Z.get(k, 0)
        sx = 100 * nx / total_x if total_x else 0
        sZ = 100 * nZ / total_Z if total_Z else 0
        rows.append((k, nx, sx, nZ, sZ))
    rows.sort(key=lambda r: -(r[1] + r[3]))
    print(f"\n{label} — top neighbors:")
    print(f"  {'neighbor':>22} | {'cc,o,x':>7} {'%':>5} | {'cc,o,Z':>7} {'%':>5} | diff(pp)")
    print("  " + "-" * 76)
    for k, nx, sx, nZ, sZ in rows[:20]:
        print(f"  {k!r:>22} | {nx:>7} {sx:>4.1f}% | {nZ:>7} {sZ:>4.1f}% | {sx-sZ:+5.1f}")


side_by_side("PRECEDING tokens", before_x, before_Z)
side_by_side("FOLLOWING tokens", after_x, after_Z)


def rank_correlation(a, b):
    """Spearman-ish over common keys."""
    # ranks, excluding low-count tokens for stability (those that appear <2 times on either side)
    a_sorted = sorted(a.items(), key=lambda kv: -kv[1])
    b_sorted = sorted(b.items(), key=lambda kv: -kv[1])
    a_ranks = {k: i + 1 for i, (k, v) in enumerate(a_sorted) if v >= 2}
    b_ranks = {k: i + 1 for i, (k, v) in enumerate(b_sorted) if v >= 2}
    common = set(a_ranks) & set(b_ranks)
    if len(common) < 3:
        return float('nan'), 0
    n = len(common)
    a_rs = [a_ranks[k] for k in common]
    b_rs = [b_ranks[k] for k in common]
    a_mean = sum(a_rs) / n
    b_mean = sum(b_rs) / n
    num = sum((a_rs[i] - a_mean) * (b_rs[i] - b_mean) for i in range(n))
    den = math.sqrt(sum((v - a_mean) ** 2 for v in a_rs) * sum((v - b_mean) ** 2 for v in b_rs))
    return (num / den if den > 0 else float('nan')), n


r_before, n_before = rank_correlation(before_x, before_Z)
r_after, n_after = rank_correlation(after_x, after_Z)

print(f"\n{'='*50}")
print(f"Rank correlation (count>=2) of PRECEDING neighbors: r={r_before:.3f}  (n={n_before} shared)")
print(f"Rank correlation (count>=2) of FOLLOWING neighbors: r={r_after:.3f}  (n={n_after} shared)")
print(f"{'='*50}")

# Also: how many unique neighbors does each have?
print(f"\nUnique preceding tokens: cc,o,x has {len(before_x)}, cc,o,Z has {len(before_Z)}, shared {len(set(before_x)&set(before_Z))}")
print(f"Unique following tokens: cc,o,x has {len(after_x)}, cc,o,Z has {len(after_Z)}, shared {len(set(after_x)&set(after_Z))}")
