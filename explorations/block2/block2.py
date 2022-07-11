'''
non-overlapping ngrams
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd
from collections import Counter

import sys
sys.path.insert(0, '../voynpy')
from corpora import chaucer, wycliffe, caesar, plants1, plants2, plants

# ==============================================================================
# Non overlapping bigrams
# ==============================================================================
def b2(tklist):
    tklist2 = [k if len(k) % 2 == 0 else k + '$' for k in tklist]
    a2 = np.array(list(''.join(tklist2)))
    a2 = a2.reshape(-1,2)
    l2 = [''.join(k) for k in a2]

    ndf = pd.DataFrame.from_dict(Counter(l2), orient = 'index').reset_index()
    ndf.columns = ['gram', 'n']
    ndf = ndf.sort_values('n', ascending = False).reset_index(drop = True)
    nsum = ndf.n.sum()
    ndf['pct'] = ['{:.2f}'.format(100*k/nsum) for k in ndf.n]

    return ndf

cdf = b2(chaucer.tklist)
wdf = b2(wycliffe.tklist)
ldf = b2(caesar.tklist)


