"""
subs
"""
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
# Things
# ==============================================================================
df1 = vms1.df
df1 = df1.replace({
    '8,a,m': '4,o,N,c,c,9',
    'cc,o,x': '4,o,N,c,c,8,9',
    'cc,c,8,9': '4,o,N,c,c,8,9',
}
)
s1 = reftext.from_dataframe(df1, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# plants1
f57v_idx = vms.df[vms.df.folio == '57r'].index.tolist()[-1] + 1
plants_df = vms.df.iloc[:f57v_idx].copy()
plants = reftext.from_dataframe(plants_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 