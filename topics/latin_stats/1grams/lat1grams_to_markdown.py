'''
Voynich 1-grams
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
df = vms.chardf().astype(str)
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
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/biblio) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | [Next ⇨](https://github.com/alexanderboxer/voynich-attack)\n\n'
desc += '## Latin Letter Frequencies\n\n'
desc += 'Our Voynich [transcription](https://github.com/alexanderboxer/voynich-attack/tree/main/transcription) consists of 147,485 comma-separated characters.'
desc += ' Of these, about 0.5% (756) are marked with a `?` to indicate an unclear or ambiguous reading.'
desc += ' The remaining character-set consists of roughly 21 “standard” and another 15 or so non-standard characters.\n\n'

markdown_text = desc + markdown_table

# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_text)
