'''
Smooth and export a given text: Pantagruel + Gargantua
'''
# ==============================================================================
# Import modules
# ==============================================================================
import re 
import sys 
import json
import pandas as pd

# ==============================================================================
# Read text 
# ==============================================================================
df0 = pd.read_csv('wallis1.csv').fillna('$')

# ==============================================================================
# Token list
# ==============================================================================
tklist = [str(k) for k in df0.values.flatten() if k != '$']
tklist = [re.sub('\.0', '', k) for k in tklist] # fix entries that for some reason are read as floats 

# ==============================================================================
# Character list
# ==============================================================================
replacement_dict = {
    '1u’': 'A',
    '2u’': 'B',
    '3u’': 'C',
    '4u’': 'D',
    '5u’': 'E',
    '6u’': 'F',
    '7u’': 'G',
    '8u’': 'H',
    '9u’': 'I',
    '0u’': 'J',
    '1’': 'a',
    '2’': 'b',
    '3’': 'c',
    '4’': 'd',
    '5’': 'e',
    '6’': 'f',
    '7’': 'g',
    '8’': 'h',
    '9’': 'i',
    '0’': 'j',
    '1u': 'k',
    '2u': 'l',
    '3u': 'm',
    '4u': 'n',
    '5u': 'o',
    '6u': 'p',
    '7u': 'q',
    '8u': 'r',
    '9u': 's',
    '0u': 't',
}

tklist_mod = tklist
for key, val in replacement_dict.items():
    tklist_mod = [re.sub(key, val, k) for k in tklist_mod]

charlist = [k for k in ''.join(tklist_mod)]
for key, val in replacement_dict.items():
    charlist = [re.sub(val, key, k) for k in charlist]

# ==============================================================================
# Export as json
# ==============================================================================
wallis1_dict = {
    'tklist': tklist,
    'charlist': charlist,
}

j = json.dumps(wallis1_dict)
with open('wallis1.json', 'w') as f:
    f.write(j)