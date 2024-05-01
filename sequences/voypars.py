'''
Create a csv of Voynich paragraphs
'''
# ==============================================================================
# Import
# ==============================================================================
import re
import sys

sys.path.insert(0, '../voynpy')
from corpora import vms

# ==============================================================================
# Create a dataframe of Voynich paragraphs
# ==============================================================================
pardf = vms.df.copy()
pardf['tks'] = pardf.iloc[:,3:].apply(lambda X: ';'.join(X), axis = 1)
pardf = pardf.groupby(['folio','par']).agg({'tks': lambda x: ';'.join(x)})
sep = '; '
pardf['textstring'] = pardf['tks'].apply(lambda x: sep.join([k for k in x.split(';') if k != '$']))
pardf = pardf['textstring'].reset_index()
pardf['side'] = [re.sub('[0-9]','',k) for k in pardf.folio]
pardf['folio'] = [int(re.sub('[^0-9]','',k)) for k in pardf.folio]
pardf['idx'] = ['{}.{}.{}'.format(k[0],k[1],k[2]) for k in zip(pardf.folio, pardf.side, pardf.par)]
pardf = pardf.sort_values(['folio','side','par'])[['idx','textstring']].set_index('idx')#.reset_index(drop=True)

# ==============================================================================
# Save
# ==============================================================================
pardf.to_csv('voypars.csv')
