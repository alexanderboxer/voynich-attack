"""Find all VMS tokens that contain `c,M,c,9` as a glyph-subsequence.

Tally prefix (glyphs before) and suffix (glyphs after) distributions. Under
the "prefix attached to base" hypothesis, a common prefix like `cc,o` may
appear both (a) as a standalone token preceding c,M,c,9 and (b) fused into a
single token `cc,o,c,M,c,9` — so summing both gives a truer picture of what
letter(s) the preceding context encodes.
"""

from __future__ import annotations

from collections import Counter

from voynpy.corpora import vms, vms1, vms2


TARGET = "c,M,c,9"
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


def contains_subsequence(token_glyphs, target_glyphs):
    """Return list of (start_idx) where target appears as contiguous subsequence."""
    hits = []
    n, m = len(token_glyphs), len(target_glyphs)
    for i in range(n - m + 1):
        if token_glyphs[i:i + m] == target_glyphs:
            hits.append(i)
    return hits


def scan(rt, name):
    prefix_counts = Counter()
    suffix_counts = Counter()
    position_counts = Counter()
    container_examples = Counter()
    total_containing = 0
    total_tokens = 0
    for t in tokens_of(rt):
        total_tokens += 1
        glyphs = t.split(",")
        hits = contains_subsequence(glyphs, T_GLYPHS)
        for start in hits:
            total_containing += 1
            prefix_glyphs = glyphs[:start]
            suffix_glyphs = glyphs[start + len(T_GLYPHS):]
            prefix = ",".join(prefix_glyphs) if prefix_glyphs else "<NONE>"
            suffix = ",".join(suffix_glyphs) if suffix_glyphs else "<NONE>"
            prefix_counts[prefix] += 1
            suffix_counts[suffix] += 1
            if not prefix_glyphs and not suffix_glyphs:
                position = "standalone"
            elif not prefix_glyphs:
                position = "suffixed_only"
            elif not suffix_glyphs:
                position = "prefixed_only"
            else:
                position = "both"
            position_counts[position] += 1
            container_examples[t] += 1
    print(f"\n=== {name}: {total_tokens:,} total tokens, "
          f"{total_containing} contain {TARGET!r} ({100*total_containing/total_tokens:.2f}%) ===")
    print(f"  positional breakdown: {dict(position_counts)}")
    print("  top 15 distinct tokens containing c,M,c,9:")
    for tok, n in container_examples.most_common(15):
        print(f"    {tok!r:>26}  {n:4d}")
    print("  top 15 PREFIXES (glyphs before c,M,c,9 within the same token):")
    total = sum(prefix_counts.values())
    for pfx, n in prefix_counts.most_common(15):
        print(f"    {pfx!r:>18}  {n:4d}  ({100*n/total:5.1f}%)")
    print("  top 15 SUFFIXES (glyphs after c,M,c,9 within the same token):")
    total = sum(suffix_counts.values())
    for sfx, n in suffix_counts.most_common(15):
        print(f"    {sfx!r:>18}  {n:4d}  ({100*n/total:5.1f}%)")
    return prefix_counts, suffix_counts


for rt, name in [(vms, "vms (full)"), (vms1, "vms1 (first half)"), (vms2, "vms2 (second half)")]:
    scan(rt, name)
