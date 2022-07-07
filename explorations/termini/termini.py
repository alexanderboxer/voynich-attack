'''
Collate and sort paragraph-starting tokens
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../voynpy')
from corpora import vms, vms1, vms2

# ==============================================================================
# Collate and sort paragraph-starting tokens
# ==============================================================================
df0 = vms.df.astype(str)

idx1s = df0[df0.line == '1'].index
terminidxs = [(k-1) for k in idx1s if k > 0]
tdf = df0.loc[terminidxs].copy()
tdf['line'] = ['.'.join(k) for k in zip(tdf.folio, tdf.par, tdf.line)]
tdf['coda'] = tdf.iloc[:,3:].apply(lambda X: ';'.join(X), axis = 1)
tdf = tdf[['line','coda']].copy()
tdf['coda'] = tdf.coda.apply(lambda x: [''.join(k) for k in x.split(';') if k != '$'])
tdf['coda'] = tdf.coda.apply(lambda x: ['$','$','$'] + x) # padd with nullchars
tdf['d-3'] = tdf.coda.apply(lambda x: x[-3])
tdf['d-2'] = tdf.coda.apply(lambda x: x[-2])
tdf['d-1'] = tdf.coda.apply(lambda x: x[-1])
tdf['s321'] = tdf.apply(lambda X: set(','.join([X['d-3'], X['d-2'], X['d-1']]).split(',')), axis = 1)
tdf = tdf[tdf.s321.apply(len) > 1]
zdf = tdf[['line','d-3','d-2','d-1']].copy().reset_index(drop = True)

yzz = zdf[zdf.apply(lambda X: X['d-2'] == X['d-1'], axis = 1)].copy()
yzz['pattern'] = 'yzz'

yyz = zdf[zdf.apply(lambda X: X['d-3'] == X['d-2'], axis = 1)].copy()
yyz = yyz[yyz['d-2'] != '$']
yyz['pattern'] = 'yyz'

zyz = zdf[zdf.apply(lambda X: X['d-3'] == X['d-1'], axis = 1)].copy()
zyz['pattern'] = 'zyz'

termini_df = pd.concat([yzz, yyz, zyz], ignore_index = True)
termini_df.to_csv('termini.csv', index = False)