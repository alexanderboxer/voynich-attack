'''
Latin 2-grams
'''
# ==============================================================================
# Imports
# ==============================================================================
import pandas as pd 

import sys
sys.path.insert(0, '../../../voynpy')
from corpora import caesar, vitruvius

# ==============================================================================
# Combine dataframes
# ==============================================================================
df1 = caesar.chardf(2)
df2 = vitruvius.chardf(2)
dataframe_list = [df1, df2]
dataframe_namelist = ['Caesar', 'Vitruvius']

tot_df = pd.concat(dataframe_list, axis = 0).groupby('gram').agg({'n': 'sum'}).sort_values('n', ascending = False).reset_index()
N = tot_df.n.sum()
tot_df['gram'] = tot_df['gram'].apply(lambda x: x.replace('-',''))
tot_df['%'] = tot_df['n'].apply(lambda x: '{:.2f}'.format(100 * x / N))
tot_df['n'] = tot_df['n'].apply(lambda x: '{:,}'.format(x))
tot_df['✧'] = ''

df = tot_df.rename(columns = {'gram': 'all texts'})
for qdf, name in zip(dataframe_list, dataframe_namelist):
    qdf = qdf.reindex(range(df.shape[0]), fill_value = '')
    qdf['gram'] = qdf['gram'].apply(lambda x: x.replace('-',''))
    qdf.rename(columns = {'gram': name}, inplace = True)
    qdf['n'] = qdf['n'].apply(lambda x: '{:,}'.format(int(x)) if x != '' else '')
    qdf['%'] = qdf.pct.astype(str).apply(lambda x: x if len(x) > 0 else '')
    qdf.drop('pct', axis = 1, inplace = True)
    qdf['✧'] = ''
    df = pd.concat([df, qdf], axis = 1)

df = df.iloc[:,:-1]
df['rank'] = df.index + 1
df = df.set_index('rank').reset_index()

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

markdown_table = dataframe_to_markdown(df)

# ==============================================================================
# Description
# ==============================================================================
desc = ''
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/latin_stats/1grams) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | [Next ⇨](https://github.com/alexanderboxer/voynich-attack)\n\n'
desc += '## Latin Bigram Frequencies\n\n'

markdown_text = desc + markdown_table

# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_text)
