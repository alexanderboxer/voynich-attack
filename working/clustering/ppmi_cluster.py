"""
PPMI + SVD token clustering experiment on wallis1 cipher text.

Builds a co-occurrence matrix, applies PPMI weighting, reduces with SVD,
then clusters and visualizes. Compares against word2vec baseline.

Usage:
    python ppmi_cluster.py              # run with default settings
    python ppmi_cluster.py --dim 24     # override embed_dim
    python ppmi_cluster.py --window 5   # override window
"""
# ==============================================================================
# Imports
# ==============================================================================
import argparse
import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
from collections import Counter

from voynpy.corpora import wallis1

# ==============================================================================
# Settings
# ==============================================================================
parser = argparse.ArgumentParser()
parser.add_argument('--dim', type=int, default=24)
parser.add_argument('--window', type=int, default=5)
parser.add_argument('--n_clusters', type=int, default=10)
parser.add_argument('--perplexity', type=int, default=15)
args = parser.parse_args()

here = Path(__file__).resolve().parent
root = Path(__file__).resolve().parents[2]

# ==============================================================================
# Load data
# ==============================================================================
with open(root / 'corpora/ciphers/wallis/wallis1.json') as f:
    j = json.load(f)
key_dict = j['key']

tklist = wallis1.tklist
vocab = sorted(set(tklist))
tok2idx = {t: i for i, t in enumerate(vocab)}
V = len(vocab)

print(f"Corpus: {len(tklist)} tokens, {V} unique")
print(f"Settings: dim={args.dim}, window={args.window}, n_clusters={args.n_clusters}")

# ==============================================================================
# Build co-occurrence matrix
# ==============================================================================
cooccur = np.zeros((V, V))
for i, tok in enumerate(tklist):
    ti = tok2idx[tok]
    for offset in range(1, args.window + 1):
        if i + offset < len(tklist):
            tj = tok2idx[tklist[i + offset]]
            cooccur[ti, tj] += 1
            cooccur[tj, ti] += 1

# ==============================================================================
# PPMI
# ==============================================================================
total = cooccur.sum()
row_sums = cooccur.sum(axis=1, keepdims=True)
col_sums = cooccur.sum(axis=0, keepdims=True)

with np.errstate(divide='ignore', invalid='ignore'):
    pmi = np.log2((cooccur * total) / (row_sums * col_sums))

pmi[~np.isfinite(pmi)] = 0
ppmi = np.maximum(pmi, 0)

# ==============================================================================
# SVD
# ==============================================================================
dim = min(args.dim, V - 1)
U, S, Vt = svds(csr_matrix(ppmi), k=dim)
# Weight by sqrt(S) — common practice
embeddings = U * np.sqrt(S)

tokens_in_model = vocab
print(f"Embedding shape: {embeddings.shape}")

# ==============================================================================
# Duplicate-plaintext scatter metric
# ==============================================================================
duplicate_groups = {
    'r': ['41', '52'],
    's': ['43', '54', 'ψ'],
}

group_scatters = {}
for pt, toks in duplicate_groups.items():
    idxs = [tok2idx[t] for t in toks]
    vecs = embeddings[idxs]
    centroid = vecs.mean(axis=0)
    dists = np.linalg.norm(vecs - centroid, axis=1)
    group_scatters[pt] = dists.mean()

scatter_metric = np.mean(list(group_scatters.values()))

print(f"\nScatter metric: {scatter_metric:.4f}  (lower is better)")
for pt, sc in group_scatters.items():
    print(f"  '{pt}' tokens {duplicate_groups[pt]}: mean dist from centroid = {sc:.4f}")

# ==============================================================================
# N-gram separation metric (silhouette score)
# ==============================================================================
ngram_labels = []
ngram_idxs = []
for t in vocab:
    pt = key_dict.get(t, '?')
    if pt == '?':
        continue
    ngram_labels.append(len(pt))
    ngram_idxs.append(tok2idx[t])

label_counts = Counter(ngram_labels)
keep = [i for i, lbl in enumerate(ngram_labels) if label_counts[lbl] > 1]
ngram_vecs = embeddings[np.array(ngram_idxs)][np.array(keep)]
ngram_labels_kept = [ngram_labels[i] for i in keep]

silhouette = silhouette_score(ngram_vecs, ngram_labels_kept)

print(f"\nN-gram silhouette: {silhouette:.4f}  (higher is better)")
for lbl in sorted(label_counts):
    marker = " *" if label_counts[lbl] == 1 else ""
    print(f"  {lbl}-gram: {label_counts[lbl]} tokens{marker}")

