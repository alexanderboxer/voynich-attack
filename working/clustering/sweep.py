"""Sweep 10 parameter variations and report the best metrics."""
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent

# Baseline for reference
base = {'embed_dim': 24, 'window': 5, 'min_count': 1, 'epochs': 200, 'sg': 1, 'n_clusters': 10, 'tsne_perplexity': 15, 'seed': 42}

# Round 3: small variations around baseline
variations = [
    {**base, 'embed_dim': 20},                                # 21
    {**base, 'embed_dim': 28},                                 # 22
    {**base, 'embed_dim': 32},                                 # 23
    {**base, 'epochs': 150},                                   # 24
    {**base, 'epochs': 250},                                   # 25
    {**base, 'epochs': 300},                                   # 26
    {**base, 'window': 4},                                     # 27
    {**base, 'window': 6},                                     # 28
    {**base, 'window': 7},                                     # 29
    {**base, 'embed_dim': 20, 'epochs': 150, 'window': 6},    # 30
]

# Write all experiments to experiments.json
with open(here / 'experiments.json') as f:
    exps = json.load(f)

start = max(int(k) for k in exps) + 1
for i, v in enumerate(variations, start=start):
    exps[str(i)] = v

with open(here / 'experiments.json', 'w') as f:
    json.dump(exps, f, indent=2)

exp_ids = list(range(start, start + len(variations)))

# Run each and capture both metrics
results = []
for i in exp_ids:
    print(f"\n{'='*60}")
    print(f"Running experiment {i}...")
    print(f"{'='*60}")
    proc = subprocess.run(
        ['python3', str(here / 'w2v_cluster.py'), str(i)],
        capture_output=True, text=True, cwd=str(here),
    )
    print(proc.stdout[-300:] if len(proc.stdout) > 300 else proc.stdout)
    scatter_val = silhouette_val = None
    for line in proc.stdout.splitlines():
        if line.startswith('Scatter metric:'):
            scatter_val = float(line.split(':')[1].split('(')[0].strip())
        if line.startswith('N-gram silhouette:'):
            silhouette_val = float(line.split(':')[1].split('(')[0].strip())
    results.append((i, scatter_val, silhouette_val, exps[str(i)]))

# Report (include baseline for reference)
results.append((0, 0.7478, -0.0692, base))

print("\n" + "=" * 60)
print("SWEEP RESULTS (sorted by n-gram silhouette, higher is better)")
print("=" * 60)
print(f"  {'Exp':>5s}  {'scatter':>8s}  {'silhouette':>10s}  changes")
print(f"  {'---':>5s}  {'-------':>8s}  {'----------':>10s}  -------")
for i, sc, si, params in sorted(results, key=lambda x: x[2], reverse=True):
    diff = {k: v for k, v in params.items() if v != base[k]}
    tag = '  (baseline)' if not diff else ''
    print(f"  Exp {i:>2d}:  {sc:.4f}      {si:+.4f}    {diff}{tag}")

best_sc = min(results, key=lambda x: x[1])
best_si = max(results, key=lambda x: x[2])
print(f"\nBest scatter:    experiment {best_sc[0]} = {best_sc[1]:.4f}")
print(f"Best silhouette: experiment {best_si[0]} = {best_si[2]:+.4f}")
