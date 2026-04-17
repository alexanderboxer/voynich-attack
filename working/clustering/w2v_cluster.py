"""
Word2Vec token clustering experiment on wallis1 cipher text.

Trains a Word2Vec model on the wallis1 token sequence, clusters the
learned embeddings, and visualizes via t-SNE. Compares clusters against
the known plaintext key to check for meaningful groupings.

Usage:
    python w2v_cluster.py          # run with new settings, append as next experiment
    python w2v_cluster.py 0        # rerun experiment 0 (baseline)
    python w2v_cluster.py 3        # rerun experiment 3
"""
# ==============================================================================
# Imports
# ==============================================================================
import sys
import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

from voynpy.corpora import wallis1

# ==============================================================================
# Settings
# ==============================================================================
SETTINGS = {
    'embed_dim': 24,
    'window': 5,
    'min_count': 1,
    'epochs': 200,
    'sg': 1,            # 1 = skip-gram, 0 = CBOW
    'n_clusters': 10,
    'tsne_perplexity': 15,
    'seed': 42,
}

here = Path(__file__).resolve().parent
settings_path = here / 'experiments.json'

def load_experiments():
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}

def save_experiments(experiments):
    with open(settings_path, 'w') as f:
        json.dump(experiments, f, indent=2)

# Determine which experiment to run
experiments = load_experiments()

if len(sys.argv) > 1:
    # Rerun a saved experiment by number
    exp_num = sys.argv[1]
    if exp_num not in experiments:
        print(f"Experiment {exp_num} not found. Available: {sorted(experiments.keys(), key=int)}")
        sys.exit(1)
    s = experiments[exp_num]
    print(f"Rerunning experiment {exp_num}: {s}")
else:
    # New experiment — find next number and save
    if not experiments:
        exp_num = '0'
    else:
        exp_num = str(max(int(k) for k in experiments) + 1)
    s = SETTINGS
    experiments[exp_num] = s
    save_experiments(experiments)
    print(f"New experiment {exp_num}: {s}")

# ==============================================================================
# Load data
# ==============================================================================
root = Path(__file__).resolve().parents[2]
with open(root / 'corpora/ciphers/wallis/wallis1.json') as f:
    j = json.load(f)
key_dict = j['key']

# Build sentences from the original CSV rows (natural line breaks)
csv_path = root / 'corpora/ciphers/wallis/wallis1.csv'
df = pd.read_csv(csv_path, header=None).fillna('$')
sentences = []
for _, row in df.iterrows():
    tokens = [str(k) for k in row.values if str(k) != '$']
    tokens = [re.sub(r'\.0', '', k) for k in tokens]
    tokens = [k.replace('u', '').replace('\u2019', "'") for k in tokens]
    if tokens:
        sentences.append(tokens)

vocab = sorted(set(wallis1.tklist))
print(f"Corpus: {len(wallis1.tklist)} tokens, {len(vocab)} unique")
print(f"Sentences (CSV lines): {len(sentences)}")

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

# Build embedding matrix for all tokens in vocab
tokens_in_model = [t for t in vocab if t in model.wv]
embeddings = np.array([model.wv[t] for t in tokens_in_model])
print(f"Tokens with embeddings: {len(tokens_in_model)}")

# ==============================================================================
# Duplicate-plaintext scatter metric
# ==============================================================================
# Tokens sharing a plaintext value should be close in embedding space.
# Measure: mean distance from group centroid, averaged across groups.
duplicate_groups = {
    'r': ['41', '52'],
    's': ['43', '54', 'ψ'],
}

group_scatters = {}
for pt, toks in duplicate_groups.items():
    vecs = np.array([model.wv[t] for t in toks])
    centroid = vecs.mean(axis=0)
    dists = np.linalg.norm(vecs - centroid, axis=1)
    group_scatters[pt] = dists.mean()

scatter_metric = np.mean(list(group_scatters.values()))

print(f"\nScatter metric: {scatter_metric:.4f}  (lower is better)")
for pt, sc in group_scatters.items():
    toks = duplicate_groups[pt]
    print(f"  '{pt}' tokens {toks}: mean dist from centroid = {sc:.4f}")

# ==============================================================================
# N-gram separation metric (silhouette score)
# ==============================================================================
# Classify tokens by plaintext length (1, 2, 3, 4, ...).
# Silhouette score measures how well these groups separate in embedding space.
# Range: -1 to +1, higher is better.
# Groups with only 1 member are excluded (silhouette is undefined for them).
from sklearn.metrics import silhouette_score
from collections import Counter as _Counter

ngram_tokens = []
ngram_labels = []
ngram_vecs = []
for t in tokens_in_model:
    pt = key_dict.get(t, '?')
    if pt == '?':
        continue
    ngram_tokens.append(t)
    ngram_labels.append(len(pt))
    ngram_vecs.append(model.wv[t])

# Drop groups with only 1 member
label_counts = _Counter(ngram_labels)
keep = [i for i, lbl in enumerate(ngram_labels) if label_counts[lbl] > 1]
ngram_vecs_arr = np.array(ngram_vecs)[keep]
ngram_labels_kept = [ngram_labels[i] for i in keep]

