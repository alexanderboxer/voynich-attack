"""Re-analyze M/N equivalence with c,M,c and c,N,c treated as atomic
(cc-straddling-M and cc-straddling-N respectively).

The user's hypothesis: [cc,M] + [c] ≡ [cc,N] — adding a bare c after
cc,M is equivalent to using cc,N directly.

Testing:
1. Direct [cc,M] ↔ [cc,N] substitution: find tokens T where replacing
   the atomic c,M,c with c,N,c yields another attested token.
2. The "extra c absorbed" rule: find tokens T where replacing
   'c,M,c,c' (atomic [cc,M] followed by bare [c]) with 'c,N,c'
   (atomic [cc,N]) yields another attested token.

Only compare pairs where c,M,c and c,N,c are used correctly atomically
(must appear as full 3-glyph substrings, not split across other glyphs).
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


def substitute_seq(glyphs, source, replacement):
    m = len(source)
    for i in range(len(glyphs) - m + 1):
        if glyphs[i:i + m] == source:
            return glyphs[:i] + replacement + glyphs[i + m:], i
    return None


# ---- Test 1: direct [cc,M] ↔ [cc,N] substitution
# tokens containing c,M,c as a 3-glyph substring
pairs_direct = []
for tok in cnt:
    glyphs = tok.split(",")
    sub = substitute_seq(glyphs, ["c", "M", "c"], ["c", "N", "c"])
    if sub is None:
        continue
    new_glyphs, pos = sub
    new_tok = ",".join(new_glyphs)
    if new_tok in cnt:
        pairs_direct.append((tok, new_tok, pos, cnt[tok], cnt[new_tok]))

pairs_direct.sort(key=lambda x: -(x[3] + x[4]))

print("=" * 80)
print("Test 1: Direct [cc,M] ↔ [cc,N] substitution (same structural position)")
print("=" * 80)
print(f"{'T with cc,M':>24} | {'T with cc,N':>22} | count(M) | count(N) | ratio")
print("-" * 80)
for x, y, pos, nx, ny in pairs_direct[:25]:
    ratio = f"{nx/ny:.2f}" if ny else "—"
    print(f"{x!r:>24} | {y!r:>22} | {nx:>8} | {ny:>8} | {ratio}")
print(f"\nTotal pairs (direct cc,M ↔ cc,N): {len(pairs_direct)}")


# ---- Test 2: [cc,M][c] → [cc,N]  — the "extra c absorbed" rule
pairs_absorbed = []
for tok in cnt:
    glyphs = tok.split(",")
    sub = substitute_seq(glyphs, ["c", "M", "c", "c"], ["c", "N", "c"])
    if sub is None:
        continue
    new_glyphs, pos = sub
    new_tok = ",".join(new_glyphs)
    if new_tok in cnt:
        pairs_absorbed.append((tok, new_tok, pos, cnt[tok], cnt[new_tok]))

pairs_absorbed.sort(key=lambda x: -(x[3] + x[4]))

print("\n" + "=" * 80)
print("Test 2: [cc,M][c] ↔ [cc,N]  — 'extra c absorbed' rule")
print("         (c,M,c,c  →  c,N,c)")
print("=" * 80)
print(f"{'T with cc,M,c':>26} | {'T with cc,N':>22} | nX | nY | ratio")
print("-" * 80)
for x, y, pos, nx, ny in pairs_absorbed[:25]:
    ratio = f"{nx/ny:.2f}" if ny else "—"
    print(f"{x!r:>26} | {y!r:>22} | {nx:>2} | {ny:>2} | {ratio}")
print(f"\nTotal pairs (cc,M+c ↔ cc,N): {len(pairs_absorbed)}")
