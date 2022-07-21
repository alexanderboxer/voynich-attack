'''
doublets
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
def doublets(token_list):
    ztk = list(zip(token_list[:-1], token_list[1:]))
    return np.cumsum([1 if k[0] == k[1] else 0 for k in ztk])

# ==============================================================================
# Voynich
# ==============================================================================
print('voynich')
vmspath = '../../transcription/vms.csv'
vdf = pd.read_csv(vmspath)

nullchar = '$'
tklist  = [k for k in vdf.iloc[:,3:].fillna(nullchar).to_numpy().flatten() if k != nullchar] # 24,073 tokens
#tklist = [k for k in tklist0 if not '?' in k] # 23,596 tokens

vdubs = doublets(tklist)

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


edubs = doublets(tklist)

# ==============================================================================
# Caesar
# ==============================================================================
print('caesar')
caesar_filepath = '../../corpora/latin/caesar_bellogallico/caesar_bellogallico_alpha.txt'
with open(caesar_filepath, 'r') as f:
    caesar_string = f.read()

caesar_wordlist = caesar_string.split()

cdubs = doublets(caesar_wordlist)

# ==============================================================================
# Hamlet
# ==============================================================================
print('hamlet')
hamlet_filepath = '../../corpora/english/hamlet/hamlet_alpha.txt'
with open(hamlet_filepath, 'r') as f:
    hamlet_string = f.read()

hamlet_wordlist = hamlet_string.split()

hdubs = doublets(hamlet_wordlist)

# ==============================================================================
# Catounet gascoun
# ==============================================================================
print('occitan')
text_filepath = '../../corpora/occitan/catounet_gascoun/catounet_gascoun_alpha.txt'
with open(text_filepath, 'r') as f:
    textstring = f.read()

wordlist = textstring.split()

odubs = doublets(wordlist)

# ==============================================================================
# Hebrew
# ==============================================================================
print('torah')
heb_filepath = '../../corpora/hebrew/torah.txt'
with open(heb_filepath, 'r') as f:
    heb = f.read()

heb_wordlist = heb.split()

tdubs = doublets(heb_wordlist)

# ==============================================================================
# Plot
# ==============================================================================

dublists = [vdubs, edubs, cdubs, hdubs, odubs, tdubs]
labels = ['voynich', 'enochian', 'caesar', 'hamlet', 'torah', 'occitan']

for idx in range(len(dublists)):
    d = dublists[idx]
    x = 1 + np.arange(len(d))
    plt.plot(x, d, label = labels[idx], zorder = 2 + len(dublists) - idx)

plt.legend(loc = 'upper right')

plt.xlim([0,15000])

plt.show()
