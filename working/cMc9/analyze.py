"""Exploration: is VMS token c,M,c,9 = 'x'?

Three checks:
1. Equivalence rule `[prefix],c,9 ≡ [prefix],2,8` — does c,M,2,8 exist with a
   similar first-half-heavy profile? If yes, supports the equivalence.
2. Context distribution — top preceding / following tokens and paragraph
   position (initial / medial / terminal).
3. The terminal-double paragraph 44v.1.3 in full.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from voynpy.corpora import vms, vms1, vms2

HERE = Path(__file__).parent
TARGET = "c,M,c,9"


def _token_cols(df):
    return [c for c in df.columns if c.startswith("t") and c[1:].isdigit()]


def _lines(rt):
    """Yield (folio, par, line, [tokens]) for each row of the df (one line per row)."""
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        tokens = [row[c] for c in cols]
        tokens = [t for t in tokens if isinstance(t, str) and t != "$"]
        yield row["folio"], row.get("par"), row.get("line"), tokens


def _paragraphs(rt):
    """Yield (folio, par, [(line, tokens), ...]) for each distinct (folio, par),
    with lines ordered by line index and tokens concatenated in reading order."""
    groups: dict = {}
    order: list = []
    for folio, par, line, tokens in _lines(rt):
        key = (folio, par)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append((int(line), tokens))
    for key in order:
        lines = sorted(groups[key], key=lambda x: x[0])
        yield key[0], key[1], lines


def count(rt, target):
    total = 0
    tkn_total = 0
    for _, _, lines in _paragraphs(rt):
        for _, tokens in lines:
            tkn_total += len(tokens)
            total += sum(1 for t in tokens if t == target)
    return total, tkn_total


def context(rt, target):
    """Emit one record per occurrence, with paragraph-level position info.

    `para_tokens` concatenates all tokens from all lines in the paragraph so
    that is_para_first / is_para_last reflect the paragraph as a whole — not
    just the line the token lives on.
    """
    before = Counter()
    after = Counter()
    positions = []
    for folio, par, lines in _paragraphs(rt):
        # flatten: [(line_num, token_idx_in_line, token), ...]
        flat = []
        for line_num, tokens in lines:
            for i, t in enumerate(tokens):
                flat.append((line_num, i, t))
        all_tokens = [t for _, _, t in flat]
        n = len(all_tokens)
        for para_idx, (line_num, line_idx, t) in enumerate(flat):
            if t != target:
                continue
            b = all_tokens[para_idx - 1] if para_idx > 0 else "<START>"
            a = all_tokens[para_idx + 1] if para_idx + 1 < n else "<END>"
            before[b] += 1
            after[a] += 1
            positions.append({
                "folio": folio, "par": par, "line": line_num,
                "para_idx": para_idx, "para_len": n,
                "line_idx": line_idx,
                "rel_pos": round(para_idx / (n - 1), 3) if n > 1 else 0.5,
                "is_para_first": para_idx == 0,
                "is_para_last":  para_idx == n - 1,
                "is_line_first": line_idx == 0,
                "is_line_last":  line_idx == len([x for x in flat if x[0] == line_num]) - 1,
                "before": b,
                "after": a,
            })
    return before, after, positions


def show_paragraph(rt, folio, par):
    """Return the paragraph's lines as [(line_num, [tokens]), ...] sorted by line."""
    for f, p, lines in _paragraphs(rt):
        if f == folio and int(p) == par:
            return lines
    return None


def main():
    # ---- 1. Equivalence check
    print("=" * 62)
    print("1. EQUIVALENCE CHECK  [prefix],c,9  ≡  [prefix],2,8")
    print("=" * 62)
    print(f"{'token':>12} | {'vms1 n':>7} {'vms1 %':>7} | {'vms2 n':>7} {'vms2 %':>7}")
    print("-" * 62)
    for t in [TARGET, "c,M,2,8"]:
        n1, tot1 = count(vms1, t)
        n2, tot2 = count(vms2, t)
        pct1 = 100 * n1 / tot1 if tot1 else 0
        pct2 = 100 * n2 / tot2 if tot2 else 0
        print(f"{t:>12} | {n1:>7} {pct1:>6.3f}% | {n2:>7} {pct2:>6.3f}%")

    # ---- 2. Context on full VMS
    b, a, positions = context(vms, TARGET)
    print()
    print("=" * 62)
    print(f"2. CONTEXT FOR {TARGET!r} ({sum(b.values())} occurrences in full VMS)")
    print("=" * 62)
    print("\nTop 10 preceding tokens:")
    tot = sum(b.values())
    for tok, n in b.most_common(10):
        print(f"  {tok!r:>22}  {n:4d}  ({100*n/tot:.1f}%)")
    print("\nTop 10 following tokens:")
    tot = sum(a.values())
    for tok, n in a.most_common(10):
        print(f"  {tok!r:>22}  {n:4d}  ({100*n/tot:.1f}%)")

    total = len(positions)
    para_first = sum(1 for p in positions if p["is_para_first"])
    para_last  = sum(1 for p in positions if p["is_para_last"])
    line_first = sum(1 for p in positions if p["is_line_first"])
    line_last  = sum(1 for p in positions if p["is_line_last"])
    print("\nParagraph-level position (grouping by (folio, par)):")
    print(f"  paragraph-initial:  {para_first:3d} ({100*para_first/total:.1f}%)")
    print(f"  paragraph-terminal: {para_last:3d} ({100*para_last/total:.1f}%)")
    print(f"  paragraph-medial:   {total-para_first-para_last:3d}"
          f" ({100*(total-para_first-para_last)/total:.1f}%)")
    print("\nLine-level position (as a cross-check):")
    print(f"  line-initial:  {line_first:3d} ({100*line_first/total:.1f}%)")
    print(f"  line-terminal: {line_last:3d} ({100*line_last/total:.1f}%)")

    # ---- 3. List every paragraph where c,M,c,9 is paragraph-terminal
    print()
    print("=" * 62)
    print("3. EVERY PARAGRAPH WHERE c,M,c,9 IS THE FINAL TOKEN")
    print("=" * 62)
    terminal_positions = [p for p in positions if p["is_para_last"]]
    for pos in terminal_positions:
        folio, par = pos["folio"], pos["par"]
        lines = show_paragraph(vms, folio, par)
        print(f"\n  --- {folio}.{par}  ({pos['para_len']} tokens across {len(lines)} lines) ---")
        for line_num, toks in lines:
            marker = " *" if TARGET in toks else "  "
            print(f"  {marker} L{line_num}: {' '.join(toks)}")

    # ---- Save context CSV
    out_csv = HERE / "cMc9_context.csv"
    if positions:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(positions[0].keys()))
            w.writeheader()
            w.writerows(positions)
        print(f"\nWrote {len(positions)} occurrence rows to {out_csv}")


if __name__ == "__main__":
    main()