# ==============================================================================
# Cluster
# ==============================================================================
km = KMeans(n_clusters=args.n_clusters, random_state=42, n_init=20)
labels = km.fit_predict(embeddings)

cluster_df = pd.DataFrame({
    'token': tokens_in_model,
    'cluster': labels,
    'plaintext': [key_dict.get(t, '?') for t in tokens_in_model],
    'freq': [tklist.count(t) for t in tokens_in_model],
})

cluster_df['pt_len'] = cluster_df.plaintext.apply(lambda x: len(x) if x != '?' else None)
cluster_names = {}
for ngram_len, label in [(1, '1-gram'), (2, '2-gram')]:
    sub = cluster_df[cluster_df.pt_len == ngram_len]
    if len(sub) > 0:
        best_cluster = sub.groupby('cluster').size().idxmax()
        if best_cluster in cluster_names:
            cluster_names[best_cluster] += ' + ' + label
        else:
            cluster_names[best_cluster] = label

print("\n" + "=" * 60)
print("PPMI+SVD CLUSTERS (with plaintext key)")
print("=" * 60)
for c in range(args.n_clusters):
    members = cluster_df[cluster_df.cluster == c].sort_values('freq', ascending=False)
    tag = f'  <-- {cluster_names[c]}' if c in cluster_names else ''
    print(f"\nCluster {c} ({len(members)} tokens){tag}:")
    for _, row in members.iterrows():
        print(f"  {row.token:>6s} -> {row.plaintext:<12s} (n={row.freq})")

# ==============================================================================
# t-SNE visualization
# ==============================================================================
perp = min(args.perplexity, len(tokens_in_model) - 1)
tsne = TSNE(n_components=2, random_state=42, perplexity=perp)
coords = tsne.fit_transform(embeddings)

fig, axes = plt.subplots(1, 2, figsize=(20, 10))
fig.suptitle(f'PPMI+SVD (dim={args.dim}, window={args.window})  |  r-s scatter: {scatter_metric:.4f}  |  n-gram silhouette: {silhouette:.4f}', fontsize=14, fontweight='bold', y=0.98)

rs_tokens = set()
for toks in duplicate_groups.values():
    rs_tokens.update(toks)
is_rs = [tok in rs_tokens for tok in tokens_in_model]
rs_idx = np.array([i for i, v in enumerate(is_rs) if v])
not_rs_idx = np.array([i for i, v in enumerate(is_rs) if not v])

vmin, vmax = labels.min(), labels.max()
cmap = plt.cm.tab10
norm = plt.Normalize(vmin=vmin, vmax=vmax)
legend_handles = []
for c in range(args.n_clusters):
    lbl = f'Cluster {c}'
    if c in cluster_names:
        lbl += f' ({cluster_names[c]})'
    legend_handles.append(plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=cmap(norm(c)), markersize=8, label=lbl))

ax = axes[0]
ax.scatter(coords[not_rs_idx, 0], coords[not_rs_idx, 1], c=labels[not_rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=40, alpha=0.7)
ax.scatter(coords[rs_idx, 0], coords[rs_idx, 1], c=labels[rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=200, alpha=0.9, marker='*', edgecolors='black', linewidths=0.5)
for i, tok in enumerate(tokens_in_model):
    ax.annotate(tok, (coords[i, 0], coords[i, 1]), fontsize=7, alpha=0.8)
ax.set_title('PPMI+SVD — t-SNE colored by K-Means cluster')
ax.legend(handles=legend_handles, fontsize=7, loc='best')

ax = axes[1]
ax.scatter(coords[not_rs_idx, 0], coords[not_rs_idx, 1], c=labels[not_rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=40, alpha=0.7)
ax.scatter(coords[rs_idx, 0], coords[rs_idx, 1], c=labels[rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=200, alpha=0.9, marker='*', edgecolors='black', linewidths=0.5)
for i, tok in enumerate(tokens_in_model):
    pt = key_dict.get(tok, '?')
    ax.annotate(pt, (coords[i, 0], coords[i, 1]), fontsize=9, fontweight='bold', alpha=0.85)
ax.set_title('PPMI+SVD — t-SNE labeled with plaintext values')
ax.legend(handles=legend_handles, fontsize=7, loc='best')

plt.tight_layout()
plt.savefig(here / 'ppmi_clusters.png', dpi=150)
print(f"\nSaved ppmi_clusters.png")
plt.close()

cluster_df.to_csv(here / 'ppmi_clusters.csv', index=False)
print("Saved ppmi_clusters.csv")
