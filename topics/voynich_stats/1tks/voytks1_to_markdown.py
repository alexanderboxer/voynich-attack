'''
Voynich tokens
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
df = vms.tkdf().astype(str)
df = df[df.gram.apply(lambda x: '?' not in x)].reset_index(drop = True)
df['rank'] = 1 + df.index
df = df.set_index('rank').reset_index().rename(columns = {'pct':'%'})
df['n'] = df['n'].apply(lambda x: '{:,}'.format(int(x)))
df = df.iloc[:1000]

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
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/voynich_stats/2grams) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | [Next ⇨](https://github.com/alexanderboxer/voynich-attack/tree/main/topics/voynich_stats/2grams)\n\n'
desc += '## Voynich Token Frequencies (top 1,000) \n\n'
desc += 'Our Voynich [transcription](https://github.com/alexanderboxer/voynich-attack/tree/main/transcription) consists of 33,669 word-like units.'
desc += ' These units are unlikely to represent words, however. More plausibly, they may encode sub-word units like bigrams, trigrams, or individual letters.'
desc += ' For this reason, we refer to them by the more generic term “tokens.”'
desc += ' In many instances, it is extremely difficult to determine whether a sequence of characters should be grouped into one token or split into several tokens. '
desc += ' Consequently, there is an unavoidable element of subjectivity in all Voynich transcriptions, including this one.'
desc += '\n\n'

markdown_text = desc + markdown_table

# ==============================================================================
# Write
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_text)
