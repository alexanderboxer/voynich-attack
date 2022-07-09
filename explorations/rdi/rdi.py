'''
radii
'''
# ==============================================================================
# Import
# ==============================================================================
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../voynpy')
import reftext
from corpora import vms, vms1, vms2, caesar


# ==============================================================================
# Read csv export from spreadsheet
# ==============================================================================
nullchar = '$'
df0 = pd.read_csv('rdi_spreadsheet.csv').fillna(nullchar).astype(str)

# ==============================================================================
# Populate index values across empty cells
# ==============================================================================
df1 = df0.copy()
df1 = df1.iloc[:1060].copy()

def val_extend(val_array, nullchar = nullchar):
    val_splits = np.split(val_array, np.where(val_array != nullchar)[0])
    val_nested = [[k[0]] * len(k) for k in val_splits if len(k) > 0]
    val_flat = [k for xs in val_nested for k in xs]
    return val_flat

df1['color'] = val_extend(df1.color.values)
df1['rays'] = [int(float(k)) for k in val_extend(df1.rays.values)]

# ==============================================================================
# Slice by color and rays
# ==============================================================================
r7_df = df1[(df1.color == 'R') & (df1.rays == 7)].copy()
r8_df = df1[(df1.color == 'R') & (df1.rays == 8)].copy()
w7_df = df1[(df1.color == 'W') & (df1.rays == 7)].copy()
w8_df = df1[(df1.color == 'W') & (df1.rays == 8)].copy()
rdf = df1[(df1.color == 'R')].copy()
wdf = df1[(df1.color == 'W')].copy()
hep_df = df1[(df1.rays == 7)].copy()
oct_df = df1[(df1.rays == 8)].copy()

r7 = reftext.from_dataframe(r7_df, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
r8 = reftext.from_dataframe(r8_df, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
w7 = reftext.from_dataframe(w7_df, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
w8 = reftext.from_dataframe(w8_df, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
r = reftext.from_dataframe(rdf, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
w = reftext.from_dataframe(wdf, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
hep = reftext.from_dataframe(hep_df, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 
oct = reftext.from_dataframe(oct_df, language = 'voynich', read_from_col = 5, comma_split_tokens = True) 