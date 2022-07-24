'''
Smooth and export a given text: Caesar
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
input_filepath = 'Perseus_text_1999.02.0002.xml'
output_filepath = 'caesar_lat0.csv'
export_flag = 0

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read()

Q = dict()
for i, book in enumerate(re.split('<head>.*</head>', s0)[1:]):
    for j, chapter in enumerate(re.split('<p><milestone.*?>', book)[1:]):
        for k, line in enumerate(re.split('<milestone.*?>', chapter)[1:]):
            textkey = '{}.{}.{}'.format(i+1, j+1, k+1)
            Q[textkey] = line 
    
df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])

# ==============================================================================
# Text formatting
# ==============================================================================
df = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df['textstring'] = df.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df['textstring'] = df.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv(output_filepath, index = True)
