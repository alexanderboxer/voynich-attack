'''
Voynich 2-grams
'''
# ==============================================================================
# Imports
# ==============================================================================
import pandas as pd 

import sys
sys.path.insert(0, '../../../voynpy')
from corpora import vms

# ==============================================================================
# Dataframe
# ==============================================================================
df = vms.chardf(2).astype(str)
df = df[df.gram.apply(lambda x: '?' not in x)].reset_index(drop = True)
df['rank'] = 1 + df.index
df = df.set_index('rank').reset_index().rename(columns = {'pct':'%'})
df['n'] = df['n'].apply(lambda x: '{:,}'.format(int(x)))

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
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/voynich_stats/1grams) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | Next ⇨\n\n'
desc += '## Voynich 2-gram Frequencies\n\n'

markdown_text = desc + markdown_table

# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_text)
