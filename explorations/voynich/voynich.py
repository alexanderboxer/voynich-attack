'''
voynich
'''
# ==============================================================================
# Import
# ==============================================================================
from collections import Counter
import pandas as pd 

# ==============================================================================
# Things
# ==============================================================================
vmspath = '../../transcription/vms.csv'
df = pd.read_csv(vmspath)

collist = ['folio','par','line'] + ['w{}'.format(1 +k) for k in range(26)][::2]
#df = df[collist]

nullchar = '$'
tklist  = [k for k in df.iloc[:,3:].fillna(nullchar).to_numpy().flatten() if k != nullchar] 


tkdf = pd.DataFrame.from_dict(Counter(tklist), orient = 'index').reset_index()
tkdf.columns = ['token','count']
tkdf = tkdf.sort_values('count', ascending = False).reset_index(drop = True)

z2 = zip(tklist[:-1],tklist[1:])
tk2df = pd.DataFrame.from_dict(Counter(z2), orient = 'index').reset_index()
tk2df.columns = ['tk2','count']
tk2df = tk2df.sort_values('count', ascending = False).reset_index(drop = True)

z3 = zip(tklist[:-2],tklist[1:-1],tklist[2:])
tk3df = pd.DataFrame.from_dict(Counter(z3), orient = 'index').reset_index()
tk3df.columns = ['tk3','count']
tk3df = tk3df.sort_values('count', ascending = False).reset_index(drop = True)