"""Prefix-family analysis. For every VMS token T, decompose into
(prefix, base) for each candidate prefix. Tabulate which bases accept
which prefix set, so we can see if `2`/`8` are structural siblings and
explore the `o,N` prefix.

A "base" is the remaining glyph sequence after stripping one of the
candidate prefixes. Only tokens with count >= MIN_OCC are reported.
"""

from __future__ import annotations

from collections import Counter, defaultdict

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

# Candidate prefixes — ordered. We'll try each as a potential prefix of T.
PREFIXES = [
    "2",
    "8",
    "cc",
    "c^c",
    "o",
    "N",
    "M",
    "9",
    "4,o",       # null
    "o,N",
    "o,M",
    "o,P2",
    "P2",
    "2,o",
    "8,o",
    "cc,o",
    "c^c,o",
    "cc,c",
    "9,M",
    "9,N",
    "4,o,N",
    "4,o,M",
]

# Map: base -> {prefix: count}
families: dict[str, Counter] = defaultdict(Counter)

for token, n in cnt.items():
    # bare token = "" prefix
    families[token][""] += n
    for pfx in PREFIXES:
        head = pfx + ","
        if token.startswith(head):
            base = token[len(head):]
            families[base][pfx] += n

# ---- Part 1: which bases accept BOTH `2` and `8` prefix?
print("=" * 72)
print("Bases accepting BOTH `2,` and `8,` prefixes (sorted by total 2+8 count)")
print("=" * 72)
pairs = []
for base, pfx_cnts in families.items():
    if pfx_cnts.get("2", 0) and pfx_cnts.get("8", 0):
        total = pfx_cnts["2"] + pfx_cnts["8"]
        pairs.append((base, pfx_cnts["2"], pfx_cnts["8"], pfx_cnts.get("", 0), total))
pairs.sort(key=lambda x: -x[4])
print(f"{'base':>22} | {'2,X':>5} {'8,X':>5} {'bare X':>8}   2:8 ratio")
print("-" * 72)
for base, n2, n8, nbare, _tot in pairs[:20]:
    ratio = f"{n2/n8:.2f}" if n8 else "—"
    print(f"{base!r:>22} | {n2:>5} {n8:>5} {nbare:>8}   {ratio}")
print(f"\nTotal bases with both 2 and 8 prefixes: {len(pairs)}")

# ---- Part 2: bases accepting `o,N,` prefix
print()
print("=" * 72)
print("Top bases accepting `o,N,` prefix")
print("=" * 72)
oN = [(base, pfx_cnts["o,N"], pfx_cnts.get("", 0)) for base, pfx_cnts in families.items()
      if pfx_cnts.get("o,N", 0) >= 3]
oN.sort(key=lambda x: -x[1])
print(f"{'base':>22} | {'o,N,X':>7} {'bare X':>8}")
for base, n, bare in oN[:20]:
    print(f"{base!r:>22} | {n:>7} {bare:>8}")

# ---- Part 3: the full prefix profile of selected "interesting" bases
print()
print("=" * 72)
print("Full prefix profile for interesting bases")
print("=" * 72)
interesting = ["a,m", "a,n", "a,Z", "a,x", "o,x", "o,Z", "9", "cc,o,x", "cc,o,Z", "c,M,c,9"]
for base in interesting:
    pfx_cnts = families.get(base, {})
    if not pfx_cnts:
        continue
    entries = sorted(pfx_cnts.items(), key=lambda x: -x[1])
    total = sum(pfx_cnts.values())
    print(f"\n--- base {base!r}  (total {total} occurrences across all prefixes) ---")
    for pfx, n in entries[:12]:
        label = pfx if pfx else "<bare>"
        print(f"   {label!r:>14} : {n:5d}  ({100*n/total:5.1f}%)")
