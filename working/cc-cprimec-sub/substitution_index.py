"""
Index where each cc/c^c substitution type is likely in the manuscript.

Type A: c^c,c <-> cc  (3 glyphs substitute for 2)
Type B: c^c   <-> cc  (1-for-1 substitution)

For each token containing c^c, check if applying each substitution
produces a token that exists elsewhere in the corpus. Map by location.
"""
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[2]

from voynpy.corpora import vms

# ==============================================================================
# Build frequency table
# ==============================================================================
freq = Counter(vms.tklist)
all_tokens = set(vms.tklist)

# ==============================================================================
# For each token with c^c, try both substitution types
# ==============================================================================
def apply_type_a(glyphs):
    """c^c,c -> cc: find first c^c followed by c and merge to cc."""
    results = []
    for i in range(len(glyphs) - 1):
        if glyphs[i] == 'c^c' and glyphs[i + 1] == 'c':
            new = glyphs[:i] + ['cc'] + glyphs[i + 2:]
            results.append(','.join(new))
    return results

def apply_type_a_reverse(glyphs):
    """cc -> c^c,c: find cc and expand to c^c,c."""
    results = []
    for i in range(len(glyphs)):
        if glyphs[i] == 'cc':
            new = glyphs[:i] + ['c^c', 'c'] + glyphs[i + 1:]
            results.append(','.join(new))
    return results

def apply_type_b(glyphs):
    """c^c -> cc: simple 1-for-1 substitution."""
    results = []
    for i in range(len(glyphs)):
        if glyphs[i] == 'c^c':
            new = glyphs[:i] + ['cc'] + glyphs[i + 1:]
            results.append(','.join(new))
    return results

def apply_type_b_reverse(glyphs):
    """cc -> c^c: simple 1-for-1 substitution."""
    results = []
    for i in range(len(glyphs)):
        if glyphs[i] == 'cc':
            new = glyphs[:i] + ['c^c'] + glyphs[i + 1:]
            results.append(','.join(new))
    return results

# ==============================================================================
# Scan the manuscript
# ==============================================================================
pars_df = pd.read_csv(root / 'sequences/voypars.csv', dtype=str)

records = []
for _, row in pars_df.iterrows():
    tokens = row.textstring.split('; ')
    idx = row.idx
    folio = idx.split('.')[0]

    for ti, tok in enumerate(tokens):
        glyphs = tok.split(',')

        if 'c^c' in glyphs:
            # Try Type A: c^c,c -> cc
            a_candidates = apply_type_a(glyphs)
            a_matches = [c for c in a_candidates if c in all_tokens]

            # Try Type B: c^c -> cc
            b_candidates = apply_type_b(glyphs)
            b_matches = [c for c in b_candidates if c in all_tokens]

            for match in a_matches:
                records.append({
                    'type': 'A',
                    'idx': idx,
                    'folio': folio,
                    'pos': ti,
                    'token': tok,
                    'tok_freq': freq[tok],
                    'partner': match,
                    'partner_freq': freq[match],
                })
            for match in b_matches:
                records.append({
                    'type': 'B',
                    'idx': idx,
                    'folio': folio,
                    'pos': ti,
                    'token': tok,
                    'tok_freq': freq[tok],
                    'partner': match,
                    'partner_freq': freq[match],
                })

        if 'cc' in glyphs:
            # Try Type A reverse: cc -> c^c,c
            a_candidates = apply_type_a_reverse(glyphs)
            a_matches = [c for c in a_candidates if c in all_tokens]

            # Try Type B reverse: cc -> c^c
            b_candidates = apply_type_b_reverse(glyphs)
            b_matches = [c for c in b_candidates if c in all_tokens]

            for match in a_matches:
                records.append({
                    'type': 'A',
                    'idx': idx,
                    'folio': folio,
                    'pos': ti,
                    'token': tok,
                    'tok_freq': freq[tok],
                    'partner': match,
                    'partner_freq': freq[match],
                })
            for match in b_matches:
                records.append({
                    'type': 'B',
                    'idx': idx,
                    'folio': folio,
                    'pos': ti,
                    'token': tok,
                    'tok_freq': freq[tok],
                    'partner': match,
                    'partner_freq': freq[match],
                })

df = pd.DataFrame(records)

# ==============================================================================
# Summary
# ==============================================================================
print(f"Total substitution records: {len(df)}")
print(f"  Type A (c^c,c <-> cc):  {len(df[df.type == 'A'])}")
print(f"  Type B (c^c <-> cc):    {len(df[df.type == 'B'])}")

# Deduplicate: count unique (token, partner) pairs per type
pairs_a = df[df.type == 'A'][['token', 'partner']].drop_duplicates()
pairs_b = df[df.type == 'B'][['token', 'partner']].drop_duplicates()
print(f"\nUnique token pairs:")
print(f"  Type A: {len(pairs_a)}")
print(f"  Type B: {len(pairs_b)}")

# ==============================================================================
# Folio distribution
# ==============================================================================
# Count occurrences of each type per folio
folio_type = df.groupby(['folio', 'type']).size().unstack(fill_value=0)
if 'A' not in folio_type.columns:
    folio_type['A'] = 0
if 'B' not in folio_type.columns:
    folio_type['B'] = 0

# Sort folios numerically
folio_type['folio_num'] = folio_type.index.map(lambda x: int(x.rstrip('abcdefghijklmnopqrstuvwxyz')))
folio_type = folio_type.sort_values('folio_num')
folio_type = folio_type.drop(columns='folio_num')

print("\nFolio distribution:")
print(f"{'folio':<10s} {'Type A':>8s} {'Type B':>8s} {'A/(A+B)':>8s}")
print("-" * 36)
for folio, row in folio_type.iterrows():
    a, b = row['A'], row['B']
    ratio = f"{a/(a+b):.2f}" if (a + b) > 0 else "—"
    print(f"{folio:<10s} {a:>8d} {b:>8d} {ratio:>8s}")

# ==============================================================================
# Tokens where ONLY Type A applies (no valid Type B partner)
# ==============================================================================
tokens_with_a = set(df[df.type == 'A'].token)
tokens_with_b = set(df[df.type == 'B'].token)
a_only = tokens_with_a - tokens_with_b
b_only = tokens_with_b - tokens_with_a
both = tokens_with_a & tokens_with_b

print(f"\nTokens with only Type A partner: {len(a_only)}")
print(f"Tokens with only Type B partner: {len(b_only)}")
print(f"Tokens with both:                {len(both)}")

# ==============================================================================
# Export
# ==============================================================================
here = Path(__file__).resolve().parent
df.to_csv(here / 'substitution_index.csv', index=False)
folio_type.to_csv(here / 'substitution_by_folio.csv')
print(f"\nSaved substitution_index.csv and substitution_by_folio.csv")
