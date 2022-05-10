'''
Hapax legomena
'''
# ==============================================================================
# Import
# ==============================================================================
from collections import Counter

import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

# ==============================================================================
# Load
# ==============================================================================
ms3188path = '../../corpora/enochian/ms3188.csv'
edf = pd.read_csv(ms3188path)

# ==============================================================================
# Token list
# ==============================================================================
nullchar = '$'
tklist0 = [k for k in edf.iloc[:,2:].fillna(nullchar).to_numpy().flatten() if k != nullchar] # 4079 tokens

# Separate hyphenated words into separate tokens (18 hyphenated tokens -> 39 unhyphenated tokens)
tk_splitlist = [k.split('-') for k in tklist0]
tklist = [k for splitlist in tk_splitlist for k in splitlist] # 4100 tokens

# ==============================================================================
# Tokens ordered by frequency
# ==============================================================================
tkounter = Counter(tklist).most_common()
tkdf = pd.DataFrame.from_dict(tkounter).rename(columns = {0:'token', 1:'n'})

hapax_fraclist = list()
for idx in range(len(tklist)):
    tkount = Counter(tklist[:idx + 1]).most_common()
    hapax_count = len([k for k in tkount if k[1] == 1])
    hapax_fraclist.append(hapax_count / (idx + 1))

# ==============================================================================
# Plot
# ==============================================================================
xx = 1 + np.arange(len(hapax_fraclist))

tstart = 0
plt.plot(xx[tstart:], hapax_fraclist[tstart:])

plt.show()