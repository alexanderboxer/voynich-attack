'''
Hapax legomena
'''
# ==============================================================================
# Import
# ==============================================================================
import sys
from collections import Counter

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

# ==============================================================================
# Compute running hapax fraction
# ==============================================================================
def hapax_fraclist(token_list):
    outlist = list()
    for idx in range(len(token_list)):
        token_count = Counter(token_list[:idx + 1]).most_common()
        hapax_count = len([k for k in token_count if k[1] == 1])
        outlist.append(hapax_count / (idx + 1))
    return outlist

# ==============================================================================
# Voynich
# ==============================================================================
print('voynich')
vmspath = '../../transcription/vms.csv'
vdf = pd.read_csv(vmspath)

nullchar = '$'
tklist0 = [k for k in vdf.iloc[:,3:].fillna(nullchar).to_numpy().flatten() if k != nullchar] # 24,073 tokens
tklist = [k for k in tklist0 if not '?' in k] # 23,596 tokens

h_vms = hapax_fraclist(tklist[:10000])

# ==============================================================================
# Enochian
# ==============================================================================
print('enochian')
ms3188path = '../../corpora/enochian/ms3188.csv'
edf = pd.read_csv(ms3188path)

tklist0 = [k for k in edf.iloc[:,2:].fillna(nullchar).to_numpy().flatten() if k != nullchar] # 4079 tokens

# Separate hyphenated words into separate tokens (18 hyphenated tokens -> 39 unhyphenated tokens)
tk_splitlist = [k.split('-') for k in tklist0]
tklist = [k for splitlist in tk_splitlist for k in splitlist] # 4100 tokens


h_enoch = hapax_fraclist(tklist)

# ==============================================================================
# Caesar
# ==============================================================================
print('caesar')
caesar_filepath = '../../corpora/latin/caesar_bellogallico/caesar_bellogallico_alpha.txt'
with open(caesar_filepath, 'r') as f:
    caesar_string = f.read()

caesar_wordlist = caesar_string.split()

h_caesar = hapax_fraclist(caesar_wordlist[:10000])

# ==============================================================================
# Hamlet
# ==============================================================================
print('hamlet')
hamlet_filepath = '../../corpora/english/hamlet/hamlet_alpha.txt'
with open(hamlet_filepath, 'r') as f:
    hamlet_string = f.read()

hamlet_wordlist = hamlet_string.split()

h_hamlet = hapax_fraclist(hamlet_wordlist[:10000])

# ==============================================================================
# Hebrew
# ==============================================================================
print('torah')
heb_filepath = '../../corpora/hebrew/torah.txt'
with open(heb_filepath, 'r') as f:
    heb = f.read()

heb_wordlist = heb.split()

h_heb = hapax_fraclist(heb_wordlist[:10000])

# ==============================================================================
# Plot
# ==============================================================================

hapaxlists = [h_vms, h_enoch, h_caesar, h_hamlet, h_heb]
labels = ['voynich', 'enochian', 'caesar', 'hamlet', 'torah']

for idx in range(len(hapaxlists)):
    h = hapaxlists[idx]
    x = 1 + np.arange(len(h))
    plt.plot(x, h, label = labels[idx], zorder = 2 + len(hapaxlists) - idx)

plt.legend(loc = 'upper right')

plt.show()
