'''
Smooth and export a given text: Simplicissimus
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
input_filepath = 'grimmelshausen_simplicissimus_1669.TEI-P5.xml'
export_flag = 0

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = html.unescape(f.read())

Q = dict()
Q[0.0] = ' '.join(re.findall('<title type=.*?>([\s\S]*?)</title>',s0)) # extract the title directly
for i, book in enumerate(re.split('<div n="1">', s0)[1:]):
    for j, chapter in enumerate(re.split('<div n="2">', book)):
        textkey = '{}.{}'.format(i+1, j)
        Q[textkey] = chapter
    
df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
fulltext0 = df0.apply(' '.join).values[0]
tags = set(re.findall('<\w+',fulltext0))

# ==============================================================================
# Text formatting 
# ==============================================================================
df = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df['textstring'] = df.textstring.apply(lambda x: re.sub('<fw.*?</fw>', '', x)) # remove all header/footer/catch text between <fw> tags 
df['textstring'] = df.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df['textstring'] = df.textstring.apply(lambda x: re.sub('-\n', '', x)) # reconnect line-broken words
df['textstring'] = df.textstring.apply(lambda x: re.sub('\n', ' ', x)) # convert all other line-breaks to whitespace
df['textstring'] = df.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))  
df['textstring'] = df.textstring.apply(lambda x: re.sub('\s[\.\,!\?:]\s', ' ', x)) 

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv('simplicissimus.csv', index = True)

