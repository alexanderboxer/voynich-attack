"""Test the hypothesis: c^c,c ≡ cc (the 2-glyph `c^c,c` sequence is a
variant of the 1-glyph `cc`).

Three tests:
1. Pairwise: for every token T containing `c^c,c` as a contiguous sub-
   sequence, compute T' = T with cc substituted. Check if T' is also an
   attested VMS token. Compare their frequencies and vms1/vms2 splits.
2. Adjacency violation: does T ever appear immediately next to T'? If
   they encode the same letter, adjacency would be a "doubling" and
   should be checked against the forbidden-triple framework.
3. Constraint check: does substituting c^c,c → cc anywhere in the VMS
   produce a quadruple (which is never observed and would be forbidden)?
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


cnt_full = Counter(tokens_of(vms))
cnt_1 = Counter(tokens_of(vms1))
cnt_2 = Counter(tokens_of(vms2))
tot_1 = sum(cnt_1.values())
tot_2 = sum(cnt_2.values())

TARGET_A = ["c^c", "c"]   # the 2-glyph sequence
TARGET_B = ["cc"]          # the 1-glyph sequence


def substitute_subsequence(glyphs, source, replacement):
    """Return a new glyph list with the first occurrence of source
    (contiguous subsequence) replaced by replacement. Returns None if
    source not found."""
    m = len(source)
    for i in range(len(glyphs) - m + 1):
        if glyphs[i:i + m] == source:
            return glyphs[:i] + replacement + glyphs[i + m:], i
    return None


# Enumerate all tokens containing the target subsequence.
pairs = []  # (t_with_c^c_c, t_with_cc, substitution_index)
for tok in cnt_full:
    glyphs = tok.split(",")
    swap = substitute_subsequence(glyphs, TARGET_A, TARGET_B)
    if swap is None:
        continue
    swapped_glyphs, pos = swap
    swapped_tok = ",".join(swapped_glyphs)
    pairs.append((tok, swapped_tok, pos))

# Now test: does the swapped token exist in VMS?
both_attested = [(a, b, pos, cnt_full[a], cnt_full.get(b, 0))
                 for a, b, pos in pairs if cnt_full.get(b, 0) > 0]
only_a_attested = [(a, b, pos, cnt_full[a]) for a, b, pos in pairs if cnt_full.get(b, 0) == 0]

print("=" * 80)
print("TEST 1: tokens with c^c,c whose swapped cc-form is ALSO attested")
print("=" * 80)
print(f"{'c^c,c-form':>28} | {'cc-form':>22} | count A | count B | pos")
print("-" * 80)
both_attested.sort(key=lambda x: -x[3])
for a, b, pos, na, nb in both_attested[:25]:
    print(f"{a!r:>28} | {b!r:>22} | {na:7} | {nb:7} | {pos}")
print(f"\nPairs both attested: {len(both_attested)}")
print(f"Tokens with c^c,c where cc-form is NOT attested: {len(only_a_attested)}")
print("  top 15 such tokens:")
only_a_attested.sort(key=lambda x: -x[3])
for a, b, pos, na in only_a_attested[:15]:
    print(f"    {a!r:>28}  count {na}  (swap would give {b!r})")

# ---- TEST 2: do any c^c,c-form and cc-form appear ADJACENT in any paragraph?
print()
print("=" * 80)
print("TEST 2: adjacency check — does T (c^c,c) ever appear next to T' (cc)?")
print("=" * 80)
pair_set = {(a, b): 0 for a, b, *_ in both_attested}
pair_set.update({(b, a): 0 for a, b, *_ in both_attested})
adjacency_hits = []
for folio, par, flat in paragraphs(vms):
    for i in range(len(flat) - 1):
        if (flat[i], flat[i + 1]) in pair_set:
            adjacency_hits.append((folio, par, i, flat[i], flat[i + 1]))
print(f"Adjacent-pair hits: {len(adjacency_hits)}")
for hit in adjacency_hits[:10]:
    print(f"  {hit[0]}.{hit[1]} @ {hit[2]}: {hit[3]!r}  {hit[4]!r}")

# ---- TEST 3: constraint — substituting globally, do we produce quadruples?
# After substitution, two adjacent tokens that become identical would be
# a new double. Three adjacent same tokens (originally triples that become
# different under substitution but actually were same) would be a
# quadruple if any existing double is adjacent to the new one.
print()
print("=" * 80)
print("TEST 3: forbidden-sequence check after global c^c,c → cc substitution")
print("=" * 80)


def apply_substitution(tok):
    glyphs = tok.split(",")
    while True:
        swap = substitute_subsequence(glyphs, TARGET_A, TARGET_B)
        if swap is None:
            break
        glyphs = swap[0]
    return ",".join(glyphs)


# For each paragraph, substitute and check for forbidden quadruples
new_quadruples = 0
new_triples = Counter()
example_quads = []
for folio, par, flat in paragraphs(vms):
    flat_new = [apply_substitution(t) for t in flat]
    i = 0
    while i < len(flat_new) - 2:
        if flat_new[i] == flat_new[i + 1] == flat_new[i + 2]:
            run = 3
            while i + run < len(flat_new) and flat_new[i + run] == flat_new[i]:
                run += 1
            new_triples[flat_new[i]] += 1
            if run >= 4:
                new_quadruples += 1
                example_quads.append((folio, par, i, flat_new[i], run))
            i += run
        else:
            i += 1
print(f"Triples after substitution: {sum(new_triples.values())}")
print(f"Quadruples (forbidden!) after substitution: {new_quadruples}")
for ex in example_quads[:10]:
    print(f"  {ex[0]}.{ex[1]} @ {ex[2]}: {ex[3]!r} x{ex[4]}")

print("\nTop triples after substitution (compared to pre-substitution):")
for tok, n in new_triples.most_common(10):
    print(f"  {tok!r:>28}: {n}")
