'''
Smooth and export a given text: Kuchemaistrey
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
input_filepath = 'nn_kuchemaistrey_1490.TEI-P5.xml'
export_flag = 1

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = html.unescape(f.read())

'''
Q = dict()
Q['title'] = 'Kuchemaistrey'
for i, txt in enumerate(re.split('<div n="2"[\s\S]*?>[\s\S]*?<', s0)[1:4]):
    tagtype = txt.split()[0].split('>')[0]
    if i == 0:
        i = 'P'
    else:
        i -= 1
    if (tagtype == 'head') or (tagtype == 'div'):
        val = txt.split('</head>')[0].split('head>')[-1]
        linekey = '{}.0'.format(i)
        Q[linekey] = val
        h = re.split('(\w+\.\s?¶\s*?)', txt)[1:]
        q = [' '.join(k) for k in zip(h[::2], h[1::2])]
        for j, par in enumerate(q):
            linekey = '{}.{}'.format(i, j+1)
            Q[linekey] = par
    else:
        val = txt.split('</p>')[0].split('p>')[-1]
        linekey = '{}.0'.format(i)
        Q[linekey] = val
        for j, listitem in enumerate(re.findall('<item>([\s\S]*?)</item>', txt)):
            linekey = '{}.{}'.format(i, j+1)
            Q[linekey] = listitem

'''
Q = dict()
Q['title'] = 'Kuchemaistrey'
for i, txt in enumerate(re.split('<div n="2"[\s\S]*?>[\s\S]*?<', s0)[1:]):
    tagtype = txt.split()[0].split('>')[0]
    if i == 0:
        i = 'P'
    else:
        i -= 1
    if (tagtype == 'head') or (tagtype == 'div'):
        val = txt.split('</head>')[0].split('head>')[-1]
        linekey = '{}.0'.format(i)
        Q[linekey] = val
        for j, par in enumerate(re.findall('<p>([\s\S]*?)</p>', txt)):
            linekey = '{}.{}'.format(i, j+1)
            Q[linekey] = par
    else:
        val = txt.split('</p>')[0].split('p>')[-1]
        linekey = '{}.0'.format(i)
        Q[linekey] = val
        for j, listitem in enumerate(re.findall('<item>([\s\S]*?)</item>', txt)):
            linekey = '{}.{}'.format(i, j+1)
            Q[linekey] = listitem


df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
fulltext0 = df0.apply(' '.join).values[0]
tags = set(re.findall('<\w+',fulltext0))

# ==============================================================================
# Text formatting 
# ==============================================================================
df = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df['textstring'] = df.textstring.apply(lambda x: re.sub('<abbr.*?</abbr>', '', x)) # remove all notes 


#df['textstring'] = df.textstring.apply(lambda x: re.sub('-<lb/>\n', '', x)) # remove hyphenated linebreak </lb> tags 
#df['textstring'] = df.textstring.apply(lambda x: re.sub('-\n', '', x)) # reconnect line-broken words
#df['textstring'] = df.textstring.apply(lambda x: re.sub('\n', ' ', x)) # convert all other line-breaks to whitespace
#df['textstring'] = df.textstring.apply(lambda x: re.sub('<note.*?</note>', '', x)) # remove all notes 
df['textstring'] = df.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df['textstring'] = df.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))  
df['textstring'] = df.textstring.apply(lambda x: re.sub('\s[\.\,!\?:]\s', ' ', x)) 

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv('kuchemaistrey1490.csv', index = True)

