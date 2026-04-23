"""Test the hypothesis that `2` = 'a' by looking at its context across
all VMS occurrences. If 2 = 'a', then standalone `2` followed by another
token X means the bigram <a, X's-letter> in the underlying text.

Also check position preferences (paragraph-initial? line-initial? etc.),
and expand to the full `2,...` token family since 2 is also a frequent
prefix.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from voynpy.corpora import vms, vms1, vms2


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


def lines_of(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        tokens = [row[c] for c in cols]
        tokens = [t for t in tokens if isinstance(t, str) and t != "$"]
        yield row["folio"], row.get("par"), row.get("line"), tokens


# ---- Frequency and positions of standalone `2`
before = Counter()
after = Counter()
para_init = 0
para_term = 0
line_init = 0
line_term = 0
total_2 = 0

# paragraph-level context
for folio, par, flat in paragraphs(vms):
    n = len(flat)
    for i, t in enumerate(flat):
        if t != "2":
            continue
        total_2 += 1
        b = flat[i - 1] if i > 0 else "<START>"
        a = flat[i + 1] if i + 1 < n else "<END>"
        before[b] += 1
        after[a] += 1
        if i == 0:
            para_init += 1
        if i == n - 1:
            para_term += 1

# line-level position
for folio, par, line, toks in lines_of(vms):
    for i, t in enumerate(toks):
        if t != "2":
            continue
        if i == 0:
            line_init += 1
        if i == len(toks) - 1:
            line_term += 1

print(f"Standalone `2` occurrences (paragraph-level iteration): {total_2}")
print(f"  paragraph-initial: {para_init}  ({100*para_init/total_2:.1f}%)")
print(f"  paragraph-terminal: {para_term}  ({100*para_term/total_2:.1f}%)")
print(f"  line-initial: {line_init}  ({100*line_init/total_2:.1f}%)")
print(f"  line-terminal: {line_term}  ({100*line_term/total_2:.1f}%)")

print("\n--- Top 15 tokens immediately AFTER standalone `2` ---")
tot = sum(after.values())
for tok, n in after.most_common(15):
    print(f"  {tok!r:>22}  {n:4d}  ({100*n/tot:5.1f}%)")

print("\n--- Top 15 tokens immediately BEFORE standalone `2` ---")
tot = sum(before.values())
for tok, n in before.most_common(15):
    print(f"  {tok!r:>22}  {n:4d}  ({100*n/tot:5.1f}%)")

# ---- First-half / second-half split
n_vms1 = sum(1 for _, _, flat in paragraphs(vms1) for t in flat if t == "2")
n_vms2 = sum(1 for _, _, flat in paragraphs(vms2) for t in flat if t == "2")
tot1 = sum(len(flat) for _, _, flat in paragraphs(vms1))
tot2 = sum(len(flat) for _, _, flat in paragraphs(vms2))
print(f"\n--- Frequency split ---")
print(f"  vms1: {n_vms1}/{tot1:,} = {100*n_vms1/tot1:.2f}%")
print(f"  vms2: {n_vms2}/{tot2:,} = {100*n_vms2/tot2:.2f}%")
print(f"  cliff: {(n_vms1/tot1)/(n_vms2/tot2):.2f}x")
