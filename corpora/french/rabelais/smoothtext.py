'''
Smooth and export a given text: Pantagruel + Gargantua
'''
# ==============================================================================
# Import modules
# ==============================================================================
import re 
import sys 
import html
import pandas as pd

# ==============================================================================
# Paths
# ==============================================================================
input_filepath = 'rabelais_combo.txt'
export_flag = 1

# ==============================================================================
# Read text 
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read().lower()

# ==============================================================================
# Smooth and convert to dataframe
# ==============================================================================
nonalpha_keepers = ['.', '!', ';', '?', ':', '&']

s1 = re.sub('-\n', '', s0) # reconnect line-broken words
s2 = re.sub('\n', ' ', s1) # convert all other line-breaks to whitespace
s3 = ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in s2.split()])

punctuation_splits = re.split('([\.!\?])\s', s3)
txt = [k.strip() for k in punctuation_splits[::2]]
punctuation = punctuation_splits[1::2] + ['']
textstring_list = [''.join(k) for k in zip(txt, punctuation)]
df0 = pd.DataFrame(textstring_list, columns = ['textstring'])

# ==============================================================================
# Export 1
# ==============================================================================
'''
if export_flag:
    df0.to_csv('rabelais_parsed_firstpass.csv', index = True)
'''

# ==============================================================================
# Read text 2
# ==============================================================================
df = pd.read_csv('rabelais.csv')
df.columns = ['op','chapter','line','textstring']
df.textstring = df.textstring.apply(lambda x: x.strip())

# ==============================================================================
# Export 2
# ==============================================================================
if export_flag:
    df.to_csv('rabelais.csv', index = False)
