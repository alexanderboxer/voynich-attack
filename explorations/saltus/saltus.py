'''
Search for simple hops
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
df2 = tkount(tklist, linelist, 2)
df2['diff'] = [sorted(list(set(k[0].split(',')) ^ set(k[1].split(',')))) for k in zip(df2[0],df2[1])]

# add-1
hop1df = df2[df2['diff'].apply(len) == 1].drop('p', axis = 1).copy()
hop1df['diff'] = hop1df['diff'].apply(lambda x: x[0])
add1df = hop1df[ hop1df.apply(lambda X: abs(len(X[0].split(',')) - len(X[1].split(','))) == 1, axis = 1) ]
add1df = add1df.merge(add1df['diff'].value_counts().to_frame('n'), how = 'left', left_on = 'diff', right_index = True).reset_index()
add1df.rename(columns = {'diff': 'add'}, inplace = True)
add1df = add1df.sort_values(['n', 'index'], ascending = [False, True]).drop('index', axis = 1)
#add1df.to_csv('add1.csv', index = False)

# swap-1
swap1df = df2[ df2.apply(lambda X: len(X[0].split(',')) == len(X[1].split(',')), axis = 1) ].drop(['p','diff'], axis = 1).copy()
swap1df['n_swaps'] = swap1df.apply(lambda X: np.sum(~(np.array(X[0].split(',')) == np.array(X[1].split(',')))), axis = 1)
swap1df = swap1df[swap1df.n_swaps == 1].drop('n_swaps', axis = 1)
swap1df['a'] = [set(k[0].split(',')).difference(set(k[1].split(','))) for k in zip(swap1df[0], swap1df[1])]
swap1df['a'] = [list(k)[0] if len(k) > 0 else '$' for k in swap1df['a']]
swap1df['b'] = [set(k[1].split(',')).difference(set(k[0].split(','))) for k in zip(swap1df[0], swap1df[1])]
swap1df['b'] = [list(k)[0] if len(k) > 0 else '$' for k in swap1df['b']]
swap1df['swap'] = ['{} → {}'.format(k[0], k[1]) for k in zip(swap1df['a'], swap1df['b'])]
swap1df.drop(['a','b'], axis = 1, inplace = True)
swap1df = swap1df.merge(swap1df['swap'].value_counts().to_frame('n'), how = 'left', left_on = 'swap', right_index = True).reset_index()
n2df = swap1df.groupby(['swap',0]).count()['n'].to_frame().reset_index().rename(columns = {'n': 'n2'})
swap1df = swap1df.merge(n2df, how = 'left', on = ['swap',0])
swap1df = swap1df.sort_values(['n','n2','swap','index'], ascending = [False, False, True, True]).drop('index', axis = 1)
swap1df[['?' not in k for k in swap1df.swap]].reset_index(drop = True, inplace = True)
#swap1df.to_csv('swap1.csv', index = False)