"""Generic token exploration: given a target VMS token, report:
- frequency in vms / vms1 / vms2 (and the cliff ratio)
- paragraph-initial, paragraph-terminal, line-terminal rates (with baseline)
- tokens that contain the target as a subsequence (prefix/suffix breakdown)
- top preceding and following standalone tokens across the full VMS
- every paragraph where the target is paragraph-terminal

Usage: edit TARGET below or pass via sys.argv.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict

from voynpy.corpora import vms, vms1, vms2


TARGET = sys.argv[1] if len(sys.argv) > 1 else "c,M,c,o,Z"


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


def _lines(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        tokens = [row[c] for c in cols]
        tokens = [t for t in tokens if isinstance(t, str) and t != "$"]
        yield row["folio"], row.get("par"), row.get("line"), tokens


def _paragraphs(rt):
    groups = defaultdict(list)
    order = []
    for folio, par, line, tokens in _lines(rt):
        key = (folio, par)
        if key not in groups:
            order.append(key)
        groups[key].append((int(line), tokens))
    for key in order:
        yield key[0], key[1], sorted(groups[key], key=lambda x: x[0])


def freq_cliff(target):
    def count(rt):
        n = 0
        tot = 0
        for _, _, _, tokens in _lines(rt):
            tot += len(tokens)
            n += sum(1 for t in tokens if t == target)
        return n, tot
    n_full, tot_full = count(vms)
    n1, tot1 = count(vms1)
    n2, tot2 = count(vms2)
    print(f"=== Frequency of {target!r} ===")
    print(f"  vms  (full):        {n_full:4d} / {tot_full:,} = {100*n_full/tot_full:.3f}%")
    print(f"  vms1 (first half):  {n1:4d} / {tot1:,} = {100*n1/tot1:.3f}%")
    print(f"  vms2 (second half): {n2:4d} / {tot2:,} = {100*n2/tot2:.3f}%")
    if tot2 and n2:
        cliff = (n1/tot1) / (n2/tot2)
        print(f"  cliff ratio (vms1/vms2 rate): {cliff:.1f}x")
    elif n1:
        print("  cliff ratio: second half has zero occurrences")


def position_analysis(target):
    # paragraph-level + line-level stats
    para_hits_first = 0
    para_hits_last = 0
    para_hits_total = 0
    line_hits_last = 0
    line_hits_total = 0
    total_lines = 0
    total_tokens = 0
    terminal_paragraphs = []

    for folio, par, lines in _paragraphs(vms):
        flat = []
        for ln, toks in lines:
            total_lines += 1
            for i, t in enumerate(toks):
                total_tokens += 1
                flat.append((ln, i, t, len(toks)))
                if t == target:
                    line_hits_total += 1
                    if i == len(toks) - 1:
                        line_hits_last += 1
        n = len(flat)
        for idx, (ln, li, t, ln_len) in enumerate(flat):
            if t != target:
                continue
            para_hits_total += 1
            if idx == 0:
                para_hits_first += 1
            if idx == n - 1:
                para_hits_last += 1
                terminal_paragraphs.append((folio, par, lines))

    print(f"\n=== Position of {target!r} in full VMS ===")
    print(f"  total occurrences: {para_hits_total}")
    print(f"  paragraph-initial:  {para_hits_first:4d}  ({100*para_hits_first/para_hits_total:.1f}%)" if para_hits_total else "")
    print(f"  paragraph-terminal: {para_hits_last:4d}  ({100*para_hits_last/para_hits_total:.1f}%)" if para_hits_total else "")
    line_baseline = 100 * total_lines / total_tokens
    lt_rate = 100 * line_hits_last / line_hits_total if line_hits_total else 0
    lt_ratio = lt_rate / line_baseline if line_baseline else 0
    print(f"  line-terminal:      {line_hits_last:4d}  ({lt_rate:.1f}%)   baseline {line_baseline:.1f}%   ratio {lt_ratio:.2f}x")

    if terminal_paragraphs:
        print(f"\n  paragraph-terminal occurrences (showing full paragraphs):")
        for folio, par, lines in terminal_paragraphs:
            print(f"    --- {folio}.{par} ---")
            for ln, toks in lines:
                marker = " *" if target in toks else "  "
                print(f"   {marker} L{ln}: {' '.join(toks)}")


def subseq_indices(haystack, needle):
    hits = []
    m = len(needle)
    for i in range(len(haystack) - m + 1):
        if haystack[i:i + m] == needle:
            hits.append(i)
    return hits


def container_analysis(target):
    t_glyphs = target.split(",")
    prefix_counts = Counter()
    suffix_counts = Counter()
    container_counts = Counter()
    total = 0
    for t in tokens_of(vms):
        glyphs = t.split(",")
        for start in subseq_indices(glyphs, t_glyphs):
            total += 1
            pfx_g = glyphs[:start]
            sfx_g = glyphs[start + len(t_glyphs):]
            prefix_counts[",".join(pfx_g) if pfx_g else "<NONE>"] += 1
            suffix_counts[",".join(sfx_g) if sfx_g else "<NONE>"] += 1
            container_counts[t] += 1

    print(f"\n=== Tokens containing {target!r} (as comma-subsequence) ===")
    print(f"  total containers: {total}  ({len(container_counts)} distinct forms)")
    print("  top 12 container tokens:")
    for tok, n in container_counts.most_common(12):
        print(f"    {tok!r:>24}  {n:4d}")
    print("  top 12 PREFIXES:")
    for pfx, n in prefix_counts.most_common(12):
        print(f"    {pfx!r:>18}  {n:4d}  ({100*n/total:5.1f}%)")
    print("  top 6 SUFFIXES:")
    for sfx, n in suffix_counts.most_common(6):
        print(f"    {sfx!r:>18}  {n:4d}  ({100*n/total:5.1f}%)")


def neighbor_analysis(target):
    """Top standalone tokens appearing immediately before / after target
    (paragraph-level, not line-level — concatenate across lines within paragraph)."""
    before = Counter()
    after = Counter()
    for folio, par, lines in _paragraphs(vms):
        flat = []
        for _, toks in lines:
            flat.extend(toks)
        for i, t in enumerate(flat):
            if t != target:
                continue
            before[flat[i - 1] if i > 0 else "<START>"] += 1
            after[flat[i + 1] if i + 1 < len(flat) else "<END>"] += 1
    print(f"\n=== Standalone neighbors of {target!r} (paragraph-level) ===")
    print("  top 10 preceding tokens:")
    tot = sum(before.values())
    for tok, n in before.most_common(10):
        print(f"    {tok!r:>22}  {n:4d}  ({100*n/tot:5.1f}%)")
    print("  top 10 following tokens:")
    tot = sum(after.values())
    for tok, n in after.most_common(10):
        print(f"    {tok!r:>22}  {n:4d}  ({100*n/tot:5.1f}%)")


freq_cliff(TARGET)
position_analysis(TARGET)
container_analysis(TARGET)
neighbor_analysis(TARGET)
