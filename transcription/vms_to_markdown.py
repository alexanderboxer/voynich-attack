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
df = pd.read_csv('vms.csv')

# ==============================================================================
# Format
# ==============================================================================
df['line'] = [k if pd.isna(k) else str(int(k)) for k in df.line] # convert floats -> ints -> strings 
s = df.to_csv(sep = '|', index = False).replace('\n','|\n|') # csv to string

table_header = '|' + s.split('\n')[0]
table_formatting = '|' + ':-:|' * df.shape[1]
table_body = s.split('\n', maxsplit = 1)[1].rsplit('\n', maxsplit = 1)[0]
markdown_table = table_header + '\n' + table_formatting + '\n' + table_body

# ==============================================================================
# Export
# ==============================================================================
with open('vms.md', 'w') as f:
	f.write(markdown_table)
