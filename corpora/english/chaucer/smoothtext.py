'''
Smooth and export a given text: Chaucer
'''
# ==============================================================================
# Import modules
# ==============================================================================
import os
import re
import sys 

# ==============================================================================
# Paths
# ==============================================================================
basename = 'chaucer'

input_directory = '.'
output_directory = '.'
input_filepath = os.path.join(input_directory, basename + '_edited.txt')
lat0_filepath = os.path.join(output_directory, basename + '_lat0.txt')

export_flag = 0

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
nonalpha_keepers = ['.', '!', ';', '?', ':']
s2 = ' '.join([''.join([k for k in word if k.isalpha() or k in nonalpha_keepers]) for word in s1.split()])

# alphabetical replacements
replacement_dictionary = {
    'ë': 'e',
    'º': '',
    'ö': 'o',
}
s3 = s2
for k, v in replacement_dictionary.items():
	s3 = s3.replace(k, v)

s_lat0 = s3

# latin-0 assert
abc26 = 'abcdefghijklmnopqrstuvwxyz'
allowed_charset = set(abc26).union(set(nonalpha_keepers)).union(set(' '))
assert len(set(s_lat0).difference(allowed_charset)) == 0


# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    with open(lat0_filepath, 'w') as f:
        f.write(s_lat0)
