'''
Smooth and export a given text: Chaucer
'''
# ==============================================================================
# Import modules
# ==============================================================================
import os
import re
import pandas as pd
import sys 

# ==============================================================================
# Paths
# ==============================================================================
basename = 'artzney'
input_directory = '.'
input_filepath = os.path.join(input_directory, basename + '_buchlein_v0.csv')
export_flag = 0

# ==============================================================================
# Read
# ==============================================================================
df0 = pd.read_csv(input_filepath)

sys.exit()
# ==============================================================================
# Initial dataframe
# ==============================================================================
delimiters_and_text = re.split('(here b[ei]ginneth)', s0.lower())[1:]
delimiters = delimiters_and_text[::2]
txt = delimiters_and_text[1::2]
tales = [k[0] + k[1] for k in zip(delimiters, txt)]

Q = dict()
for tale_num, tale_txt in enumerate(tales):
    paragraphs = re.split('\n\n\n', tale_txt)
    for paragraph_num, paragraph in enumerate(paragraphs):
        idx = '{}.{}.{}'.format(tale_num, paragraph_num, 0)
        Q[idx] = ''
        for line_num, line_txt in enumerate(re.split('\n\n', paragraph)):
            idx = '{}.{}.{}'.format(tale_num, paragraph_num, line_num + 1)
            line_txt2 = re.split('[1-9]', line_txt)[0]
            Q[idx] = line_txt2.replace('\n','')
            Q[idx] = re.sub('[\\n\(\)\[\]]','',line_txt2)

df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])
df0['i0'] = [int(k.split('.')[0]) for k in df0.index]
df0['i1'] = [int(k.split('.')[1]) for k in df0.index]
df0['i2'] = [int(k.split('.')[2]) for k in df0.index]
df0 = df0[['i0','i2','textstring']]

# Export intermediate csv
#df0.to_csv('c0.csv', index = False)

# ==============================================================================
# Edited dataframe
# ==============================================================================
df1 = pd.read_csv('c1.csv')

# Remove empty rows between paragraphs
df1 = df1[~pd.isna(df1.textstring)].copy().reset_index(drop=True)

# And paragraph numbering
df2 = pd.DataFrame()
for talenum in set(df1.i0):
     taledf = df1[df1.i0==talenum].copy()
     taledf['i1'] = (taledf.i2==1).cumsum()
     df2 = pd.concat([df2, taledf])

# Create index
df2['idx'] = ['{}.{}.{}'.format(k[0],k[1],k[2]) for k in zip(df2.i0, df2.i1, df2.i2)]    
df2 = df2.drop(['i0','i1','i2'], axis=1)
df2 = df2.set_index('idx')

# Remove all non-alpha characters
df2['textstring'] = df2.textstring.apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha()]) for word in x.lower().split()]))  

# alphabetical replacements
df2['textstring'] = df2.textstring.str.replace('ë','e')
df2['textstring'] = df2.textstring.str.replace('ö','o')

# charset
fulltext = df2.apply(' '.join).values[0]
charset = set(fulltext)
abc26 = 'abcdefghijklmnopqrstuvwxyz'
allowed_charset = set(abc26).union(set(' '))
assert len(charset.difference(allowed_charset)) == 0

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df2.to_csv('chaucer.csv', index = True)
