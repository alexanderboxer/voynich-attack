'''
German 1-words
'''
# ==============================================================================
# Imports
# ==============================================================================
import pandas as pd 

import sys
sys.path.insert(0, '../../../voynpy')
from corpora import simp, kuche, promptuarium, german

# ==============================================================================
# Combine dataframes
# ==============================================================================
nmax = 1000
alldf = german.tkdf().iloc[:nmax]
df1 = simp.tkdf().iloc[:nmax]
df2 = kuche.tkdf().iloc[:nmax]
df3 = promptuarium.tkdf().iloc[:nmax]

dataframe_list = [alldf, df1, df2, df3]
dataframe_namelist = ['all texts', 'Simplicissimus', 'Kuchemaistrey', 'Promptuarium medicinae']

df = pd.DataFrame()
for qdf, name in zip(dataframe_list, dataframe_namelist):
    qdf.rename(columns = {'gram': name, 'pct': '%'}, inplace = True)
    qdf['n'] = qdf['n'].apply(lambda x: '{:,}'.format(int(x)))
    qdf['%'] = qdf['%'].astype(str).apply(lambda x: x if len(x) > 0 else '')
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
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/german_stats/2grams) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | [Next ⇨](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/german_stats/2words)\n\n'
desc += '## German Word Frequencies (Top 1,000)\n\n'

markdown_text = desc + markdown_table

# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_text)
