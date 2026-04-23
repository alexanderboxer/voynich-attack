"""Pattern search over VMS token sequences.

Pattern syntax (space-separated token specs, left to right):
- literal token:        `cc,o,x`
- alternation:          `cc,o,x|c^c,o,x`          (matches either)
- any token:            `*`
- quantifier:           `cc,o,x{2,4}`             (match between 2 and 4 reps)
                        `cc,o,x{3}`               (exactly 3)
                        `cc,o,x?`                 (0 or 1)

Matching happens within a single paragraph (tokens flattened across lines
in reading order). Each match reports (folio, par, start_idx, tokens).

Example:
    python pattern_search.py 'cc,o,x{3} 8,a,m'
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict

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


_QUANT_RE = re.compile(r"^(.+?)(?:\{(\d+)(?:,(\d+))?\}|\?)?$")


def parse_spec(spec: str):
    """Return (token_matcher, min_reps, max_reps).
    token_matcher is a frozenset of literal tokens, or None for wildcard."""
    m = _QUANT_RE.match(spec)
    body = m.group(1)
    q_min_s = m.group(2)
    q_max_s = m.group(3)
    is_optional = spec.endswith("?") and not q_min_s
    if body == "*":
        matcher = None  # wildcard
    else:
        alternatives = body.split("|")
        matcher = frozenset(alternatives)
    if is_optional:
        return matcher, 0, 1
    if q_min_s is not None:
        q_min = int(q_min_s)
        q_max = int(q_max_s) if q_max_s is not None else q_min
        return matcher, q_min, q_max
    return matcher, 1, 1


def token_matches(matcher, token):
    if matcher is None:
        return True
    return token in matcher


def match_at(specs, tokens, start):
    """Try to match the sequence of (matcher, min, max) specs starting at
    `start`. Returns (end_idx) on success or None. Uses greedy matching with
    backtracking for quantifiers."""
    def recurse(spec_i, tok_i):
        if spec_i == len(specs):
            return tok_i
        matcher, q_min, q_max = specs[spec_i]
        # how many reps can we consume greedily
        max_reps = 0
        while max_reps < q_max and tok_i + max_reps < len(tokens) \
                and token_matches(matcher, tokens[tok_i + max_reps]):
            max_reps += 1
        # backtrack from max down to q_min
        for reps in range(max_reps, q_min - 1, -1):
            result = recurse(spec_i + 1, tok_i + reps)
            if result is not None:
                return result
        return None
    return recurse(0, start)


def search(pattern_str, rt=vms):
    specs = [parse_spec(p) for p in pattern_str.split()]
    matches = []
    for folio, par, flat in paragraphs(rt):
        i = 0
        while i < len(flat):
            end = match_at(specs, flat, i)
            if end is not None and end > i:
                matches.append((folio, par, i, flat[i:end]))
                i = end  # skip past this match (non-overlapping)
            else:
                i += 1
    return matches


def report(pattern_str, rt=vms, max_show=20):
    matches = search(pattern_str, rt)
    print(f"Pattern: {pattern_str!r}")
    print(f"Matches: {len(matches)}")
    for folio, par, idx, toks in matches[:max_show]:
        print(f"  {folio}.{par}  @{idx:>3}:  {' '.join(toks)}")
    if len(matches) > max_show:
        print(f"  ... ({len(matches) - max_show} more)")
    return matches


if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else "cc,o,x{3} 8,a,m"
    report(pattern)
