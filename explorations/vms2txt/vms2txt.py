'''
vms2txt
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../voynpy')
from corpora import plants1

# ==============================================================================
# Replacement dictionaries
# ==============================================================================
eng1 = {
    '8,a,m':			'th',	# rank 1
    'cc,o,x':			'er',	# rank 2    TRIPLE (x2)
    'cc,o,Z':			'es',	# rank 3	TERMINAL DOUBLE
    '8,9':		        '.',	# rank 4
    '8,a,Z':		    '.',	# rank 5
    '2':			    '.',	# rank 6
    'c^c,o,x':			'.',	# rank 7	
    'c,M,c,9':			'.',	# rank 8    TERMINAL DOUBLE
    'cc,9':			    '.',	# rank 9
    'o,Z':		        '.',	# rank 10
    'c^c,o':		    '.',	# rank 11	
    '8,a,n':			'.',	# rank 12
    'o,x':				'.',	# rank 13
    'a,m':				'.',	# rank 14	
    'cc,c,9':	        '.',	# rank 15	
    'c^c,o,Z':			'.',	# rank 16
    'cc,c,8,9':		    '.',	# rank 17
    'c^c,9':			'.',	# rank 18
    'a,Z':			    '.',	# rank 19
    'o,N,a,m':			'.',	# rank 20
    '$':                ''
}


# ==============================================================================
# Replace and export
# ==============================================================================
replacement_dictionary = eng1
df = plants1.df.astype(str).copy()
df['line'] = ['.'.join(k) for k in zip(df.folio, df.par, df.line)]

df.iloc[:,3:] = df.iloc[:,3:].applymap(lambda x: replacement_dictionary[x].upper() if x in replacement_dictionary.keys() else '.')
df = df.drop(['folio','par'], axis = 1).set_index('line')


df.to_csv('vms.txt', header = None, index = None, sep = ' ')
with open('vms.txt', 'r+') as f:
	s = f.read()
	f.seek(0)
	f.write(s.replace('"',''))
	f.truncate()