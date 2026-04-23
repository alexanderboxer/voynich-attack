"""Find VMS paragraphs ending in cc,o,x cc,o,x 8,a,m (= YYZ / 'iis' under
the Latin i-s hypothesis). Report the token immediately BEFORE the YYZ,
which under the hypothesis encodes the last letter of the stem (the
consonant or vowel preceding -iis in a Latin word like al-iis, var-iis,
fol-iis, med-iis).

Also scan for the "relaxed" version — any terminal `YYZ` pattern where
the last three tokens obey Y=Y≠Z — and tabulate all such YZ pairs so we
can see which terminal-double tokens appear across the manuscript.
"""

from __future__ import annotations

from collections import Counter, defaultdict

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


TARGET_Y = "cc,o,x"
TARGET_Z = "8,a,m"

# ---- Part 1: exact YYZ endings cc,o,x cc,o,x 8,a,m
exact_matches = []
# ---- Part 2: all terminal YYZ patterns (any Y, any Z, with Y=Y≠Z)
terminal_yyz = Counter()
yyz_contexts = defaultdict(list)   # (Y, Z) -> list of (folio, par, tok_before, tail)

for folio, par, flat in paragraphs(vms):
    if len(flat) < 3:
        continue
    a, b, c = flat[-3], flat[-2], flat[-1]
    if a == b and b != c:
        terminal_yyz[(a, c)] += 1
        tok_before = flat[-4] if len(flat) >= 4 else "<START>"
        yyz_contexts[(a, c)].append((folio, par, tok_before, flat[-6:] if len(flat) >= 6 else flat))
        if a == TARGET_Y and c == TARGET_Z:
            exact_matches.append((folio, par, flat))

# Part 1 output
print("=" * 72)
print(f"Paragraphs ending with {TARGET_Y!r} {TARGET_Y!r} {TARGET_Z!r}  (the 'iis' pattern)")
print("=" * 72)
print(f"Matches found: {len(exact_matches)}")
for folio, par, flat in exact_matches:
    tail = flat[-6:] if len(flat) >= 6 else flat
    tok_before = flat[-4] if len(flat) >= 4 else "<START>"
    print(f"\n  --- {folio}.{par} ---   token-before-YYZ: {tok_before!r}")
    print(f"      tail: {'  '.join(tail)}")

# Tally the tokens appearing immediately before the exact YYZ match
before_cnt = Counter()
for folio, par, flat in exact_matches:
    tok_before = flat[-4] if len(flat) >= 4 else "<START>"
    before_cnt[tok_before] += 1
if before_cnt:
    print(f"\n  token-before-YYZ tally:")
    for tok, n in before_cnt.most_common():
        print(f"     {tok!r:>24}  {n}")

# Part 2 output
print()
print("=" * 72)
print("All paragraph-terminal YYZ patterns (Y, Y, Z) in VMS")
print("=" * 72)
print(f"{'Y (doubled)':>28} | {'Z (final)':>14} | count")
print("-" * 62)
for (y, z), n in terminal_yyz.most_common():
    print(f"{y!r:>28} | {z!r:>14} | {n}")
