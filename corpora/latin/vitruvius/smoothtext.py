'''
Smooth and export a given text: Vitruvius
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
input_filepath = 'Perseus_text_1999.02.0072.xml'
export_flag = 0

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read().replace('\n',' ')

Q = dict()
for i, book in enumerate(re.split('<head>.*?</head>', s0)[1:]):
    for j, chapter in enumerate(re.split('<div2.*?>', book)[1:]):
        for k, line in enumerate(re.split('<div3.*?><p>', chapter)[1:]):
            textkey = '{}.{}.{}'.format(i+1, j, k+1)
            Q[textkey] = line 
    
df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
fulltext0 = df0.apply(' '.join).values[0]
tags = set(re.findall('<\w+',fulltext0))

# ==============================================================================
# Text formatting (Lat1)
# ==============================================================================
df_lat1 = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df_lat1['textstring'] = df_lat1.textstring.apply(lambda x: re.sub('<foreign.*?</foreign>', '', x)) # remove Greek text 
df_lat1['textstring'] = df_lat1.textstring.apply(lambda x: re.sub('<note.*?</note>', '', x)) # remove English notes 
df_lat1['textstring'] = df_lat1.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df_lat1['textstring'] = df_lat1.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))

fulltext_lat1 = df_lat1.apply(' '.join).values[0]
charset_lat1 = set(fulltext_lat1)

# ==============================================================================
# Text formatting (Lat1)
# ==============================================================================
df_lat0 = df_lat1.copy()

replacement_dictionary = {
    'î': 'ii', 
    'duûm': 'duorum',
    'binûm': 'binum',
    'ternûm': 'ternum',
    'quinûm': 'quinum',
    'senûm': 'senum',
    'octonûm': 'octonum',
    'denûm': 'denum',
    'quinquagenûm': 'quinquagenum',

    'sonitûm': 'sonituum',
    'angiportûm': 'angiportuum',
    'stadiûm': 'stadiorum',
    'rubrûm et nigrûm tofûm': 'rubrorum et nigrorum toforum',
    'mediûm': 'mediorum',
    'cymatiûm': 'cymatiorum',
    'intertigniûm': 'intertigniorum',
    'eûm': 'eorum',
    'porticûm': 'porticuum',
    'capitulûm': 'capitulorum',
    'digitûm': 'digitorum',
    'candelabrûm': 'candelabrorum',
    'fructûm': 'fructuum',
    'ipsûm': 'ipsorum',
    'intervallûm': 'intervallorum',
    'talentûm': 'talentum'
}

for k, v in replacement_dictionary.items():
	df_lat0['textstring'] = df_lat0.textstring.apply(lambda x: x.replace(k, v))

fulltext_lat0 = df_lat0.apply(' '.join).values[0]
charset_lat0 = set(fulltext_lat0)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df_lat1.to_csv('vitruvius_lat1.csv', index = True)
    df_lat0.to_csv('vitruvius_lat0.csv', index = True)
