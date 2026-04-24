"""
Voynich reference text instances
"""
# ==============================================================================
# Import
# ==============================================================================
import json
from pathlib import Path
import pandas as pd
from . import reftext

# ==============================================================================
# Root directory of the repository
# ==============================================================================
_root = Path(__file__).resolve().parent.parent

# ==============================================================================
# Instantiate Reftext objects
# ==============================================================================
# vms: full Voynich
vmspath = _root / 'transcription/vms.csv'
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

# R7
r7path = _root / 'corpora/misc/stars/R7.csv'
r7 = reftext.from_csv(r7path, language = 'voynich', read_from_col = 4, comma_split_tokens = True)
r7.df.columns = ['folio','side','par','line'] + ['t{}'.format(k + 1) for k in range(r7.df.shape[1] - 4)]
r7.df = r7.df.fillna('$')

# W7
w7path = _root / 'corpora/misc/stars/W7.csv'
w7 = reftext.from_csv(w7path, language = 'voynich', read_from_col = 4, comma_split_tokens = True)
w7.df.columns = ['folio','side','par','line'] + ['t{}'.format(k + 1) for k in range(w7.df.shape[1] - 4)]
w7.df = w7.df.fillna('$')

# vms_unicode: Voynich with PUA Unicode mapping (Supplementary PUA-B, U+FF400–FF51F)
unicode_dict_path = _root / 'transcription/unicode_dict.json'
with open(unicode_dict_path, 'r') as f:
    _unicode_char_map = json.load(f)
vms_unicode = reftext.from_mapped(vms, _unicode_char_map, language='voynich_unicode')

# vms_unicode_bmp: Voynich with BMP PUA mapping (U+E000–E11F)
unicode_dict_bmp_path = _root / 'transcription/unicode_dict_bmp.json'
with open(unicode_dict_bmp_path, 'r') as f:
    _unicode_char_map_bmp = json.load(f)
vms_unicode_bmp = reftext.from_mapped(vms, _unicode_char_map_bmp, language='voynich_unicode_bmp')


