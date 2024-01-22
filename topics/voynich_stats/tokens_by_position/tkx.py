'''
Voynich tokens by position
'''
# ==============================================================================
# Imports
# ==============================================================================
import re
from collections import Counter
import pandas as pd 

import sys
sys.path.insert(0, '../../../voynpy')
from corpora import plants, fems, stars

# ==============================================================================
# Function: smv
# ==============================================================================
def voypar(voynich_dataframe, window, backwards = False):
    df = voynich_dataframe.copy()
    df['tks'] = df.iloc[:,3:].apply(lambda X: ';'.join(X), axis = 1)
    df = df.groupby(['folio','par']).agg({'tks': lambda x: ';'.join(x)})

    if backwards:
        df['tks'] = df['tks'].apply(lambda x: [k for k in x.split(';') if k != '$'][::-1])
        token_prefix = 'z' 
    else:
        df['tks'] = df['tks'].apply(lambda x: [k for k in x.split(';') if k != '$'])
        token_prefix = 't'
    
    for i in range(window):
        df['{}{}'.format(token_prefix, i+1)] = df.tks.apply(lambda x: x[i] if len(x) > i else '$')
    
    df = df.drop('tks', axis = 1).reset_index()
    df['side'] = [re.sub('[0-9]','',k) for k in df.folio]
    df['folio'] = [int(re.sub('[^0-9]','',k)) for k in df.folio]
    collist = ['folio','side','par'] + [k for k in df.columns if k[0]==token_prefix]
    df = df[collist]
    df = df.sort_values(['folio','side','par']).reset_index(drop=True)

    return df

# ==============================================================================
# function: ngram
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
    ndf['gram'] = ['-'.join([*k]) for k in ndf.gram]
    ndf = ndf.sort_values('n', ascending = False).reset_index(drop = True)
    nsum = ndf.n.sum()
    ndf['pct'] = ['{:.1f}'.format(round(100*k/nsum, 1)) for k in ndf.n]
    return ndf


# ==============================================================================
# function: tokens by position
# ==============================================================================
def tokens_by_position(voynich_dataframe, window, depth):
    vmsdf = voypar(voynich_dataframe, window, backwards = False)
    smvdf = voypar(voynich_dataframe, window, backwards = True)
    tkxdf = pd.DataFrame()
    pctdf = pd.DataFrame()
    nndf = pd.DataFrame()
    for i in range(1, window + 1):
        tkxdf['a{}'.format(i)] = ngram([k for k in vmsdf['t{}'.format(i)] if k != '$'], 1).gram.iloc[:depth]
        tkxdf['z{}'.format(i)] = ngram([k for k in smvdf['z{}'.format(i)] if k != '$'], 1).gram.iloc[:depth]
        pctdf['a{}'.format(i)] = ngram([k for k in vmsdf['t{}'.format(i)] if k != '$'], 1).pct.iloc[:depth]
        pctdf['z{}'.format(i)] = ngram([k for k in smvdf['z{}'.format(i)] if k != '$'], 1).pct.iloc[:depth]
        nndf['a{}'.format(i)] = ngram([k for k in vmsdf['t{}'.format(i)] if k != '$'], 1).n.iloc[:depth]
        nndf['z{}'.format(i)] = ngram([k for k in smvdf['z{}'.format(i)] if k != '$'], 1).n.iloc[:depth]

    collist = ['a{}'.format(k) for k in range(1, window + 1)] + ['z{}'.format(k) for k in range(1, window + 1)][::-1]
    return tkxdf[collist], pctdf[collist], nndf[collist] 

# ==============================================================================
# Voynich sections
# ==============================================================================
voynich_dataframe = plants.df
tkxdf, pctdf, nndf = tokens_by_position(voynich_dataframe, 10, 5)
parstats_df = pd.DataFrame()
for col in list(tkxdf.columns):
    parstats_df[col] = ['**{}**<br><sub>n={}</sub><br><sub>{}%</sub>'.format(k[0],k[2],k[1]) for k in zip(tkxdf[col], pctdf[col], nndf[col])]
plants_parstats_df = parstats_df

voynich_dataframe = fems.df
tkxdf, pctdf, nndf = tokens_by_position(voynich_dataframe, 10, 5)
parstats_df = pd.DataFrame()
for col in list(tkxdf.columns):
    parstats_df[col] = ['**{}**<br><sub>n={}</sub><br><sub>{}%</sub>'.format(k[0],k[2],k[1]) for k in zip(tkxdf[col], pctdf[col], nndf[col])]
fems_parstats_df = parstats_df

voynich_dataframe = stars.df
tkxdf, pctdf, nndf = tokens_by_position(voynich_dataframe, 10, 5)
parstats_df = pd.DataFrame()
for col in list(tkxdf.columns):
    parstats_df[col] = ['**{}**<br><sub>n={}</sub><br><sub>{}%</sub>'.format(k[0],k[2],k[1]) for k in zip(tkxdf[col], pctdf[col], nndf[col])]
stars_parstats_df = parstats_df

# ==============================================================================
# Convert to markdown
# ==============================================================================
def dataframe_to_markdown(dataframe):
    s = dataframe.to_csv(sep = '|', index = False).replace('\n','|\n|')
    table_header = '|' + s.split('\n')[0]
    table_formatting = '|' + ':-:|' * dataframe.shape[1]
    table_body = s.split('\n', maxsplit = 1)[1].rsplit('\n', maxsplit = 1)[0]
    markdown_table = table_header + '\n' + table_formatting + '\n' + table_body
    return markdown_table

markdown_table1 = dataframe_to_markdown(plants_parstats_df)
markdown_table2 = dataframe_to_markdown(fems_parstats_df)
markdown_table3 = dataframe_to_markdown(stars_parstats_df)

# ==============================================================================
# sription
# ==============================================================================
s = ''
s += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/voynich_stats/2tks) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | [Next ⇨](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/biblio)\n\n'
s += '## Voynich Positional Statistics \n\n'
s += 'Text text text.'
s += '\n\n'
s += '### 1. Voynich Section: Plants\n'
s += 'f1v - f57r; f87r - f102vb (335 paragraphs)\n\n'
s += markdown_table1
s += '\n\n'
s += '### 2. Voynich Section: Femmes\n'
s += 'f75r - f84v (108 paragraphs)\n\n'
s += markdown_table2
s += '\n\n'
s += '### 3. Voynich Section: Stars\n'
s += 'f103r - f116r (307 paragraphs)\n\n'
s += markdown_table3



# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(s)