silhouette = silhouette_score(ngram_vecs_arr, ngram_labels_kept)

print(f"\nN-gram silhouette: {silhouette:.4f}  (higher is better)")
for lbl in sorted(label_counts):
    marker = " *" if label_counts[lbl] == 1 else ""
    print(f"  {lbl}-gram: {label_counts[lbl]} tokens{marker}")
if any(v == 1 for v in label_counts.values()):
    print("  (* excluded from silhouette — only 1 member)")

# ==============================================================================
# Cluster
# ==============================================================================
km = KMeans(n_clusters=s['n_clusters'], random_state=s['seed'], n_init=20)
labels = km.fit_predict(embeddings)

# ==============================================================================
# Map clusters to plaintext for validation
# ==============================================================================
cluster_df = pd.DataFrame({
    'token': tokens_in_model,
    'cluster': labels,
    'plaintext': [key_dict.get(t, '?') for t in tokens_in_model],
    'freq': [wallis1.tklist.count(t) for t in tokens_in_model],
})

# Name clusters by n-gram concentration
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
print(f"EXPERIMENT {exp_num} — CLUSTERS (with plaintext key)")
print("=" * 60)
for c in range(s['n_clusters']):
    members = cluster_df[cluster_df.cluster == c].sort_values('freq', ascending=False)
    tag = f'  <-- {cluster_names[c]}' if c in cluster_names else ''
    print(f"\nCluster {c} ({len(members)} tokens){tag}:")
    for _, row in members.iterrows():
        print(f"  {row.token:>6s} -> {row.plaintext:<12s} (n={row.freq})")

# ==============================================================================
# t-SNE visualization
# ==============================================================================
perp = min(s['tsne_perplexity'], len(tokens_in_model) - 1)
tsne = TSNE(n_components=2, random_state=s['seed'], perplexity=perp)
coords = tsne.fit_transform(embeddings)

fig, axes = plt.subplots(1, 2, figsize=(20, 10))
fig.suptitle(f'Experiment {exp_num}  |  r-s scatter: {scatter_metric:.4f}  |  n-gram silhouette: {silhouette:.4f}', fontsize=14, fontweight='bold', y=0.98)

# Identify r/s duplicate tokens for star markers
rs_tokens = set()
for toks in duplicate_groups.values():
    rs_tokens.update(toks)
is_rs = [tok in rs_tokens for tok in tokens_in_model]
rs_idx = np.array([i for i, v in enumerate(is_rs) if v])
not_rs_idx = np.array([i for i, v in enumerate(is_rs) if not v])

vmin, vmax = labels.min(), labels.max()

# Build legend handles for cluster colors
cmap = plt.cm.tab10
norm = plt.Normalize(vmin=vmin, vmax=vmax)
legend_handles = []
for c in range(s['n_clusters']):
    lbl = f'Cluster {c}'
    if c in cluster_names:
        lbl += f' ({cluster_names[c]})'
    legend_handles.append(plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=cmap(norm(c)), markersize=8, label=lbl))

# Plot 1: colored by cluster, labeled with cipher token
ax = axes[0]
ax.scatter(coords[not_rs_idx, 0], coords[not_rs_idx, 1], c=labels[not_rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=40, alpha=0.7)
ax.scatter(coords[rs_idx, 0], coords[rs_idx, 1], c=labels[rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=200, alpha=0.9, marker='*', edgecolors='black', linewidths=0.5)
for i, tok in enumerate(tokens_in_model):
    ax.annotate(tok, (coords[i, 0], coords[i, 1]), fontsize=7, alpha=0.8)
ax.set_title(f'Experiment {exp_num} — t-SNE colored by K-Means cluster')
ax.legend(handles=legend_handles, fontsize=7, loc='best')


# Plot 2: colored by cluster, labeled with plaintext
ax = axes[1]
ax.scatter(coords[not_rs_idx, 0], coords[not_rs_idx, 1], c=labels[not_rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=40, alpha=0.7)
ax.scatter(coords[rs_idx, 0], coords[rs_idx, 1], c=labels[rs_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=200, alpha=0.9, marker='*', edgecolors='black', linewidths=0.5)
for i, tok in enumerate(tokens_in_model):
    pt = key_dict.get(tok, '?')
    ax.annotate(pt, (coords[i, 0], coords[i, 1]), fontsize=9, fontweight='bold', alpha=0.85)
ax.set_title(f'Experiment {exp_num} — t-SNE labeled with plaintext values')
ax.legend(handles=legend_handles, fontsize=7, loc='best')


png_path = here / f'w2v_clusters_{exp_num}.png'
plt.tight_layout()
plt.savefig(png_path, dpi=150)
print(f"\nSaved {png_path.name}")
plt.close()

# ==============================================================================
# Export cluster table
# ==============================================================================
csv_out = here / f'w2v_clusters_{exp_num}.csv'
cluster_df.to_csv(csv_out, index=False)
print(f"Saved {csv_out.name}")
