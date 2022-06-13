"""
Voynich reference text instances
"""
# ==============================================================================
# Import
# ==============================================================================
import reftext

# ==============================================================================
# Instantiate
# ==============================================================================
# vms: full Voynich
vmspath = '../../transcription/vms.csv'
vms = reftext.from_csv(vmspath, language = 'voynich', read_from_col = 3, comma_split_tokens = True)

# vms1: Voynich up to f103r
f013r_idx = vms.df[vms.df.folio == '103r'].index.tolist()[0]
vms1_df = vms.df.iloc[:f013r_idx].copy()
vms1 = reftext.from_dataframe(vms1_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# vms2: Voynich from f103r
vms2_df = vms.df.iloc[f013r_idx:].copy()
vms2 = reftext.from_dataframe(vms2_df, language = 'voynich', read_from_col = 3, comma_split_tokens = True) 

# enoch: MS 3188 Enochian 
enochpath = '../../corpora/enochian/ms3188.csv'
enoch = reftext.from_csv(enochpath, language = 'enochian', read_from_col = 2, comma_split_tokens = False)

# caesar: Caesar De Bello Gallico
caesarpath = '../../corpora/latin/caesar_bellogallico/caesar_bellogallico_lat0.txt'
caesar = reftext.from_txt(caesarpath, language = 'latin')

# heb: Torah
hebpath = '../../corpora/hebrew/torah/torah.txt'
heb = reftext.from_txt(hebpath, language = 'hebrew')

