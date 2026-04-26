'''
Smooth and export a given text
'''
# ==============================================================================
# Import modules
# ==============================================================================
import os
import re

# ==============================================================================
# Paths
# ==============================================================================
basename = 'hamlet'

input_directory = '.'
output_directory = '.'
input_filepath = os.path.join(input_directory, basename + '_edited.txt')
alpha_filepath = os.path.join(output_directory, basename + '_alpha.txt')
alphaplus_filepath = os.path.join(output_directory, basename + '_alphaplus.txt')

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
}
s3 = s2
for k, v in replacement_dictionary.items():
	s3 = s3.replace(k, v)

s_alphaplus = s3
s_alpha = ' '.join([''.join([k for k in word if k.isalpha()]) for word in s_alphaplus.split()])

# alphaplus assert
abc26 = 'abcdefghijklmnopqrstuvwxyz'
allowed_charset = set(abc26).union(set(nonalpha_keepers)).union(set(' '))
assert len(set(s_alphaplus).difference(allowed_charset)) == 0

# alpha assert
allowed_charset = set(abc26).union(set(' '))
assert len(set(s_alpha).difference(allowed_charset)) == 0

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    with open(alpha_filepath, 'w') as f:
        f.write(s_alpha)

    with open(alphaplus_filepath, 'w') as f:
        f.write(s_alphaplus)