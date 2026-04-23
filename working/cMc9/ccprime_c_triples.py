"""Under the hypothesis c^c,c ≡ cc, scan for adjacent runs of tokens
that are all (c^c,c,X) or (cc,X) with the same suffix X. Any run of 3+
is a same-letter triple; any run of 4+ is a forbidden quadruple.

Also examine whether the 16 known c^c,c/cc adjacency pairs sit next to
yet another matching-suffix token, extending them into triples.
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


def equiv_class(token):
    """Normalize c^c,c → cc, returning the canonicalized token. Returns
    None if the token has no c^c,c or cc segments that would change."""
    parts = token.split(",")
    out = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and parts[i] == "c^c" and parts[i + 1] == "c":
            out.append("cc")
            i += 2
        else:
            out.append(parts[i])
            i += 1
    return ",".join(out)


# Pre-compute equivalence-class for every token
def walk_paragraphs_with_eq():
    for folio, par, flat in paragraphs(vms):
        eq_flat = [equiv_class(t) for t in flat]
        yield folio, par, flat, eq_flat


# Find runs of identical eq-class (of length >= 2) within paragraphs
runs_by_length = Counter()
run_examples = defaultdict(list)   # run_length -> list
new_triples = []     # runs created or expanded by substitution
new_quadruples = []

for folio, par, flat, eq_flat in walk_paragraphs_with_eq():
    i = 0
    while i < len(eq_flat) - 1:
        if eq_flat[i] == eq_flat[i + 1]:
            run = 2
            while i + run < len(eq_flat) and eq_flat[i + run] == eq_flat[i]:
                run += 1
            runs_by_length[run] += 1
            if run >= 3:
                # was this a triple BEFORE substitution?
                orig = flat[i:i + run]
                was_already_triple = all(t == orig[0] for t in orig)
                if not was_already_triple:
                    new_triples.append((folio, par, i, run, orig, eq_flat[i]))
                if run >= 4 and not was_already_triple:
                    new_quadruples.append((folio, par, i, run, orig, eq_flat[i]))
            i += run
        else:
            i += 1

print("=" * 80)
print("Runs (length >= 2) of identical EQUIVALENCE-CLASS tokens, under c^c,c ≡ cc")
print("=" * 80)
for length, n in sorted(runs_by_length.items()):
    print(f"  run length {length}: {n} occurrences")

print()
print("=" * 80)
print("NEW triples/quadruples created by the c^c,c ≡ cc substitution")
print("(runs of 3+ that were NOT already same-token triples pre-substitution)")
print("=" * 80)

if not new_triples:
    print("  None — every same-eq-class run of 3+ was already a native triple.")
else:
    for folio, par, i, run, orig, eq in new_triples:
        print(f"\n  --- {folio}.{par} @ token idx {i}  run length {run}  eq-class {eq!r} ---")
        print(f"    original tokens: {orig}")

print()
if new_quadruples:
    print(f"⚠ FORBIDDEN: {len(new_quadruples)} new QUADRUPLES created by substitution:")
    for folio, par, i, run, orig, eq in new_quadruples:
        print(f"  {folio}.{par} @ {i}: {orig!r} (eq-class {eq!r}, length {run})")
else:
    print("✓ No new quadruples created by the substitution.")
