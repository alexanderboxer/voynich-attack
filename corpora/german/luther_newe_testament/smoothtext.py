'''
Smooth and export a given text: Martin Luther Das Newe Testament Deutzsch
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
input_filepath = 'luther_nt_edited.txt'
export_flag = 1

# ==============================================================================
# Read text 
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read().lower()

# ==============================================================================
# Smooth and convert to dataframe
# ==============================================================================
nonalpha_keepers = ['.', '!', ';', '?', ':', '&']

s1 = re.sub('\n', ' ', s0) # convert all other line-breaks to whitespace
s2 = ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in s1.split()])

punctuation_splits = re.split('([\.!\?])\s', s2)
txt = [k.strip() for k in punctuation_splits[::2]]
punctuation = punctuation_splits[1::2] + ['']
textstring_list = [''.join(k) for k in zip(txt, punctuation)]
df0 = pd.DataFrame(textstring_list, columns = ['textstring'])

# ==============================================================================
# Export 1
# ==============================================================================
#df0.to_csv('luther_nt_parsed_firstpass.csv', index = False)

# ==============================================================================
# Read text 2
# ==============================================================================
df1 = pd.read_csv('luther_nt_parsed_edited.csv')
df1.columns = ["book","chapter","line","textstring"]
df1 = df1.applymap(lambda x: x.strip() if type(x) == str else x)

# ==============================================================================
# Substitutions
# ==============================================================================
abc1 = set(''.join([k for k in df1.textstring]))

replacement_dict = {
    "ß": "ss",
}

def charsubs(replacement_dictionary, string):
    for k,v in replacement_dictionary.items():
        string = string.replace(k, v)
    return string

df2 = df1.copy()

df2['textstring'] = df2['textstring'].apply(lambda x: charsubs(replacement_dict, x)) # character replacements

df2['textstring'] = df2['textstring'].apply(lambda x: ' '.join([''.join([k for k in word if k.isalpha()]) for word in x.split()])) # remove remaining punctuation

abc2 = set(''.join([k for k in df2.textstring]))

# ==============================================================================
# Export 2
# ==============================================================================
if export_flag:
    df2.to_csv('luther_nt22_lat0.csv', index = False)
