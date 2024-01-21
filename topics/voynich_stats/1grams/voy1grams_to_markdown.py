'''
Voynich 1-grams
'''
# ==============================================================================
# Imports
# ==============================================================================
import pandas as pd
from collections import Counter 

import sys
sys.path.insert(0, '../../../voynpy')
from corpora import vms, plants1, fems, stars

# ==============================================================================
# Function: ngram
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
    ndf['%'] = [100*k/nsum for k in ndf.n]
    return ndf

# ==============================================================================
# Dataframe
# ==============================================================================
df = ngram([k for k in vms.charlist if '?' not in k], 1)
df['n'] = df['n'].apply(lambda x: '{:,}'.format(x))
df['%'] = ['{:.2f}'.format(round(k,2)) for k in df['%']]
df['✧'] = ''
df['rank'] = [1 + k for k in range(df.shape[0])]
df = df[['rank','gram','n','%','✧']].rename(columns = {'gram': 'all'})

subcorpus_list = [plants1, fems, stars]
subcorpus_namelist = ['plants<br><sub>f1v-f57r</sub>', 'fems<br><sub>f75r-f84v</sub>', 'stars<br><sub>f103r-f116r</sub>']

for subcorpus, col_name in zip(subcorpus_list, subcorpus_namelist):
    qdf = ngram([k for k in subcorpus.charlist if '?' not in k], 1)
    qdf['n'] = qdf['n'].apply(lambda x: '{:,}'.format(x))
    qdf['%'] = ['{:.2f}'.format(round(k,2)) for k in qdf['%']]
    qdf['✧'] = ''
    qdf = qdf.rename(columns = {'gram':col_name})
    df = pd.concat([df, qdf], axis = 1)
df = df.iloc[:,:-1]

# ==============================================================================
# Convert to markdown
# ==============================================================================
def dataframe_to_markdown(dataframe):
    s = dataframe.to_csv(sep = '|', index = False).replace('\n','|\n|')
    table_header = '|' + s.split('\n')[0]
    table_formatting = '|' + ':-:|' * df.shape[1]
    table_body = s.split('\n', maxsplit = 1)[1].rsplit('\n', maxsplit = 1)[0]
    markdown_table = table_header + '\n' + table_formatting + '\n' + table_body
    return markdown_table

markdown_table = dataframe_to_markdown(df)

# ==============================================================================
# Description
# ==============================================================================
desc = ''
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/transcription) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | [Next ⇨](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/voynich_stats/2grams)\n\n'
desc += '## Voynich Character Frequencies\n\n'
desc += 'Our Voynich [transcription](https://github.com/alexanderboxer/voynich-attack/tree/main/transcription) consists of 147,485 comma-separated characters.'
desc += ' Of these, about 0.5% (756) are marked with a `?` to indicate an unclear or ambiguous reading.'
desc += ' The remaining character-set consists of roughly 21 “standard” and another 15 or so non-standard characters.\n\n'

markdown_text = desc + markdown_table

# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_text)
