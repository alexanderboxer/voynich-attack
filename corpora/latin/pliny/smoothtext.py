'''
Smooth and export a given text: Pliny
'''
# ==============================================================================
# Import modules
# ==============================================================================
import re
import sys 
import pandas as pd

# ==============================================================================
# Paths
# ==============================================================================
input_filepath = 'Perseus_text_1999.02.0138.xml'
export_flag = 0

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read().replace('\n',' ')

Q = dict()
for i, book in enumerate(re.split('<div0 type="book".*?>', s0)[1:]):
    for j, chapter in enumerate(re.split('<div1.*?>\s*<milestone.*?>', book)[1:]):
        textkey = '{}.{}'.format(i, j+1)
        Q[textkey] = chapter 
    
df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
fulltext0 = df0.apply(' '.join).values[0]
tags = set(re.findall('<\w+',fulltext0))

# ==============================================================================
# Text formatting 
# ==============================================================================
df = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df['textstring'] = df.textstring.apply(lambda x: re.sub('<foreign.*?</foreign>', '', x)) # remove Greek text
df['textstring'] = df.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df['textstring'] = df.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv('pliny_lat0.csv', index = True)

