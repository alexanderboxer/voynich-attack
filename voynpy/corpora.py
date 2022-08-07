"""
Voynich reference text instances
"""
# ==============================================================================
# Import
# ==============================================================================
import os
from weakref import ref
import pandas as pd
import reftext

# ==============================================================================
# Navigate to this module's directory
# ==============================================================================
cwd = os.getcwd()
module_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(module_path)

# ==============================================================================
# Instantiate Reftext objects
# ==============================================================================
# vms: full Voynich
vmspath = '../transcription/vms.csv'
vms = reftext.from_csv(vmspath, language = 'voynich', read_from_col = 3, comma_split_tokens = True)

# vms1: Voynich up to f103r
f103r_idx = vms.df[vms.df.folio == '103r'].index.tolist()[0]
vms1_df = vms.df.iloc[:f103r_idx].copy()
vms1 = reftext.from_dataframe(vms1_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# vms2: Voynich from f103r
vms2_df = vms.df.iloc[f103r_idx:].copy()
vms2 = reftext.from_dataframe(vms2_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# plants1: f1v through f57r
idx1 = vms.df[vms.df.folio == '1v'].index.tolist()[0]
idx2 = 1 + vms.df[vms.df.folio == '57r'].index.tolist()[-1]
plants1_df = vms.df.iloc[idx1:idx2].copy()
plants1 = reftext.from_dataframe(plants1_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# fems: f75r through f84v
idx1 = vms.df[vms.df.folio == '75r'].index.tolist()[0]
idx2 = 1 + vms.df[vms.df.folio == '84v'].index.tolist()[-1]
fems_df = vms.df.iloc[idx1:idx2].copy()
fems = reftext.from_dataframe(fems_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# plants2: f87r through f102vb
idx1 = vms.df[vms.df.folio == '87r'].index.tolist()[0]
idx2 = 1 + vms.df[vms.df.folio == '102vb'].index.tolist()[-1]
plants2_df = vms.df.iloc[idx1:idx2].copy()
plants2 = reftext.from_dataframe(plants2_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# stars: Voynich from f103r (same as vms2)
stars_df = vms.df.iloc[f103r_idx:].copy()
stars = reftext.from_dataframe(stars_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# plants: concat plants 1 and 2
plants_df = pd.concat([plants1_df, plants2_df])
plants = reftext.from_dataframe(plants_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# enoch: MS 3188 Enochian 
enochpath = '../corpora/enochian/ms3188.csv'
enoch = reftext.from_csv(enochpath, language = 'enochian', read_from_col = 2, comma_split_tokens = False)

#----------
# Latin
#----------
# Caesar: De bello gallico
caesarpath = '../corpora/latin/caesar/caesar_lat0.csv'
caesar = reftext.from_textstring_csv(caesarpath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Vitruvius: De architectura
vitruviuspath = '../corpora/latin/vitruvius/vitruvius_lat0.csv'
vitruvius = reftext.from_textstring_csv(vitruviuspath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Celsus: De medicina
celsuspath = '../corpora/latin/celsus/celsus_lat0.csv'
celsus = reftext.from_textstring_csv(celsuspath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Pliny: Naturalis historia
plinypath = '../corpora/latin/pliny/pliny_lat0.csv'
pliny = reftext.from_textstring_csv(plinypath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Latin: all texts
reftext_list = [caesar, vitruvius, celsus, pliny]
namelist = ['caes', 'vitr', 'cels', 'plin']

latin_df = pd.DataFrame()
for obj, name in zip(reftext_list, namelist):
    opus_df = obj.df.copy()
    opus_df.columns = ['line', 'textstring']
    opus_df['op'] = name 
    opus_df = opus_df[['op','line','textstring']]
    latin_df = pd.concat([latin_df, opus_df], ignore_index = True)

latin_fulltext = ' '.join([k for k in latin_df.textstring])
latin_tklist = [''.join([k for k in word if k.isalpha()]) for word in latin_fulltext.split()]
latin_charlist = list(''.join(latin_tklist))
latin = reftext.RefText('latin', latin_tklist, latin_charlist)
latin.df = latin_df

#----------
# Hebrew
#----------
# heb: Torah
hebpath = '../corpora/hebrew/torah/torah.txt'
heb = reftext.from_txt(hebpath, language = 'hebrew')

#----------
# English
#----------
# chaucer: canterbury tales, etc.
chaucerpath = '../corpora/english/chaucer/chaucer_lat0.txt'
chaucer = reftext.from_txt(chaucerpath, language = 'english')

# wycliffe bible
wycliffepath = '../corpora/english/wycliffe/wycliffe_lat0.txt'
wycliffe = reftext.from_txt(wycliffepath, language = 'english')

#----------
# German
#----------
# Simplicissimus  (utf8)
simppath = '../corpora/german/simplicissimus/simplicissimus.csv'
simp = reftext.from_textstring_csv(simppath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# Promptuarium medicinae  (lat0)
promptuariumpath = '../corpora/german/promptuarium_medicinae/promptuarium1483.csv'
promptuarium = reftext.from_textstring_csv(promptuariumpath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# kuchemaistrey (lat1)
kuchepath = '../corpora/german/kuchemaistrey_1490/kuchemaistrey_lat1.csv'
kuche = reftext.from_textstring_csv(kuchepath, language = 'german', read_from_col = 0, comma_split_tokens = False)

# splendor solis (lat1)
splendorpath = '../corpora/german/splendor_solis_1590/splendor_solis_lat1.csv'
splendor = reftext.from_textstring_csv(splendorpath, language = 'german', read_from_col = 0, comma_split_tokens = False)

# German: all texts
reftext_list = [simp, promptuarium]
namelist = ['simp','prom']

german_df = pd.DataFrame()
for obj, name in zip(reftext_list, namelist):
    opus_df = obj.df.copy()
    opus_df.columns = ['line', 'textstring']
    opus_df['op'] = name 
    opus_df = opus_df[['op','line','textstring']]
    german_df = pd.concat([german_df, opus_df], ignore_index = True)

german_fulltext = ' '.join([k for k in german_df.textstring])
german_tklist = [''.join([k for k in word if k.isalpha()]) for word in german_fulltext.split()]
german_charlist = list(''.join(german_tklist))
german = reftext.RefText('german', german_tklist, german_charlist)
german.df = german_df


# ==============================================================================
# Navigate back to the original working directory
# ==============================================================================
os.chdir(cwd)

