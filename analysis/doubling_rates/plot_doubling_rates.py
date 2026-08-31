#==================================================
# Imports
#==================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from voynpy.corpora import vms


#==================================================
# Config
#==================================================
source_filename1 = 'nl_ngram_doubling_rates_per_1000_pairs.csv'
source_filename2 = 'nl_word_doubling_rates_per_1000_pairs.csv'
target_filename = 'nl_doubling_rates_per_1000_pairs.png'
file_export_flag = False


#==================================================
# Load Data
#==================================================
ndf = pd.read_csv(source_filename1, index_col='n')
wdf = pd.read_csv(source_filename2, index_col='language')


#==================================================
# Compute the VMS token-doubling rate
#==================================================
vms_adjacent_tokens = list(zip(vms.tklist[:-1], vms.tklist[1:]))
vms_adjacent_doubles = [k for k in vms_adjacent_tokens if (k[0]==k[1]) and ('?' not in k[0])]
n_adjacent_pairs = len(vms.tklist) - 1
vms_token_doubling_rate_per_1000 = 1000 * len(vms_adjacent_doubles) / n_adjacent_pairs


#==================================================
# Estimate τ via log-linear interpolation between n=1 and n=2
#==================================================
log_ndf = ndf.apply(np.log10)
slope_series = log_ndf.loc[2] - log_ndf.loc[1]
log_vms = np.log10(vms_token_doubling_rate_per_1000)
tau_series = 1 + (log_vms - log_ndf.loc[1]) / slope_series
tau_est = float(tau_series.drop('Dutch').mean()) # exclude Dutch outlier value


#==================================================
# Plot
#==================================================
# Set up the Figure and Axes
fig, ax = plt.subplots(figsize=(12, 6))
fig.subplots_adjust(right=0.72)
ax.set_yscale('log')
ax.set_xlim(1, 5)
ax.set_ylim(0.02, 100)

# Colors
color_map = {
    'German':  '#000000',
    'Latin':   '#a020f0',
    'English': '#2196f3',
    'Dutch':   '#FF6F00',
    'French':  '#AFE1AF',
  }

# NL data
ndf.plot(ax=ax, marker='o', linewidth=2.0,color=[color_map[c] for c in ndf.columns], clip_on=False)
for i, line in enumerate(ax.get_lines()):
    line.set_zorder(10 - i) # Set z-ordering

# Legend
ax.legend(loc='upper right', ncol=5, fontsize=9, framealpha=0.95)

# VMS doubling-rate line
vms_color = (0.8, 0, 0)
ax.axhline(y=vms_token_doubling_rate_per_1000, color=vms_color, linestyle='-', linewidth=1.0, zorder = 100)

# VMS token-doubling box
vms_sem = 0.7 # computed in tabulate_vms_doubling_rate_with_errorbars.py
vms_tk_doubling_rate_min, vms_tk_doubling_rate_max = vms_token_doubling_rate_per_1000 - vms_sem, vms_token_doubling_rate_per_1000 + vms_sem
xmin, xmax = ndf.index.min(), ndf.index.max()
ax.add_patch(Rectangle((xmin, vms_tk_doubling_rate_min), xmax-xmin, 2 * vms_sem, facecolor=vms_color, alpha=0.3, edgecolor=vms_color, linewidth=0.7, zorder=0))
vms_textstring = f'Voynich Manuscript\ntoken-doubling rate\n{vms_token_doubling_rate_per_1000:.1f} ± {vms_sem} per 1,000'
vms_txt_x, vms_txt_y = 1.02, vms_token_doubling_rate_per_1000
ax.text(vms_txt_x, vms_txt_y, vms_textstring, transform=ax.get_yaxis_transform(), va='center', ha='left', color=vms_color, fontsize=11, linespacing=1.5)

# Natural-language word-doubling box
nl_word_doubling_rate_min, nl_word_doubling_rate_max = wdf['rate_per_1000'].min(), wdf['rate_per_1000'].max()
xmin, xmax = ndf.index.min(), ndf.index.max()
ax.add_patch(Rectangle((xmin, nl_word_doubling_rate_min), xmax-xmin, nl_word_doubling_rate_max - nl_word_doubling_rate_min, facecolor='lightgray', alpha=0.3, edgecolor='black', linewidth=0.7, zorder=0))
nl_textstring = f'Natural-language\nword-doubling rate\n{nl_word_doubling_rate_min:.2f} - {nl_word_doubling_rate_max:.2f} per 1,000'
nl_txt_x, nl_txt_y = 1.02, nl_word_doubling_rate_min + (nl_word_doubling_rate_max - nl_word_doubling_rate_min)/2
ax.text(nl_txt_x, nl_txt_y, nl_textstring, transform=ax.get_yaxis_transform(), va='center', ha='left', color='black', fontsize=11, linespacing=1.5)

# Tau marker and line
ax.plot([tau_est], [vms_token_doubling_rate_per_1000], marker='o', markersize=15, markerfacecolor='none', markeredgecolor='dimgray', markeredgewidth=0.7, zorder=20)
ax.plot([tau_est, tau_est], [0.02, vms_token_doubling_rate_per_1000 * 0.82], color='black', linestyle=':', linewidth=1.5, zorder=4)
ax.text(tau_est, 0.0135, r'$\tau$', ha='center', fontsize=16)

# Format axes and ticks
ax.set_xlabel('n-gram length (letters)', fontsize=12)
ax.set_ylabel('Doublings per 1,000 n-gram pairs  (log scale)', fontsize=12)
ax.set_title('Voynich Token-Doubling Rate vs. Natural-Language n-gram Doubling Rates', fontsize=13, pad=10)
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xticklabels(['1', '2', '3', '4', '5'])
ax.tick_params(axis='x', labelsize=12)
ax.set_yticks([0.1, 1, 10, 100])
ax.set_yticklabels(['0.1', '1', '10', '100'])
ax.grid(True, which='major', linestyle='-', alpha=0.3)
ax.grid(True, which='minor', linestyle=':', alpha=0.2)


#==================================================
# Export
#==================================================
if file_export_flag:
    plt.savefig(target_filename, dpi=300, bbox_inches='tight', pad_inches=0.05)
    pdf_filename = target_filename.replace('.png', '.pdf')
    plt.savefig(pdf_filename, bbox_inches='tight', pad_inches=0.05)
    print(f'Wrote {target_filename} and {pdf_filename}')
else:
    plt.show()
