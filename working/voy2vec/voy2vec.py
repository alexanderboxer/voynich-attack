"""
Word2Vec token clustering on the Voynich Manuscript.

Uses baseline settings from wallis1 experiments (embed_dim=24, window=5,
epochs=200, skip-gram). Sentences are the 801 paragraphs from voypars.csv.
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

from voynpy.corpora import vms

# ==============================================================================
# Settings
# ==============================================================================
SETTINGS = {
    'embed_dim': 24,
    'window': 5,
    'min_count': 1,
    'epochs': 200,
    'sg': 1,
    'n_clusters': 10,
    'tsne_perplexity': 15,
    'seed': 42,
}

here = Path(__file__).resolve().parent
root = Path(__file__).resolve().parents[2]
settings_path = here / 'experiments.json'

def load_experiments():
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}

def save_experiments(experiments):
    with open(settings_path, 'w') as f:
        json.dump(experiments, f, indent=2)

experiments = load_experiments()

if len(sys.argv) > 1:
    exp_num = sys.argv[1]
    if exp_num not in experiments:
        print(f"Experiment {exp_num} not found. Available: {sorted(experiments.keys(), key=int)}")
        sys.exit(1)
    s = experiments[exp_num]
    print(f"Rerunning experiment {exp_num}: {s}")
else:
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
pars_df = pd.read_csv(root / 'sequences/voypars.csv', dtype=str)
sentences = [row.textstring.split('; ') for _, row in pars_df.iterrows()]

vocab = sorted(set(vms.tklist))
print(f"Corpus: {len(vms.tklist)} tokens, {len(vocab)} unique")
print(f"Sentences (paragraphs): {len(sentences)}")

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
print(f"Tokens with embeddings: {len(tokens_in_model)}")

# ==============================================================================
# Cluster
# ==============================================================================
km = KMeans(n_clusters=s['n_clusters'], random_state=s['seed'], n_init=20)
labels = km.fit_predict(embeddings)

cluster_df = pd.DataFrame({
    'token': tokens_in_model,
    'cluster': labels,
    'freq': [vms.tklist.count(t) for t in tokens_in_model],
    'token_len': [len(t.split(',')) for t in tokens_in_model],
})

print("\n" + "=" * 60)
print(f"EXPERIMENT {exp_num} — VMS CLUSTERS")
print("=" * 60)
for c in range(s['n_clusters']):
    members = cluster_df[cluster_df.cluster == c].sort_values('freq', ascending=False)
    avg_len = members.token_len.mean()
    print(f"\nCluster {c} ({len(members)} tokens, avg glyph len={avg_len:.1f}):")
    for _, row in members.head(15).iterrows():
        print(f"  {row.token:<25s} (n={row.freq}, glyphs={row.token_len})")
    if len(members) > 15:
        print(f"  ... and {len(members) - 15} more")

# ==============================================================================
# t-SNE visualization
# ==============================================================================
perp = min(s['tsne_perplexity'], len(tokens_in_model) - 1)
tsne = TSNE(n_components=2, random_state=s['seed'], perplexity=perp)
coords = tsne.fit_transform(embeddings)

fig, axes = plt.subplots(1, 2, figsize=(20, 10))
fig.suptitle(f'VMS Experiment {exp_num}', fontsize=14, fontweight='bold', y=0.98)

vmin, vmax = labels.min(), labels.max()
cmap = plt.cm.tab10
norm = plt.Normalize(vmin=vmin, vmax=vmax)

# Cluster legend
legend_handles = []
for c in range(s['n_clusters']):
    n_members = (labels == c).sum()
    avg_len = cluster_df[cluster_df.cluster == c].token_len.mean()
    legend_handles.append(plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=cmap(norm(c)), markersize=8,
                          label=f'Cluster {c} (n={n_members}, avg_len={avg_len:.1f})'))

# Plot 1: all tokens colored by cluster
ax = axes[0]
ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap='tab10', vmin=vmin, vmax=vmax, s=10, alpha=0.5)
ax.set_title(f'Experiment {exp_num} — all {len(tokens_in_model)} tokens')
ax.legend(handles=legend_handles, fontsize=7, loc='best')

# Plot 2: top 200 most frequent tokens, labeled
ax = axes[1]
ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap='tab10', vmin=vmin, vmax=vmax, s=10, alpha=0.2)
top_n = 200
top_idx = cluster_df.nlargest(top_n, 'freq').index.tolist()
ax.scatter(coords[top_idx, 0], coords[top_idx, 1], c=labels[top_idx], cmap='tab10', vmin=vmin, vmax=vmax, s=30, alpha=0.8)
for i in top_idx:
    ax.annotate(tokens_in_model[i], (coords[i, 0], coords[i, 1]), fontsize=5, alpha=0.8)
ax.set_title(f'Experiment {exp_num} — top {top_n} tokens labeled')
ax.legend(handles=legend_handles, fontsize=7, loc='best')

png_path = here / f'voy2vec_{exp_num}.png'
plt.tight_layout()
plt.savefig(png_path, dpi=150)
print(f"\nSaved {png_path.name}")
plt.close()

csv_out = here / f'voy2vec_{exp_num}.csv'
cluster_df.to_csv(csv_out, index=False)
print(f"Saved {csv_out.name}")
