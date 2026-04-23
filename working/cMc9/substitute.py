"""Substitution engine for testing letter hypotheses on VMS paragraphs.

Given a dict of {vms_token: letter}, apply substitutions to every token in
a paragraph and show the resulting letter sequence. Tokens without a
mapping are shown with brackets so we can see what's still unresolved.

Two modes:
- `substitute_exact`: replace the whole token if it exactly matches a key.
- `substitute_recursive`: strip 4,o prefix first (null), then replace; if
  token still unmatched, attempt to extract the longest known substring.
"""

from __future__ import annotations

import sys
from collections import defaultdict

from voynpy.corpora import vms


# Current tentative letter mappings — edit freely
MAPPING = {
    "8,a,m":     "s",
    "cc,o,x":    "i",
    "c,M,c,9":   "x",
    "cc,o,Z":    "c",   # user's tentative
    "c,M,c,o,Z": "t",   # user's tentative
    # experimental: cc as 'e' (only within fused tokens — not a standalone map here)
}

# 4,o stripped first (null delimiter, per prior decipherment plan).
NULL_PREFIXES = ["4,o"]


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
        lines = sorted(groups[key], key=lambda x: x[0])
        yield key[0], key[1], lines


def strip_null(token: str) -> str:
    for pfx in NULL_PREFIXES:
        head = pfx + ","
        while token.startswith(head):
            token = token[len(head):]
        if token == pfx:
            return ""
    return token


def substitute_recursive(token: str, mapping: dict[str, str]) -> str:
    """Strip null prefixes, then either:
       - exact-match replacement
       - extract the longest known mapping substring (contiguous comma
         subsequence), replace, and recurse on remainder prefix/suffix.
       Returns a string with substituted letters in place and unresolved
       glyph groups in <angle brackets>.
    """
    t = strip_null(token)
    if t == "":
        return ""
    if t in mapping:
        return mapping[t]

    glyphs = t.split(",")
    # try longest substring match
    best = None  # (start, length, letter)
    for start in range(len(glyphs)):
        for end in range(len(glyphs), start, -1):
            sub = ",".join(glyphs[start:end])
            if sub in mapping:
                if best is None or (end - start) > best[1]:
                    best = (start, end - start, mapping[sub])
    if best is None:
        return "<" + t + ">"
    s_idx, length, letter = best
    left = ",".join(glyphs[:s_idx])
    right = ",".join(glyphs[s_idx + length:])
    left_out = substitute_recursive(left, mapping) if left else ""
    right_out = substitute_recursive(right, mapping) if right else ""
    return left_out + letter + right_out


def render_paragraph(folio, par, lines, mapping):
    print(f"=== {folio}.{par} ===")
    for ln, toks in lines:
        stripped = [strip_null(t) for t in toks]
        subs = [substitute_recursive(t, mapping) for t in stripped]
        # show original vs substituted per token
        print(f"  L{ln}:")
        print(f"    vms: {' '.join(toks)}")
        print(f"    sub: {' · '.join(subs)}")
    print()


def find_paragraph(folio: str, par):
    for f, p, lines in paragraphs(vms):
        if f == folio and int(p) == int(par):
            return (f, p, lines)
    return None


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "19v.1"
    folio, par = target.split(".")
    found = find_paragraph(folio, par)
    if not found:
        print(f"paragraph {target} not found")
        sys.exit(1)
    render_paragraph(*found, MAPPING)
    print("Mapping used:")
    for k, v in sorted(MAPPING.items()):
        print(f"  {k!r:>14} → {v!r}")
    print(f"  (+ null prefixes stripped: {NULL_PREFIXES})")
