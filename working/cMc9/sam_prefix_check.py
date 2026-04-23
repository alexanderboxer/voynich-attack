"""Verify cc=e hypothesis via 8,a,m (candidate 's').

If cc encodes 'e' and fuses onto the following token, then the cc-family
share of prefixes before 8,a,m should match the rate at which 'e' precedes
's' in Latin.
"""

from __future__ import annotations

from collections import Counter

from voynpy.corpora import vms, vms1, vms2, caesar, vitruvius, celsus, pliny, latin


# ---- Part 1: Latin — what letter precedes 's'? (and 'x' for reference)
def letter_before(rt, target):
    before = Counter()
    for word in rt.tklist:
        w = word.lower()
        for i, ch in enumerate(w):
            if ch == target:
                before[w[i - 1] if i > 0 else "<WORD_START>"] += 1
    return before


def top_n(cnt, n=6):
    tot = sum(cnt.values())
    return [(k, v, 100 * v / tot) for k, v in cnt.most_common(n)], tot


print("=" * 60)
print("LATIN: top letters preceding 's' vs 'x'")
print("=" * 60)
for target in ("s", "x"):
    print(f"\n--- before {target!r} ---")
    print(f"{'corpus':>12} | {'top preceding letters':<40}")
    for name, rt in [("caesar", caesar), ("vitruvius", vitruvius),
                     ("celsus", celsus), ("pliny", pliny), ("latin-all", latin)]:
        b = letter_before(rt, target)
        items, tot = top_n(b, 5)
        summary = "  ".join(f"{k!r}={p:.1f}%" for k, _, p in items)
        print(f"{name:>12} | n={tot:>6}   {summary}")


# ---- Part 2: VMS — prefix distribution on 8,a,m containers
TARGET = "8,a,m"
T_GLYPHS = TARGET.split(",")


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


def contains_subsequence(glyphs, targ):
    hits = []
    n, m = len(glyphs), len(targ)
    for i in range(n - m + 1):
        if glyphs[i:i + m] == targ:
            hits.append(i)
    return hits


def scan(rt, name):
    prefix_counts = Counter()
    total = 0
    for t in tokens_of(rt):
        glyphs = t.split(",")
        for start in contains_subsequence(glyphs, T_GLYPHS):
            total += 1
            prefix_glyphs = glyphs[:start]
            prefix = ",".join(prefix_glyphs) if prefix_glyphs else "<NONE>"
            prefix_counts[prefix] += 1
    return prefix_counts, total


def classify_family(prefix):
    if prefix == "<NONE>":
        return "<NONE>"
    parts = prefix.split(",")
    # strip leading 4,o (null delimiter)
    if len(parts) >= 2 and parts[0] == "4" and parts[1] == "o":
        parts = parts[2:]
    if not parts:
        return "<4,o-null>"
    first = parts[0]
    if first == "cc":
        return "cc-family"
    if first == "c^c":
        return "c^c-family"
    return "other"


print()
print("=" * 60)
print(f"VMS: prefix distribution for tokens containing {TARGET!r}")
print("=" * 60)
for rt, name in [(vms, "vms (full)"), (vms1, "vms1"), (vms2, "vms2")]:
    pfx, total = scan(rt, name)
    print(f"\n--- {name}: {total} tokens contain {TARGET!r} ---")
    print("  top 15 prefixes:")
    for p, n in pfx.most_common(15):
        print(f"    {p!r:>16}: {n:5d}  ({100*n/total:5.1f}%)")
    # family sums
    families = Counter()
    for p, n in pfx.items():
        families[classify_family(p)] += n
    print("  family totals:")
    for fam in ("<NONE>", "<4,o-null>", "cc-family", "c^c-family", "other"):
        if fam in families:
            print(f"    {fam:>14}: {families[fam]:5d}  ({100*families[fam]/total:5.1f}%)")
