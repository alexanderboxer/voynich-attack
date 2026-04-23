"""Test hypothesis: c,M,c,c,9 = c,N,c,9 = 't'.

The implicit algebra: the pair 'M,c' is equivalent to 'N' alone. Test by:
1. Comparing the distributions of c,M,c,c,9 and c,N,c,9.
2. Looking for other token pairs that differ by the same 'M,c ↔ N' swap.
3. If they encode the same letter, they should have similar frequency,
   similar half-of-manuscript cliff, similar neighbor patterns.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from voynpy.corpora import vms, vms1, vms2


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


cnt = Counter(tokens_of(vms))
cnt1 = Counter(tokens_of(vms1))
cnt2 = Counter(tokens_of(vms2))
tot1 = sum(cnt1.values())
tot2 = sum(cnt2.values())


# ---- Part 1: direct comparison of the two target tokens
for tok in ["c,M,c,c,9", "c,N,c,9"]:
    n = cnt.get(tok, 0)
    n1 = cnt1.get(tok, 0)
    n2 = cnt2.get(tok, 0)
    p1 = 100 * n1 / tot1 if tot1 else 0
    p2 = 100 * n2 / tot2 if tot2 else 0
    cliff = f"{p1/p2:.1f}x" if p2 > 0 else "—"
    print(f"{tok!r:>16}: total={n:4d}  vms1={n1:4d} ({p1:.3f}%)  vms2={n2:4d} ({p2:.3f}%)  cliff={cliff}")


# ---- Part 2: find all token pairs (X_with_Mc, X_with_N) where replacing
# 'M,c' in X_with_Mc gives X_with_N, and BOTH are attested VMS tokens.
def substitute_first(glyphs, source, replacement):
    m = len(source)
    for i in range(len(glyphs) - m + 1):
        if glyphs[i:i + m] == source:
            return glyphs[:i] + replacement + glyphs[i + m:], i
    return None


pairs = []
for tok in cnt:
    glyphs = tok.split(",")
    # substitute ['M','c'] -> ['N']
    sub = substitute_first(glyphs, ["M", "c"], ["N"])
    if sub is None:
        continue
    new_glyphs, pos = sub
    new_tok = ",".join(new_glyphs)
    if new_tok in cnt:
        pairs.append((tok, new_tok, pos, cnt[tok], cnt[new_tok]))

pairs.sort(key=lambda x: -(x[3] + x[4]))
print(f"\n{'='*80}")
print("Tokens X where 'M,c' in X can be replaced by 'N' to give another attested token")
print(f"{'='*80}")
print(f"{'X (has M,c)':>26} | {'Y (has N)':>20} | pos | {'nX':>5} {'nY':>5}")
print("-" * 80)
for x, y, pos, nx, ny in pairs[:25]:
    print(f"{x!r:>26} | {y!r:>20} | {pos:3d} | {nx:>5} {ny:>5}")
print(f"\nTotal such pairs: {len(pairs)}")


# ---- Part 3: also check the reverse substitution 'N' -> 'M,c'
# and reciprocal pairs (i.e., swap in either direction yields an attested token)
pairs2 = []
for tok in cnt:
    glyphs = tok.split(",")
    sub = substitute_first(glyphs, ["N"], ["M", "c"])
    if sub is None:
        continue
    new_glyphs, pos = sub
    new_tok = ",".join(new_glyphs)
    if new_tok in cnt and (tok, new_tok, pos) not in {(y, x, p) for x, y, p, _, _ in pairs}:
        pairs2.append((tok, new_tok, pos, cnt[tok], cnt[new_tok]))
pairs2.sort(key=lambda x: -(x[3] + x[4]))


# ---- Part 4: neighbor comparison
def neighbor_counts(target):
    before = Counter()
    after = Counter()
    for _, _, flat in paragraphs(vms):
        for i, t in enumerate(flat):
            if t != target:
                continue
            before[flat[i - 1] if i > 0 else "<START>"] += 1
            after[flat[i + 1] if i + 1 < len(flat) else "<END>"] += 1
    return before, after


bef_M, aft_M = neighbor_counts("c,M,c,c,9")
bef_N, aft_N = neighbor_counts("c,N,c,9")

print(f"\n{'='*80}")
print("Neighbor comparison: c,M,c,c,9 vs c,N,c,9")
print(f"{'='*80}")
print("PRECEDING tokens:")
all_b = set(bef_M) | set(bef_N)
rows = sorted(all_b, key=lambda k: -(bef_M.get(k, 0) + bef_N.get(k, 0)))
print(f"{'neighbor':>22} | {'c,M,c,c,9':>10} | {'c,N,c,9':>10}")
for k in rows[:10]:
    print(f"{k!r:>22} | {bef_M.get(k, 0):>10} | {bef_N.get(k, 0):>10}")
print("\nFOLLOWING tokens:")
all_a = set(aft_M) | set(aft_N)
rows = sorted(all_a, key=lambda k: -(aft_M.get(k, 0) + aft_N.get(k, 0)))
print(f"{'neighbor':>22} | {'c,M,c,c,9':>10} | {'c,N,c,9':>10}")
for k in rows[:10]:
    print(f"{k!r:>22} | {aft_M.get(k, 0):>10} | {aft_N.get(k, 0):>10}")
