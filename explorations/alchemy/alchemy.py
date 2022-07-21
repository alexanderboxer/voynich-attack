'''
Collate and categorize all sequences for a given sequence-length
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../voynpy')
from corpora import vms, vms1, vms2, caesar

# ==============================================================================
# Collate tokens and count uniques
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

    df = pd.DataFrame(data = np.array(seqlist).T) # dataframe of ngrams
    df['p'] = [len(set(k)) for k in zip(*seqlist)] # count of unique grams in set
    return df

# ==============================================================================
# Concat line numbers for reference
# ==============================================================================
def tkount(tklist, linelist, order):
    df1 = ngram(tklist, order)
    df2 = ngram(linelist, order)
    line_df = df2[0].to_frame(name = 'line')
    df = pd.concat([line_df, df1], axis = 1)
    return df

# ==============================================================================
# Create a zipped list of tokens with their line-numbers
# ==============================================================================
df0 = vms.df.astype(str)
tkdf = df0.iloc[:,3:]

linenums = ['.'.join(k) for k in zip(df0.folio, df0.par, df0.line)]
linenum_array = np.repeat(linenums, tkdf.shape[1])
tkarray = tkdf.to_numpy().flatten()
line_and_tklist = [(k[0],k[1]) for k in zip(linenum_array, tkarray) if k[1] != '$']
tklist = [k[1] for k in line_and_tklist]
linelist = [k[0] for k in line_and_tklist]

# ==============================================================================
# Generate and sequence dataframe, keep rows with the fewest unique tokens
# ==============================================================================
df8 = tkount(tklist, linelist, 8)

#df8[df8.p <= 5].to_csv('seq8.csv', index = False)

# ==============================================================================
# aba
# ==============================================================================
df3 = tkount(tklist, linelist, 3)
df3['txt'] = df3.apply(lambda X: X[0] + X[1] + X[2], axis = 1)
value_counts = df3.txt.value_counts().to_frame(name = 'n')

aba_df = df3.copy()
aba_df['aba'] = aba_df.apply(lambda X: X[0]==X[2], axis = 1)
aba_df = aba_df.merge(value_counts, left_on = 'txt', right_index = True).drop(['p','txt'], axis = 1)
aba_df = aba_df[aba_df.aba].drop('aba', axis = 1).sort_values(['n', 0, 1], ascending = [False, True, True])
#aba_df.to_csv('aba.csv', index = False)

# ==============================================================================
# abb
# ==============================================================================
abb_df = df3.copy()
abb_df['abb'] = abb_df.apply(lambda X: X[1]==X[2], axis = 1)
abb_df = abb_df.merge(value_counts, left_on = 'txt', right_index = True).drop(['p','txt'], axis = 1)
abb_df = abb_df[abb_df.abb].drop('abb', axis = 1).sort_values(['n', 0, 1], ascending = [False, True, True])
#abb_df.to_csv('abb.csv', index = False)

# ==============================================================================
# aab
# ==============================================================================
aab_df = df3.copy()
aab_df['aab'] = aab_df.apply(lambda X: X[0]==X[1], axis = 1)
aab_df = aab_df.merge(value_counts, left_on = 'txt', right_index = True).drop(['p','txt'], axis = 1)
aab_df = aab_df[aab_df.aab].drop('aab', axis = 1).sort_values(['n', 0, 1], ascending = [False, True, True])
#aab_df.to_csv('aab.csv', index = False)