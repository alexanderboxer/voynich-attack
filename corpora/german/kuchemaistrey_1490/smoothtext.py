'''
Smooth and export a given text: Kuchmaistrey
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
basename = 'kuchemaistrey'

input_directory = '.'
output_directory = '.'
input_filepath = os.path.join(input_directory, basename + '_edited.txt')
lat1_filepath = os.path.join(output_directory, basename + '_lat1.csv')

export_flag = 1

# ==============================================================================
# Read
# ==============================================================================
with open(input_filepath, 'r') as f:
    s0 = f.read()

# ==============================================================================
# Smooth
# ==============================================================================
s1 = s0.lower().replace('\n', ' ')

# punctuation cleanup
nonalpha_keepers = ['.', '!', ';', '?', ':', '¶']
s2 = ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in s1.split()])

# split into pages
pagelist = s2.split('¶')
pagelist = [' '.join(k.split()) for k in pagelist] # map all whitespaces to a single whitespace

# dataframe
df = pd.DataFrame(pagelist, columns = ['textstring'])

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    df.to_csv(lat1_filepath, index = False)
