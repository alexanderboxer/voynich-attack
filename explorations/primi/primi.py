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
df0 = vms2.df.astype(str)

df1 = df0[df0.line == '1'].copy()
df1['line'] = ['.'.join(k) for k in zip(df1.folio, df1.par, df1.line)]
df1 = df1[['line','t1','t2','t3']]
df1 = df1.merge(df1['t1'].value_counts().to_frame('n'), how = 'left', left_on = 't1', right_index = True).reset_index()
df1 = df1.sort_values(['n', 't1', 'index'], ascending = [False, True, True]).drop('index', axis = 1)

df1.to_csv('primi.csv', index = False)