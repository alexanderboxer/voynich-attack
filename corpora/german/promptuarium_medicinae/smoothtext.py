'''
Smooth and export a given text: Promptuarium medicinae
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
input_filepath = 'nn_promptuarium_1483.TEI-P5.xml'
export_flag = 1

# ==============================================================================
# Read XML document into pandas dataframe
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = html.unescape(f.read())

Q = dict()
Q['title'] = ' '.join(re.findall('<title type=.*?>([\s\S]*?)</title>',s0)).replace('niederdeutsch',' ') # extract the title directly
Q['preface'] = re.search('<div type="index" n="1"><div type="preface" n="2"><p>([\s\S]*?)</div>',s0).group(1)
biblio = ' '.join(re.findall('<div type="bibliography" n="2">([\s\S]*?)</div>',s0)) # extract the bibliography directly
for k, txt in enumerate(re.findall('<item>([\s\S]*?)</item>',biblio)):
    Q['biblio.{}'.format(k + 1)] = txt 
for l, txt in enumerate(re.findall('<p>([\s\S]*?)</p>',biblio)):
    Q['biblio.{}'.format(k + l + 1)] = txt 

index1 =  ' '.join(re.findall('<div n="2"><list>([\s\S]*?)</list></div>', s0)) # extract the index directly
for k, txt in enumerate(re.split('<item>', index1)[1:]):
    Q['index1.{}'.format(k + 1)] = txt 

for j, txt in enumerate(re.split('<div type="index" n="2">', s0)[1:4]):
    for k, entry in enumerate(re.split('<item>', txt)):
        Q['index{}.{}'.format(j+2, k)] = entry

index5 = re.split('<div type="index" n="2">', s0)[4].split('</list>')[0]
for k, entry in enumerate(re.split('<item>', index5)):
    Q['index5.{}'.format(k)] = entry

index6 = re.findall('<div n="2">  <head>([\s\S]*?)</list></div></div>', s0)[0]
for j, txt in enumerate(re.split('<head>', index6)):
    for k, entry in enumerate(re.split('<item>', txt)):
        Q['index6.{}.{}'.format(j,k)] = entry 

index7 = re.split('<div type="index" n="2">', s0)[5].split('</div></div>')[0]
for j, txt in enumerate(re.split('<head>', index7)[1:]):
    for k, entry in enumerate(re.split('<item>', txt)):
        Q['index7.{}.{}'.format(j,k)] = entry 

index8 = re.split('<div type="index" n="2">', s0)[6].split('</div></div>')[0]
for k, entry in enumerate(re.split('<item>', index8)):
    Q['index8.{}'.format(k)] = entry 

maintext = re.split('<div n="1"><div n="2">', s0)[1]
for j, txt in enumerate(re.split('<div n="2">', maintext)):
    for k, entry in enumerate(re.split('<p>', txt)):
        if len(re.sub('<.*?>', '', entry)) > 0:
            Q['{}.{}'.format(j+1, k)] = entry

df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
fulltext0 = df0.apply(' '.join).values[0]
tags = set(re.findall('<\w+',fulltext0))

# ==============================================================================
# Text formatting 
# ==============================================================================
df = df0.copy()

nonalpha_keepers = ['.', '!', ';', '?', ':']

df['textstring'] = df.textstring.apply(lambda x: re.sub('-<lb/>\n', '', x)) # remove hyphenated linebreak </lb> tags 
df['textstring'] = df.textstring.apply(lambda x: re.sub('-\n', '', x)) # reconnect line-broken words
df['textstring'] = df.textstring.apply(lambda x: re.sub('\n', ' ', x)) # convert all other line-breaks to whitespace
df['textstring'] = df.textstring.apply(lambda x: re.sub('<note.*?</note>', '', x)) # remove all notes 
df['textstring'] = df.textstring.apply(lambda x: re.sub('<.*?>', '', x)) # remove any leftover tags
df['textstring'] = df.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in x.lower().split()]))  
df['textstring'] = df.textstring.apply(lambda x: re.sub('\s[\.\,!\?:]\s', ' ', x)) 

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv('promptuarium1483.csv', index = True)

