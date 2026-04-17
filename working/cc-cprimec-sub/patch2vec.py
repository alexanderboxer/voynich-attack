"""
Word2Vec on BPE patches of the Voynich Manuscript.

Trains word2vec on patch-level sentences from BPE output.
Focuses on identifying distributionally equivalent patches
(patches that appear in the same contexts).

Usage:
    python patch2vec.py              # use bpe_50.json, default w2v settings
    python patch2vec.py bpe_100.json # use a different BPE file
"""
# ==============================================================================
# Imports
# ==============================================================================
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

here = Path(__file__).resolve().parent

# ==============================================================================
# Settings (wallis1 baseline)
# ==============================================================================
s = {
    'embed_dim': 24,
    'window': 5,
    'min_count': 1,
    'epochs': 200,
    'sg': 1,
    'n_clusters': 10,
    'tsne_perplexity': 15,
    'seed': 42,
}

# ==============================================================================
# Load BPE data
# ==============================================================================
bpe_file = sys.argv[1] if len(sys.argv) > 1 else 'bpe_50.json'
bpe_path = here / bpe_file
with open(bpe_path) as f:
    bpe = json.load(f)

sentences = bpe['patch_sentences']
vocab = sorted(bpe['vocab'])
n_merges = bpe['n_merges']

freq = Counter(p for sent in sentences for p in sent)
total_patches = sum(freq.values())
print(f"BPE: {n_merges} merges, {len(vocab)} patches, {total_patches} total observations")
print(f"Sentences: {len(sentences)}")

# ==============================================================================
# Train Word2Vec
# ==============================================================================
model = Word2Vec(
    sentences=sentences,
    vector_size=s['embed_dim'],
    window=s['window'],
    min_count=s['min_count'],
    epochs=s['epochs'],
    sg=s['sg'],
    seed=s['seed'],
)

tokens_in_model = [t for t in vocab if t in model.wv]
embeddings = np.array([model.wv[t] for t in tokens_in_model])
print(f"Patches with embeddings: {len(tokens_in_model)}")

# ==============================================================================
# Cosine similarity: find most similar pairs
# ==============================================================================
cos_sim = cosine_similarity(embeddings)
np.fill_diagonal(cos_sim, -1)  # exclude self-similarity

# Top similar pairs
n_pairs = 30
pairs = []
sim_flat = cos_sim.copy()
for _ in range(n_pairs):
    i, j = np.unravel_index(sim_flat.argmax(), sim_flat.shape)
    pairs.append((tokens_in_model[i], tokens_in_model[j], sim_flat[i, j]))
    sim_flat[i, j] = -1
    sim_flat[j, i] = -1

print("\n" + "=" * 60)
print(f"TOP {n_pairs} MOST SIMILAR PATCH PAIRS (cosine similarity)")
print("=" * 60)
for a, b, sim in pairs:
    fa, fb = freq[a], freq[b]
    ga, gb = len(a.split(',')), len(b.split(','))
    print(f"  {a:<20s} ({ga}g, n={fa:>5d})  <->  {b:<20s} ({gb}g, n={fb:>5d})  sim={sim:.4f}")

# ==============================================================================
# Per-patch nearest neighbors
# ==============================================================================
print("\n" + "=" * 60)
print("NEAREST NEIGHBORS (top 3 for each patch)")
print("=" * 60)

# Sort by frequency for readability
sorted_patches = sorted(tokens_in_model, key=lambda t: freq[t], reverse=True)
for t in sorted_patches:
    neighbors = model.wv.most_similar(t, topn=3)
    nstr = '  '.join([f'{n[0]}({n[1]:.3f})' for n in neighbors])
    g = len(t.split(','))
    print(f"  {t:<25s} ({g}g, n={freq[t]:>5d}):  {nstr}")

# ==============================================================================
# Cluster
# ==============================================================================
km = KMeans(n_clusters=s['n_clusters'], random_state=s['seed'], n_init=20)
labels = km.fit_predict(embeddings)

print("\n" + "=" * 60)
print("CLUSTERS")
print("=" * 60)
for c in range(s['n_clusters']):
    members = [(tokens_in_model[i], freq[tokens_in_model[i]]) for i in range(len(tokens_in_model)) if labels[i] == c]
    members.sort(key=lambda x: x[1], reverse=True)
    glyphs = [len(m[0].split(',')) for m in members]
    print(f"\nCluster {c} ({len(members)} patches, avg glyphs={np.mean(glyphs):.1f}):")
    for tok, f in members:
        g = len(tok.split(','))
        print(f"  {tok:<25s} ({g}g, n={f:>5d})")

# ==============================================================================
# t-SNE visualization
# ==============================================================================
perp = min(s['tsne_perplexity'], len(tokens_in_model) - 1)
tsne = TSNE(n_components=2, random_state=s['seed'], perplexity=perp)
coords = tsne.fit_transform(embeddings)

fig, ax = plt.subplots(1, 1, figsize=(14, 14))

vmin, vmax = labels.min(), labels.max()
cmap = plt.cm.tab10
norm = plt.Normalize(vmin=vmin, vmax=vmax)

ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap='tab10', vmin=vmin, vmax=vmax, s=60, alpha=0.7)
for i, tok in enumerate(tokens_in_model):
    ax.annotate(tok, (coords[i, 0], coords[i, 1]), fontsize=8, fontweight='bold', alpha=0.85)
ax.set_title(f'VMS BPE patches ({n_merges} merges, {len(vocab)} patches) — Word2Vec + K-Means', fontsize=13)

legend_handles = []
for c in range(s['n_clusters']):
    n_members = (labels == c).sum()
    legend_handles.append(plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=cmap(norm(c)), markersize=8,
                          label=f'Cluster {c} (n={n_members})'))
ax.legend(handles=legend_handles, fontsize=8, loc='best')

plt.tight_layout()
plt.savefig(here / f'patch2vec_{n_merges}.png', dpi=150)
print(f"\nSaved patch2vec_{n_merges}.png")
plt.close()
