"""What is `8` in the VMS?

Investigate: does the single glyph `8` stand alone as a VMS token? What
tokens start with `8,`? How often does `8` act as a prefix on other tokens?
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


# ---- 1. Standalone `8` count
for name, rt in [("vms (full)", vms), ("vms1", vms1), ("vms2", vms2)]:
    c_total = 0
    c_8 = 0
    for t in tokens_of(rt):
        c_total += 1
        if t == "8":
            c_8 += 1
    print(f"{name:>12}: `8` as standalone token: {c_8}/{c_total:,} ({100*c_8/c_total:.3f}%)")


# ---- 2. Most common tokens starting with `8,`
print("\n=== Top 20 VMS tokens starting with `8,` ===")
cnt = Counter()
for t in tokens_of(vms):
    if t == "8" or t.startswith("8,"):
        cnt[t] += 1
for t, n in cnt.most_common(20):
    print(f"  {t!r:>16}: {n:5d}")
print(f"  ... total distinct tokens starting with `8`: {len(cnt)}")
print(f"  ... total occurrences: {sum(cnt.values())}")


# ---- 3. `8` as prefix: what bases does it attach to?
print("\n=== `8` as prefix (removing leading `8,` to see the base) ===")
base_cnt = Counter()
for t in tokens_of(vms):
    if t.startswith("8,"):
        base = t[2:]
        base_cnt[base] += 1
print("  top 20 base tokens that get `8,` prefix:")
for base, n in base_cnt.most_common(20):
    # is the bare base also a common standalone token?
    bare_count = sum(1 for tok in tokens_of(vms) if tok == base)
    # expensive; let's avoid re-iterating. Compute bare counts once.
    break  # fall through

# actually build bare counts once
bare_cnt = Counter()
for t in tokens_of(vms):
    bare_cnt[t] += 1

print(f"  {'base':>24} | {'prefixed 8,X':>13}  {'bare X':>8}  {'ratio':>6}")
for base, n in base_cnt.most_common(20):
    bare = bare_cnt.get(base, 0)
    r = f"{n/bare:.2f}x" if bare else "—"
    print(f"  {base!r:>24} | {n:>13}  {bare:>8}  {r:>6}")


# ---- 4. Bases where `8,X` is MORE common than bare `X`
print("\n=== Bases where `8,X` appears MORE often than bare `X` (min count 5) ===")
flips = []
for base, n_prefixed in base_cnt.items():
    bare = bare_cnt.get(base, 0)
    if n_prefixed >= 5 and n_prefixed > bare:
        flips.append((base, n_prefixed, bare))
flips.sort(key=lambda x: -x[1])
for base, n_p, n_b in flips[:15]:
    print(f"  {base!r:>24} | prefixed {n_p:4d} > bare {n_b:4d}")
