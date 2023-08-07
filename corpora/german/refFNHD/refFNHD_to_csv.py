'''
Convert Referenzkorpus Frühneuhochdeutsch text to csv 
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
textlist = sorted(os.listdir('./texts'))
target_filepath = 'refFNHD.csv'
export_flag = 1

# ==============================================================================
# Auxiliary functions
# ==============================================================================
def justalphas(s):
    a1 = ' '.join([''.join([k for k in word if k.isalpha()]) for word in s.split()])
    return ' '.join([k for k in a1.split()])

# ==============================================================================
# Parse refFNHD file
# ==============================================================================
dataframe_list = list()
for filename in textlist:
    filepath = os.path.join('./texts', filename)
    with open(filepath, 'r') as f:
        s0 = f.read().replace('\n','')
    id = filename.split('.')[0].capitalize()
    header_regex = r'{}:.*?Modernisierter Lesetext'.format(id)
    footer_regex = r'Referenzkorpus Frühneuhochdeutsch 1.0.1\s+\(.*?\)\s+\d+'
    assert len(re.findall(header_regex, s0)) > 0, 'header_regex not found'
    assert len(re.findall(footer_regex, s0)) > 0, 'header_regex not found'
    s1 = re.sub(header_regex, '', s0)
    s1 = re.sub(footer_regex, '', s1)
    s2 = s1.split('@H')[-1]
    df = pd.DataFrame(data = s2.split('{}-'.format(id))[1:], columns = ['txt'])
    df['idx'] = ['{}.{}'.format(id, k.split()[0].replace(',','.')) for k in df.txt]
    df['textstring'] = [' '.join(k.split()[1:]).lower() for k in df.txt]
    df['textstring'] = [justalphas(k) for k in df.textstring]
    df = df[['idx','textstring']]
    dataframe_list.append(df)

rdf = pd.concat(dataframe_list, ignore_index=True)

# ==============================================================================
# Fix duplicate page numberings (an error in the refFNHD transcriptions)
# ==============================================================================
sublabel_string = ' abcdefghijklmnopqrstuvwxyz'
rdf['sublabel_index'] = rdf.groupby('idx').cumcount()
rdf['idx'] = ['{}{}'.format(k[0],sublabel_string[k[1]]).strip() for k in zip(rdf.idx, rdf.sublabel_index)]
rdf = rdf.drop('sublabel_index', axis=1)

# ==============================================================================
# Export
# ==============================================================================
if export_flag:
    rdf.to_csv(target_filepath, index = False)

