"""Find all VMS tokens that triple (same token 3+ times adjacent) and
focus on the cc,o,x-family.

Under the hypothesis that tripling = 'iii' (Roman numeral or consecutive
'i's), any token that triples is a candidate for 'i'.
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


# ---- Part 1: all triples (tokens appearing 3+ times adjacent)
triples = Counter()   # token -> number of run-of-3 occurrences
quadruples = Counter()
triple_locations = defaultdict(list)

for folio, par, flat in paragraphs(vms):
    i = 0
    while i < len(flat) - 2:
        if flat[i] == flat[i + 1] == flat[i + 2]:
            run_len = 3
            while i + run_len < len(flat) and flat[i + run_len] == flat[i]:
                run_len += 1
            triples[flat[i]] += 1
            triple_locations[flat[i]].append((folio, par, i, run_len))
            if run_len >= 4:
                quadruples[flat[i]] += 1
            i += run_len
        else:
            i += 1

print("=" * 72)
print("All tokens that triple (appear 3+ times adjacent) anywhere in VMS")
print("=" * 72)
for tok, n in sorted(triples.items(), key=lambda x: -x[1]):
    q = quadruples.get(tok, 0)
    locs = triple_locations[tok]
    print(f"\n  {tok!r:>28}  triples: {n}  quadruples+: {q}")
    for folio, par, idx, rl in locs:
        print(f"    - {folio}.{par} @ token idx {idx}  (run length {rl})")

# ---- Part 2: contextualize cc,o,x-family
print("\n" + "=" * 72)
print("cc,o,x-family tokens: frequency, vms1/vms2 split, context")
print("=" * 72)

def _tokens_of(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        for c in cols:
            t = row[c]
            if isinstance(t, str) and t != "$":
                yield t


from voynpy.corpora import vms1, vms2

cnt_full = Counter(_tokens_of(vms))
cnt_1 = Counter(_tokens_of(vms1))
cnt_2 = Counter(_tokens_of(vms2))
tot_1 = sum(cnt_1.values())
tot_2 = sum(cnt_2.values())

# Find all tokens ending in ",cc,o,x" or equal to "cc,o,x"
# (and also c^c,c,o,x, c^c,o,x, cc,c,o,x for comparison)
family_members = []
for tok, n in cnt_full.items():
    if tok == "cc,o,x" or tok.endswith(",cc,o,x") or tok.endswith(",c^c,c,o,x") or tok == "c^c,c,o,x" or tok.endswith(",c^c,o,x") or tok == "c^c,o,x" or tok.endswith(",cc,c,o,x") or tok == "cc,c,o,x":
        family_members.append(tok)
family_members.sort(key=lambda x: -cnt_full[x])

print(f"{'token':>26} | {'total':>6} {'vms1':>5} {'%':>6} {'vms2':>5} {'%':>6} cliff  triples")
print("-" * 88)
for tok in family_members[:30]:
    n = cnt_full[tok]
    n1 = cnt_1.get(tok, 0)
    n2 = cnt_2.get(tok, 0)
    p1 = 100 * n1 / tot_1
    p2 = 100 * n2 / tot_2
    cliff = f"{p1/p2:.1f}x" if p2 > 0 else "—"
    trip = triples.get(tok, 0)
    print(f"{tok!r:>26} | {n:>6} {n1:>5} {p1:>5.3f}% {n2:>5} {p2:>5.3f}% {cliff:>5}  {trip}")
