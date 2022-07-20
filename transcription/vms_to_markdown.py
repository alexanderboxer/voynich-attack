'''
Format vms.csv as a github-friendly markdown table
'''
# ==============================================================================
# Import modules
# ==============================================================================
import pandas as pd 

# ==============================================================================
# Read csv
# ==============================================================================
df = pd.read_csv('vms.csv').astype(str)

# ==============================================================================
# Format
# ==============================================================================
nullchar = '$'
df = df.replace(nullchar, '')
s = df.to_csv(sep = '|', index = False).replace('\n','|\n|') # csv to string

table_header = '|' + s.split('\n')[0]
table_formatting = '|' + ':-:|' * df.shape[1]
table_body = s.split('\n', maxsplit = 1)[1].rsplit('\n', maxsplit = 1)[0]
markdown_table = table_header + '\n' + table_formatting + '\n' + table_body

# ==============================================================================
# Description
# ==============================================================================
desc = ''
desc += '[⇦ Back](https://github.com/alexanderboxer/voynich-attack) | [Table of Contents](https://github.com/alexanderboxer/voynich-attack) | Next ⇨\n\n'
desc += 'A new, freely shareable csv [transcription](https://github.com/alexanderboxer/voynich-attack/blob/main/transcription/vms.csv) of all extant pages of Voynich block text\n\n'

markdown_table = desc + markdown_table

# ==============================================================================
# Export
# ==============================================================================
with open('README.md', 'w') as f:
	f.write(markdown_table)
