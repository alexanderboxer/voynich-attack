"""Test hypothesis: o,N,cc,o,x = 'r'.

Enumerate all 10 VMS occurrences and examine:
- Paragraph context (where in paragraph is it, which paragraph)
- Preceding and following tokens
- Co-occurrence with already-guessed tokens (cc,o,x='i', 8,a,m='s', c,M,c,9='x')
- Under Latin 'r', the expected neighbor letters are:
    before r: often vowels (a,e,i,o,u) or plosives (b,p,t,c,g)
    after r:  often vowels or {t,n,m,s,x} (Latin -rt, -rn, -rm, -rs, -rex)
"""

from __future__ import annotations

from collections import Counter, defaultdict

from voynpy.corpora import vms


TARGET = "o,N,cc,o,x"


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


# ---- Part 1: enumerate every occurrence + local context
print("=" * 80)
print(f"All VMS occurrences of {TARGET!r}")
print("=" * 80)
before_counter = Counter()
after_counter = Counter()
occurrences = []
for folio, par, flat in paragraphs(vms):
    for i, t in enumerate(flat):
        if t != TARGET:
            continue
        b = flat[i - 1] if i > 0 else "<START>"
        a = flat[i + 1] if i + 1 < len(flat) else "<END>"
        before_counter[b] += 1
        after_counter[a] += 1
        # 6-token window around the hit
        window_start = max(0, i - 3)
        window_end = min(len(flat), i + 4)
        window = flat[window_start:window_end]
        hit_idx = i - window_start
        occurrences.append((folio, par, i, len(flat), window, hit_idx))

for folio, par, idx, total, window, hit_idx in occurrences:
    print(f"\n  --- {folio}.{par}  (position {idx}/{total - 1}) ---")
    parts = []
    for k, tok in enumerate(window):
        if k == hit_idx:
            parts.append(f"*{tok}*")
        else:
            parts.append(tok)
    print(f"    context: {'  '.join(parts)}")


# ---- Part 2: neighbor tallies
print("\n" + "=" * 80)
print(f"Neighbor tallies ({len(occurrences)} occurrences total)")
print("=" * 80)
print("\ntop preceding tokens:")
for tok, n in before_counter.most_common():
    print(f"  {tok!r:>26}  {n}")
print("\ntop following tokens:")
for tok, n in after_counter.most_common():
    print(f"  {tok!r:>26}  {n}")


# ---- Part 3: frequency vs Latin 'r'
# Latin 'r' is ~5-7% of letters. Under 'r' hypothesis, o,N,cc,o,x as a
# single 'r'-encoding token at 10 occurrences (all vms1) is a tiny slice
# of total 'r's needed. Sanity check:
total_tokens_vms1 = sum(
    1 for _, _, flat in paragraphs(vms) if flat for t in flat if t != ""
)
# More precise — vms1 only
from voynpy.corpora import vms1
def _tokens_of(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        for c in cols:
            t = row[c]
            if isinstance(t, str) and t != "$":
                yield t
n_vms1_total = sum(1 for _ in _tokens_of(vms1))
print()
print("=" * 80)
print("Sanity check: frequency of o,N,cc,o,x in vms1")
print("=" * 80)
hits_vms1 = sum(1 for t in _tokens_of(vms1) if t == TARGET)
print(f"  {TARGET!r}: {hits_vms1} / {n_vms1_total:,} = {100*hits_vms1/n_vms1_total:.3f}%")
print(f"  Latin 'r' is typically 5-7% of letters. So if o,N,cc,o,x = 'r',")
print(f"  we'd need ~{int(n_vms1_total * 0.06)} 'r's total; this token covers {hits_vms1},")
print(f"  so the remaining 'r' letters must be encoded by other tokens (your 'many tokens per letter' framework).")
