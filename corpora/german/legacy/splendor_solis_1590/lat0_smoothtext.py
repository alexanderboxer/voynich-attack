'''
Smooth and export a given text: Splendor Solis
'''
# ==============================================================================
# Import modules
# ==============================================================================
import os
import re
import sys 
import pandas as pd

# ==============================================================================
# Paths
# ==============================================================================
basename = 'splendor_solis'

input_directory = '.'
output_directory = '.'
input_filepath = os.path.join(input_directory, basename + '_edited.txt')
lat0_filepath = os.path.join(output_directory, basename + '_lat0.csv')

export_flag = 0

# ==============================================================================
# Read
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read()

# ==============================================================================
# Smooth
# ==============================================================================
s1 = s0.lower().replace('\n', ' ').replace('- ','')

# punctuation cleanup
nonalpha_keepers = ['.', '!', ';', '?', ':', '/']
pagebreaks = ['[',']']
s2 = ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers + pagebreaks]) for word in s1.split()])

# split into pages
pagelist = s2.split('[]')[1:]
pagelist = [' '.join(k.split()) for k in pagelist] # map all whitespaces to a single whitespace

# dataframe
df = pd.DataFrame(pagelist, columns = ['textstring'])

# ==============================================================================
# Split pages into sentences
# ==============================================================================
df1 = df.copy()
df1['textsplit'] = [re.split('[\.\!\;\?\:]',k) for k in df1.textstring]

txtlist = []
idxlist = []
for i in range(df1.shape[0]):
    idx = df1.index[i]
    txtsplit = [k for k in df1.textsplit.iloc[i] if len(k) > 0]
    txtlist += txtsplit 
    idxlist += ['{}.{}'.format(idx, k+1) for k in range(len(txtsplit))]

df2 = pd.DataFrame(index = idxlist, data = txtlist, columns = ['textstring'])

# ==============================================================================
# Split sentences into phrases
# ==============================================================================
df3 = df2.copy()
df3['textsplit'] = [re.split('/',k) for k in df3.textstring]

txtlist = []
idxlist = []
for i in range(df3.shape[0]):
    idx = df3.index[i]
    txtsplit = [k for k in df3.textsplit.iloc[i] if len(k) > 0]
    txtlist += txtsplit 
    idxlist += ['{}.{}'.format(idx, k+1) for k in range(len(txtsplit))]

df4 = pd.DataFrame(index = idxlist, data = txtlist, columns = ['textstring'])
df4['textstring'] = [k.strip() for k in df4.textstring]

# ==============================================================================
# Latin-0 formatting
# ==============================================================================
# textstring
charset1 = set(''.join([k for k in df4.textstring]))

replacement_dict = {
    'ß': 'ss',
    'â': 'ae',
    'ä': 'ae',
    'æ': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'ÿ': 'j',
    'ͻ': 'us',
}

def rpl(s):
    for k, v in replacement_dict.items():
        s = s.replace(k, v)
    return s
        
df4['textstring'] = [rpl(k) for k in df4.textstring]
df4.index.name = 'idx'

charset = set(''.join([k for k in df4.textstring]))

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df4.to_csv(lat0_filepath)
