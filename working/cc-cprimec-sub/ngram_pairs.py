"""
Find near-duplicate n-gram sequences in the VMS, assuming cc ≡ c^c.

Extracts sliding-window n-grams from voypars.csv paragraphs, normalizes
cc/c^c, and finds pairs that differ in exactly 1 internal token.

Usage:
    python ngram_pairs.py                  # default: 5-grams, internal diff only
    python ngram_pairs.py --n 4            # 4-grams
    python ngram_pairs.py --n 6            # 6-grams
    python ngram_pairs.py --any-pos        # allow diff at any position (not just internal)
    python ngram_pairs.py --max-diff 2     # allow up to 2 differing tokens
"""
import argparse
import pandas as pd
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[2]

# ==============================================================================
# Settings
# ==============================================================================
parser = argparse.ArgumentParser()
parser.add_argument('--n', type=int, default=5, help='n-gram length')
parser.add_argument('--any-pos', action='store_true', help='allow diff at any position, not just internal')
parser.add_argument('--max-diff', type=int, default=1, help='max number of differing tokens')
args = parser.parse_args()

N = args.n
internal_only = not args.any_pos
max_diff = args.max_diff

# ==============================================================================
# Load data
# ==============================================================================
pars_df = pd.read_csv(root / 'sequences/voypars.csv', dtype=str)

def norm(tok):
    return tok.replace('c^c', 'cc')

# ==============================================================================
# Extract n-grams with location
# ==============================================================================
ngrams = []  # (original_tokens, normalized_tokens, idx, position)
for _, row in pars_df.iterrows():
    tokens = row.textstring.split('; ')
    idx = row.idx
    for i in range(len(tokens) - N + 1):
        orig = tuple(tokens[i:i + N])
        normed = tuple(norm(t) for t in orig)
        ngrams.append((orig, normed, idx, i))

print(f"n={N}, {len(ngrams)} n-grams from {len(pars_df)} paragraphs")
print(f"internal_only={internal_only}, max_diff={max_diff}")

# ==============================================================================
# Find pairs differing in exactly `max_diff` positions
# ==============================================================================
if max_diff == 1:
    # Efficient: group by dropping one position at a time
    diff_positions = range(1, N - 1) if internal_only else range(N)
    results = []

    for drop_pos in diff_positions:
        groups = defaultdict(list)
        for orig, normed, idx, pos in ngrams:
            key = normed[:drop_pos] + normed[drop_pos + 1:]
            groups[key].append((orig, normed, idx, pos))

        for key, members in groups.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a_orig, a_norm, a_idx, a_pos = members[i]
                    b_orig, b_norm, b_idx, b_pos = members[j]
                    if a_norm[drop_pos] != b_norm[drop_pos]:
                        results.append((drop_pos, a_orig, a_idx, a_pos, b_orig, b_idx, b_pos))

else:
    # General case: group by (N - max_diff) matching positions
    # For each combination of positions to keep fixed, group and compare
    from itertools import combinations

    fixed_positions_list = list(combinations(range(N), N - max_diff))
    if internal_only:
        # First and last must always be in the fixed set
        fixed_positions_list = [fp for fp in fixed_positions_list if 0 in fp and (N - 1) in fp]

    results = []
    seen_pairs = set()

    for fixed_positions in fixed_positions_list:
        groups = defaultdict(list)
        for orig, normed, idx, pos in ngrams:
            key = tuple(normed[p] for p in fixed_positions)
            groups[key].append((orig, normed, idx, pos))

        for key, members in groups.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a_orig, a_norm, a_idx, a_pos = members[i]
                    b_orig, b_norm, b_idx, b_pos = members[j]
                    # Count actual differences
                    diffs = [p for p in range(N) if a_norm[p] != b_norm[p]]
                    if len(diffs) != max_diff:
                        continue
                    if internal_only and (0 in diffs or N - 1 in diffs):
                        continue
                    pair_key = (min((a_idx, a_pos), (b_idx, b_pos)),
                                max((a_idx, a_pos), (b_idx, b_pos)))
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)
                    results.append((diffs, a_orig, a_idx, a_pos, b_orig, b_idx, b_pos))

# ==============================================================================
# Display
# ==============================================================================
if max_diff == 1:
    results.sort(key=lambda x: (x[0], x[2], x[3]))
else:
    results.sort(key=lambda x: (x[0], x[2], x[3]))

print(f"\nPairs found: {len(results)}\n")

for entry in results:
    if max_diff == 1:
        diff_pos, a_orig, a_idx, a_pos, b_orig, b_idx, b_pos = entry
        diff_positions_list = [diff_pos]
    else:
        diff_positions_list, a_orig, a_idx, a_pos, b_orig, b_idx, b_pos = entry

    a_str = list(a_orig)
    b_str = list(b_orig)
    for d in diff_positions_list:
        a_str[d] = '[' + a_str[d] + ']'
        b_str[d] = '[' + b_str[d] + ']'

    diff_label = ','.join(str(d + 1) for d in diff_positions_list)
    print(f"  diff@{diff_label}  {a_idx}:{a_pos}  {'; '.join(a_str)}")
    print(f"  {' ' * len(f'diff@{diff_label}')}  {b_idx}:{b_pos}  {'; '.join(b_str)}")
    print()
