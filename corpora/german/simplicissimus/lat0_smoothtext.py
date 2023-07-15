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
export_flag = 1

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
# Split chapters into sentences
# ==============================================================================
df1 = df.copy()
df1['textstring'] = [re.sub('\.','',k,1) for k in df1.textstring]
df1['textstring'].iloc[:2] = df['textstring'].iloc[:2]
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
# Latin-0 formatting
# ==============================================================================
df2['textstring'] = [k.strip() for k in df2.textstring]

replacement_dict = {
    'ß': 'ss',
    'æ': 'ae',
    'â': 'a',
    'ä': 'ae',
    'å': 'a',
    'è': 'e',
    'ë': 'e',
    'ô': 'o',
    'ü': 'ue',
    'œ': 'e',
    'ů': 'u',
    'ſ': 's',
    ' ꝛc': ' etc',
    'ꝛ': 'r',
}

def rpl(s):
    for k, v in replacement_dict.items():
        s = s.replace(k, v)
    return s
        
df2['textstring'] = [rpl(k) for k in df2.textstring]

fulltext2 = df2.apply(' '.join).values[0]
charset2 = set(fulltext2)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df2.to_csv('simplicissimus_lat0.csv', index = True)

