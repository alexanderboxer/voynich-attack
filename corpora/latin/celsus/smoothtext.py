'''
Smooth and export a given text: Celsus
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
input_filepath = 'Perseus_text_2007.01.0088.xml'
export_flag = 0

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read().replace('\n',' ')

Q = dict()
for i, book in enumerate(re.split('<div1 type="book".*?>', s0)[1:]):
    for chapter in re.split('<div2', book)[1:]:
        j = re.search('type="chapter" n="(.+?)"', chapter).group(1)
        for k, line in enumerate(re.split('<milestone.*?>', chapter)[1:]):
            textkey = '{}.{}.{}'.format(i+1, [j if j!='pr' else 0][0], k+1)
            Q[textkey] = line 
    
df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
fulltext0 = df0.apply(' '.join).values[0]
tags = set(re.findall('<\w+',fulltext0))

# ==============================================================================
# Text formatting 
# ==============================================================================
df = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df['textstring'] = df.textstring.apply(lambda x: re.sub('<foreign.*?</foreign>', '', x)) # remove Greek text
df['textstring'] = df.textstring.apply(lambda x: re.sub('<bibl.*?</bibl>', '', x)) # remove bibliographic citations
df['textstring'] = df.textstring.apply(lambda x: re.sub('<note.*?</note>', '', x)) # remove English notes 
df['textstring'] = df.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df['textstring'] = df.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv('celsus.csv', index = True)

