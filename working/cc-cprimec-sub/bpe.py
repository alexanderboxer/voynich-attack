"""
Byte-Pair Encoding on VMS glyph sequences.

Starts with the 66 individual glyphs as the base vocabulary, then
iteratively merges the most frequent adjacent pair. Produces a
vocabulary of "patches" at any desired granularity.

Usage:
    python bpe.py              # default 50 merges
    python bpe.py 100          # 100 merges
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter

from voynpy.corpora import vms

here = Path(__file__).resolve().parent
root = Path(__file__).resolve().parents[2]

n_merges = int(sys.argv[1]) if len(sys.argv) > 1 else 50

# ==============================================================================
# Prepare corpus: each token is a tuple of glyphs
# ==============================================================================
# Normalize c^c -> cc, then split each token into a glyph sequence
def norm(tok):
    return tok.replace('c^c', 'cc')

corpus = [tuple(norm(t).split(',')) for t in vms.tklist]

base_vocab = sorted(set(g for tok in corpus for g in tok))
print(f"Base vocabulary: {len(base_vocab)} glyphs")
print(f"Corpus: {len(corpus)} tokens, {len(set(corpus))} unique")

# ==============================================================================
# BPE: iteratively merge most frequent adjacent glyph pair
# ==============================================================================
merges = []

for step in range(n_merges):
    # Count all adjacent pairs
    pair_counts = Counter()
    for tok in corpus:
        for i in range(len(tok) - 1):
            pair_counts[(tok[i], tok[i + 1])] += 1

    if not pair_counts:
        print(f"No more pairs to merge at step {step}")
        break

    best_pair = pair_counts.most_common(1)[0]
    pair, count = best_pair
    merged = pair[0] + ',' + pair[1]
    merges.append({'step': step, 'pair': list(pair), 'merged': merged, 'count': count})

    # Apply merge to corpus
    new_corpus = []
    for tok in corpus:
        new_tok = []
        i = 0
        while i < len(tok):
            if i < len(tok) - 1 and tok[i] == pair[0] and tok[i + 1] == pair[1]:
                new_tok.append(merged)
                i += 2
            else:
                new_tok.append(tok[i])
                i += 1
        new_corpus.append(tuple(new_tok))
    corpus = new_corpus

    if step < 20 or step % 10 == 0:
        n_unique = len(set(g for tok in corpus for g in tok))
        print(f"  Step {step:>3d}: merge {pair[0]:>15s} + {pair[1]:<15s} -> {merged:<30s} (count={count:>5d}, vocab={n_unique})")

# ==============================================================================
# Final vocabulary and statistics
# ==============================================================================
final_vocab = sorted(set(g for tok in corpus for g in tok))
patch_counts = Counter(g for tok in corpus for g in tok)

print(f"\nAfter {len(merges)} merges:")
print(f"  Vocabulary size: {len(final_vocab)}")
print(f"  Total patches in corpus: {sum(len(tok) for tok in corpus)}")
print(f"  Unique tokens (as patch sequences): {len(set(corpus))}")

# Token length distribution after BPE
token_lengths = Counter(len(tok) for tok in corpus)
print(f"\nToken length distribution (in patches):")
for l in sorted(token_lengths):
    print(f"  len={l}: {token_lengths[l]} tokens")

print(f"\nTop 30 patches by frequency:")
for patch, count in patch_counts.most_common(30):
    n_glyphs = len(patch.split(','))
    print(f"  {patch:<30s} (n={count:>5d}, glyphs={n_glyphs})")

# ==============================================================================
# Build sentences of patches for word2vec
# ==============================================================================
# Re-read paragraphs and segment each token into its BPE patches
pars_df = pd.read_csv(root / 'sequences/voypars.csv', dtype=str)

def apply_bpe(token_str, merges_list):
    """Apply learned BPE merges to a single token string (normalized)."""
    tok = tuple(norm(token_str).split(','))
    for m in merges_list:
        pair = tuple(m['pair'])
        merged = m['merged']
        new_tok = []
        i = 0
        while i < len(tok):
            if i < len(tok) - 1 and tok[i] == pair[0] and tok[i + 1] == pair[1]:
                new_tok.append(merged)
                i += 2
            else:
                new_tok.append(tok[i])
                i += 1
        tok = tuple(new_tok)
    return tok

# Build patch-level sentences (one per paragraph)
patch_sentences = []
for _, row in pars_df.iterrows():
    tokens = row.textstring.split('; ')
    sentence = []
    for t in tokens:
        patches = apply_bpe(t, merges)
        sentence.extend(patches)
    patch_sentences.append(sentence)

print(f"\nPatch-level sentences: {len(patch_sentences)}")
patch_vocab = sorted(set(p for s in patch_sentences for p in s))
print(f"Patch vocabulary: {len(patch_vocab)}")

patch_freq = Counter(p for s in patch_sentences for p in s)
hapax = sum(1 for v in patch_freq.values() if v == 1)
print(f"Hapax legomena: {hapax} ({100*hapax/len(patch_vocab):.1f}%)")

# ==============================================================================
# Export
# ==============================================================================
output = {
    'n_merges': len(merges),
    'merges': merges,
    'vocab': final_vocab,
    'patch_sentences': patch_sentences,
}

out_path = here / f'bpe_{len(merges)}.json'
with open(out_path, 'w') as f:
    json.dump(output, f)
print(f"\nSaved {out_path.name}")
