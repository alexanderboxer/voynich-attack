'''
Identify and remove typos from vms_spreadsheet.numbers
'''
# ==============================================================================
# Import
# ==============================================================================
import re
import numpy as np
import pandas as pd

# ==============================================================================
# Read csv export from spreadsheet
# ==============================================================================
nullchar = '$'
df0 = pd.read_csv('vmsraw.csv').fillna(nullchar).astype(str)

# ==============================================================================
# Populate index values across empty cells, clean up paragraph and line labels 
# ==============================================================================
df1 = df0

def val_extend(val_array, nullchar = nullchar):
    val_splits = np.split(val_array, np.where(val_array != nullchar)[0])
    val_nested = [[k[0]] * len(k) for k in val_splits if len(k) > 0]
    val_flat = [k for xs in val_nested for k in xs]
    return val_flat

df1['folio'] = val_extend(df0.folio.values)
df1['par'] = [re.sub('\[.*?\]','', k) for k in df1.par] # remove cases of bracketed notes appended to the paragraph number (e.g., 7[R7])
df1['par'] = [k if k in [nullchar] + [str(k) for k in range(25)] else nullchar for k in df1.par] # keep only the numerical entry (i.e., remove notes)
df1['par'] = val_extend(df1.par.values)
df1['line'] = [str(int(float(k))) if k != nullchar else nullchar for k in df1.line]
df1.drop(df1[df1.line == nullchar].index, inplace = True) # drop empty rows between pages

# ==============================================================================
# Create a simplified frame with one string per line (no word-breaks) 
# ==============================================================================
df2 = pd.concat([df1.iloc[:,:3], df1.iloc[:,3:].agg(','.join, axis = 1)], axis = 1).rename(columns = {0: 'txt'})

# ==============================================================================
# Find all lines with anomalous chars (and correct these in the spreadsheet)
# ==============================================================================
charstring = ','.join([k for k in df2.txt])  
charset = sorted(list(set(charstring.split(','))))

standard_chars = ['2','4','8','9','a','c','cc','c^c','i','M','m','N','n','o','P1','P2','Q','x','Y','Z']
odd_chars = ['3','9^','â','c^','c^o','c^9','h','ô','о̄','m+','v','V','V^','y','<','<*','>']
goodchars = sorted(list(set(standard_chars).union(set(odd_chars))))

badchars = set(charset) - set(goodchars) - set(nullchar)
badchars = sorted([k for k in badchars if '?' not in k]) 

bdf = df2[df2.txt.apply(lambda x: 'о̄' in x.split(','))]

# ==============================================================================
# Export clean vms.csv
# ==============================================================================
#df1.to_csv('vms.csv', index = False)