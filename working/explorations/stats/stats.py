'''
Basic Voynich stats
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd
from collections import Counter

import sys
sys.path.insert(0, '../../voynpy')
from corpora import vms, vms1, vms2, plants1, plants2, plants, fems, stars, simp1, caesar

# ==============================================================================
# ngram 
# ==============================================================================
def ngram(gramlist, order):
    order = max([1, order])
    N = len(gramlist)
    seqlist = list()
    for i in range(order):
        start_index = i
        stop_index = N + 1 - order + i
        seq = gramlist[start_index: stop_index]
        seqlist.append(seq)
    ndf = pd.DataFrame.from_dict(Counter(zip(*seqlist)), orient = 'index').reset_index()
    ndf.columns = ['gram', 'n']
    ndf['gram'] = [' - '.join([*k]) for k in ndf.gram]
    ndf = ndf.sort_values('n', ascending = False).reset_index(drop = True)
    nsum = ndf.n.sum()
    ndf['pct'] = ['{:.2f}'.format(100*k/nsum) for k in ndf.n]
    return ndf

# ==============================================================================
# Things
# ==============================================================================
tkmod = [k for k in plants1.tklist if '?' not in k]

ndf = ngram(tkmod, 1)