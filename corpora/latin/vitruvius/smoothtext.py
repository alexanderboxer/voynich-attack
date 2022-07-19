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
input_filepaths = ['{}.txt'.format(k) for k in ['v1','v2','v3','v4','v5','v6','v7','v8','v9','v10']]
output_filepath = 'vitruvius_lat1.csv'
export_flag = 0

# ==============================================================================
# Read text into a dictionary 
# ==============================================================================
Q = dict()
nonalpha_keepers = ['.', '!', ';', '?', ':']

for i, filepath in enumerate(input_filepaths):
    with open(filepath, 'r') as f:
        s0 = f.read()

    s1 = ' '.join(s0.lower().replace('\n', ' ').split())

    # Find chapter headings
    chapter_headings = re.findall(r'\w*\s*\w+\s+\[1]', s1) + ['']

    # Split files into chapters and chapters into lines
    for j, heading in enumerate(chapter_headings[:-1]):
        pattern = '{}(.+){}'.format(chapter_headings[j], chapter_headings[j+1]).replace('[','\[').replace(']','\]')
        chapter_text = re.search(pattern, s1).group(1)
        for l, textline in enumerate(re.split('\[\d+\]',chapter_text)):
            linenum = '{}.{}.{}'.format(i+1, j, l+1)
            Q[linenum] = ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in textline.split()])


df0 = pd.DataFrame.from_dict(Q, orient = 'index', columns = ['textstring'])

# ==============================================================================
# Character replacements
# ==============================================================================
df = df0.copy()
replacement_dictionary = {
    'ã': 'i', # strange typo (2 examples)
    'ê': 'e', # 1 example
    'ì': 'i', # 4 examples
    'î': 'î', # leave as is: 9 examples
    'ï': 'i', # 2 examples
    'û': 'û', # leave as is: 16 examples
}

for k, v in replacement_dictionary.items():
	df['textstring'] = df.textstring.apply(lambda x: x.replace(k, v))

fulltext = df.apply(' '.join).values[0]
charset = set(fulltext)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv(output_filepath, index = False)