#----------
# Latin
#----------
# Caesar: De bello gallico
caesarpath = _root / 'corpora/latin/caesar/caesar_lat0.csv'
caesar = reftext.from_textstring_csv(caesarpath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Vitruvius: De architectura
vitruviuspath = _root / 'corpora/latin/vitruvius/vitruvius_lat0.csv'
vitruvius = reftext.from_textstring_csv(vitruviuspath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Celsus: De medicina
celsuspath = _root / 'corpora/latin/celsus/celsus_lat0.csv'
celsus = reftext.from_textstring_csv(celsuspath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Pliny: Naturalis historia
plinypath = _root / 'corpora/latin/pliny/pliny_lat0.csv'
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
hebpath = _root / 'corpora/hebrew/torah/torah.txt'
heb = reftext.from_txt(hebpath, language = 'hebrew')

#----------
# English
#----------
# chaucer: canterbury tales, etc.
chaucerpath = _root / 'corpora/english/chaucer/chaucer.csv'
chaucer = reftext.from_textstring_csv(chaucerpath, language = 'english', read_from_col = 1, comma_split_tokens = False)

# wycliffe bible
wycliffepath = _root / 'corpora/english/wycliffe/wycliffe_lat0.txt'
wycliffe = reftext.from_txt(wycliffepath, language = 'english')

#----------
# German
#----------
# Simplicissimus  (utf8)
simppath = _root / 'corpora/german/simplicissimus/simplicissimus.csv'
simp = reftext.from_textstring_csv(simppath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# Simplicissimus  (lat0)
simp0path = _root / 'corpora/german/simplicissimus/simplicissimus_lat0.csv'
simp0 = reftext.from_textstring_csv(simp0path, language = 'german', read_from_col = 1, comma_split_tokens = False)

# Promptuarium medicinae  (lat0)
promptuariumpath = _root / 'corpora/german/promptuarium_medicinae/promptuarium1483.csv'
promptuarium = reftext.from_textstring_csv(promptuariumpath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# kuchemaistrey (lat1)
kuchepath = _root / 'corpora/german/kuchemaistrey/kuchemaistrey1490.csv'
kuche = reftext.from_textstring_csv(kuchepath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# splendor solis (lat1)
splendorpath = _root / 'corpora/german/splendor_solis_1590/splendor_solis_lat1.csv'
splendor = reftext.from_textstring_csv(splendorpath, language = 'german', read_from_col = 0, comma_split_tokens = False)

# splendor solis (lat0)
splendorpath0 = _root / 'corpora/german/splendor_solis_1590/splendor_solis_lat0.csv'
splendor0 = reftext.from_textstring_csv_lat0(splendorpath0, language = 'german')

# refFNHD miscellany
refFNHDpath = _root / 'corpora/german/refFNHD/refFNHD.csv'
refFNHD = reftext.from_textstring_csv_lat0(refFNHDpath, language = 'german')

# luther september bible (lat0)
lutherpath = _root / 'corpora/german/luther_newe_testament/luther_nt22_lat0.csv'
luther = reftext.from_textstring_csv_var1(lutherpath, language = 'german', read_from_col = 3, comma_split_tokens = False)

# =============================================================================
# Lazy-loading framework for corpus_build pipeline texts.
# Older texts above this point still load eagerly; new corpus_build texts
# register lazy loaders and are materialized on first attribute access via
# module-level __getattr__ (PEP 562). Migration of older texts is optional.
# =============================================================================

_LOADERS: dict[str, callable] = {}
_CACHE: dict[str, reftext.RefText] = {}


def _register(name: str):
    def _decorator(fn):
        _LOADERS[name] = fn
        return fn
    return _decorator


def _get(name: str):
    if name in _CACHE:
        return _CACHE[name]
    if name in _LOADERS:
        _CACHE[name] = _LOADERS[name]()
        return _CACHE[name]
    raise AttributeError(f"module 'voynpy.corpora' has no attribute {name!r}")


def __getattr__(name):
    return _get(name)


# brunfels apodixis 1531 (corpus_build pipeline; textstring_simple column)
@_register('brunfels')
def _load_brunfels():
    path = _root / 'corpora/german/brunfels_apodixis_1531/brunfels_apodixis_1531.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Nürnberg almanach 1473 (Koberger; corpus_build pipeline)
@_register('almanach1473')
def _load_almanach1473():
    path = _root / 'corpora/german/nn_almanach05_1473/nn_almanach05_1473.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Dracole pamphlet 1485 (Lübeck; Bartholomaeus Gothan; Low German; Vlad the Impaler)
@_register('dracole1485')
def _load_dracole1485():
    path = _root / 'corpora/german/nn_dracole_1485/nn_dracole_1485.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Das Meerwunder 1472 (heroic epic from Dresdner Heldenbuch; Early New High German verse)
@_register('meerwunder1472')
def _load_meerwunder1472():
    path = _root / 'corpora/german/nn_meerwunder_1472/nn_meerwunder_1472.csv'
    return reftext.from_corpus_build_csv(path, language='german', block_types=('verse',))


# Nürnberg almanach 1481 (Creussner/Koberger; calendrical prose almanac)
@_register('almanach1481')
def _load_almanach1481():
    path = _root / 'corpora/german/nn_almanach05_1481/nn_almanach05_1481.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Promptuarium medicinae 1483 (Bartholomäus Ghotan, Magdeburg; Low German medical reference)
# Replaces the older hand-coded `promptuarium` entry.
@_register('promptuarium1483')
def _load_promptuarium1483():
    path = _root / 'corpora/german/nn_promptuarium_1483/nn_promptuarium_1483.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Kuchemaistrey 1490 (Peter Wagner, Nürnberg; early printed German cookbook)
# Replaces the older hand-coded `kuchemaistrey` entry.
@_register('kuchemaistrey1490')
def _load_kuchemaistrey1490():
    path = _root / 'corpora/german/nn_kuchemaistrey_1490/nn_kuchemaistrey_1490.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# dta: combined RefText across all corpus_build-pipeline DTA texts.
@_register('dta')
def _load_dta():
    parts = [(name, _get(name)) for name in ('brunfels', 'almanach1473', 'dracole1485', 'meerwunder1472', 'almanach1481', 'promptuarium1483', 'kuchemaistrey1490')]
    tklist = [t for _, rt in parts for t in rt.tklist]
    charlist = list(''.join(tklist))
    rt = reftext.RefText('german', tklist, charlist)
    rt.df = pd.concat(
        [p.df.assign(doc=name) for name, p in parts],
        ignore_index=True,
    )[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    return rt

# German: all texts
reftext_list = [simp, kuche, promptuarium]
namelist = ['simp','kuche','prom']

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


#----------
# French
#----------
# Rabelais: Pantagruel + Gargantual
rabelaispath = _root / 'corpora/french/rabelais/rabelais.csv'
rabelais = reftext.from_textstring_csv_var1(rabelaispath, language = 'french', read_from_col = 3, comma_split_tokens = False)


#----------
# Spanish
#----------
# Cervantes: Don Quixote
quixotepath = _root / 'corpora/spanish/quixote/quixote_lat0.csv'
quixote = reftext.from_textstring_csv_var1(quixotepath, language = 'spanish', read_from_col = 3, comma_split_tokens = False)


#----------
# Ciphers
#----------
wallis1path = _root / 'corpora/ciphers/wallis/wallis1.json'
with open(wallis1path, 'r') as f:
    j = json.load(f)
wallis1 = reftext.RefText('cipher', tklist = j['tklist'], charlist = j['charlist'])

#----------
# Enochian
#----------
# enoch: MS 3188 Enochian 
enochpath = _root / 'corpora/enochian/ms3188.csv'
enoch = reftext.from_csv(enochpath, language = 'enochian', read_from_col = 2, comma_split_tokens = False)


