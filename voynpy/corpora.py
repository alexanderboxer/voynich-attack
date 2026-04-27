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
chaucerpath = _root / 'corpora/english/legacy/chaucer/chaucer.csv'
chaucer = reftext.from_textstring_csv(chaucerpath, language = 'english', read_from_col = 1, comma_split_tokens = False)

# wycliffe bible
wycliffepath = _root / 'corpora/english/legacy/wycliffe/wycliffe_lat0.txt'
wycliffe = reftext.from_txt(wycliffepath, language = 'english')

#----------
# German
#----------
# Simplicissimus  (utf8)
simppath = _root / 'corpora/german/legacy/simplicissimus/simplicissimus.csv'
simp = reftext.from_textstring_csv(simppath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# Simplicissimus  (lat0)
simp0path = _root / 'corpora/german/legacy/simplicissimus/simplicissimus_lat0.csv'
simp0 = reftext.from_textstring_csv(simp0path, language = 'german', read_from_col = 1, comma_split_tokens = False)

# Promptuarium medicinae  (lat0)
promptuariumpath = _root / 'corpora/german/legacy/promptuarium_medicinae/promptuarium1483.csv'
promptuarium = reftext.from_textstring_csv(promptuariumpath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# kuchemaistrey (lat1)
kuchepath = _root / 'corpora/german/legacy/kuchemaistrey/kuchemaistrey1490.csv'
kuche = reftext.from_textstring_csv(kuchepath, language = 'german', read_from_col = 1, comma_split_tokens = False)

# splendor solis (lat1)
splendorpath = _root / 'corpora/german/legacy/splendor_solis_1590/splendor_solis_lat1.csv'
splendor = reftext.from_textstring_csv(splendorpath, language = 'german', read_from_col = 0, comma_split_tokens = False)

# splendor solis (lat0)
splendorpath0 = _root / 'corpora/german/legacy/splendor_solis_1590/splendor_solis_lat0.csv'
splendor0 = reftext.from_textstring_csv_lat0(splendorpath0, language = 'german')

# refFNHD miscellany
refFNHDpath = _root / 'corpora/german/legacy/refFNHD/refFNHD.csv'
refFNHD = reftext.from_textstring_csv_lat0(refFNHDpath, language = 'german')

# luther september bible (lat0)
lutherpath = _root / 'corpora/german/legacy/luther_newe_testament/luther_nt22_lat0.csv'
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
    path = _root / 'corpora/german/DTA/1531_brunfels_apodixis/1531_brunfels_apodixis.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Nürnberg almanach 1473 (Koberger; corpus_build pipeline)
@_register('almanach1473')
def _load_almanach1473():
    path = _root / 'corpora/german/DTA/1473_nn_almanach05/1473_nn_almanach05.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Dracole pamphlet 1485 (Lübeck; Bartholomaeus Gothan; Low German; Vlad the Impaler)
@_register('dracole1485')
def _load_dracole1485():
    path = _root / 'corpora/german/DTA/1485_nn_dracole/1485_nn_dracole.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Das Meerwunder 1472 (heroic epic from Dresdner Heldenbuch; Early New High German verse)
@_register('meerwunder1472')
def _load_meerwunder1472():
    path = _root / 'corpora/german/DTA/1472_nn_meerwunder/1472_nn_meerwunder.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Nürnberg almanach 1481 (Creussner/Koberger; calendrical prose almanac)
@_register('almanach1481')
def _load_almanach1481():
    path = _root / 'corpora/german/DTA/1481_nn_almanach05/1481_nn_almanach05.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Promptuarium medicinae 1483 (Bartholomäus Ghotan, Magdeburg; Low German medical reference)
# Replaces the older hand-coded `promptuarium` entry.
@_register('promptuarium1483')
def _load_promptuarium1483():
    path = _root / 'corpora/german/DTA/1483_nn_promptuarium/1483_nn_promptuarium.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Kuchemaistrey 1490 (Peter Wagner, Nürnberg; early printed German cookbook)
# Replaces the older hand-coded `kuchemaistrey` entry.
@_register('kuchemaistrey1490')
def _load_kuchemaistrey1490():
    path = _root / 'corpora/german/DTA/1490_nn_kuchemaistrey/1490_nn_kuchemaistrey.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Crescentiis, Von den Figuren der Baum und Kreuter (1493, Peter Drach, Speyer;
# German translation of Petrus de Crescentiis' agricultural/herbal work).
@_register('crescentiis1493')
def _load_crescentiis1493():
    path = _root / 'corpora/german/DTA/1493_crescentiis_figuren/1493_crescentiis_figuren.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Springer, Merfart (1509, Balthasar Springer; account of an Indian voyage).
@_register('springer1509')
def _load_springer1509():
    path = _root / 'corpora/german/DTA/1509_springer_merfart/1509_springer_merfart.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Ellenbog, Von den gifftigen temmpffen (1524, Ulrich Ellenbog, Augsburg;
# treatise on toxic metalworking vapors).
@_register('ellenbog1524')
def _load_ellenbog1524():
    path = _root / 'corpora/german/DTA/1524_ellenbog_temmpffe/1524_ellenbog_temmpffe.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Artzney Buchlein wider allerlei kranckeyten der tzeen (1530, Lübeck;
# anonymous Low German treatise on dental diseases and remedies).
@_register('tzeen1530')
def _load_tzeen1530():
    path = _root / 'corpora/german/DTA/1530_nn_tzeen/1530_nn_tzeen.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Anonymous 1487 almanac (DTA nn_almanach04_1487).
@_register('almanach1487')
def _load_almanach1487():
    path = _root / 'corpora/german/DTA/1487_nn_almanach04/1487_nn_almanach04.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Dracole waide (1488 print; second edition of the Dracole wyda narrative,
# cf. dracole1485).
@_register('dracole1488')
def _load_dracole1488():
    path = _root / 'corpora/german/DTA/1488_nn_dracole/1488_nn_dracole.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Kaspar Has, Eyn new gedicht der loblichen Stat Nürmberg (1490;
# Nürnberg civic-praise poem, 742 rhymed verse lines).
@_register('has1490')
def _load_has1490():
    path = _root / 'corpora/german/DTA/1490_has_lob/1490_has_lob.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Der fußpfadt zu der ewigen seligkeyt (1492; anonymous devotional work,
# "The footpath to eternal salvation").
@_register('fusspfad1492')
def _load_fusspfad1492():
    path = _root / 'corpora/german/DTA/1492_nn_fusspfad/1492_nn_fusspfad.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Anonymous 1492 almanac (DTA nn_almanach04_1492).
@_register('almanach1492')
def _load_almanach1492():
    path = _root / 'corpora/german/DTA/1492_nn_almanach04/1492_nn_almanach04.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Friedrich Morgener, Walfart in sant Thomas land (1497; chivalric pilgrimage
# ballad in stanzas).
@_register('morgener1497')
def _load_morgener1497():
    path = _root / 'corpora/german/DTA/1497_oa_morgener/1497_oa_morgener.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Von ritter gotfrid wie er sein weib erlöst (1497; anonymous chivalric
# rescue ballad).
@_register('gottfried1497')
def _load_gottfried1497():
    path = _root / 'corpora/german/DTA/1497_nn_gottfried/1497_nn_gottfried.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Rechnungsbuch (1500; ledger entries — grain sales / receipts in pounds,
# pennings, schillings; Regensburg-area). Each row is one ledger item.
@_register('rechnungsbuch1500')
def _load_rechnungsbuch1500():
    path = _root / 'corpora/german/DTA/1500_rechnungsbuch01/1500_rechnungsbuch01.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Kunz Has, Hierin vindet mon die vrsach (1500; Nürnberg verse satire on
# the corruption of the world; same author as has1490).
@_register('has1500')
def _load_has1500():
    path = _root / 'corpora/german/DTA/1500_has_welt/1500_has_welt.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Kunz Has, Ein ſpruch vonn einem pecken knecht (1516; Nürnberg verse
# narrative on a Vienna mass murder; same author as has1490, has1500).
@_register('has1516')
def _load_has1516():
    path = _root / 'corpora/german/DTA/1516_has_spruch/1516_has_spruch.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Martin Bucer, Das ym selbs (1521; early Reformation dialogue between
# parishioners — Pfarrer, Schultheyß — on faith and works).
@_register('bucer1521')
def _load_bucer1521():
    path = _root / 'corpora/german/DTA/1521_bucer_dialogus/1521_bucer_dialogus.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Luther, Passional Christi und Antichristi (1521; polemical pamphlet
# contrasting Christ with the Pope, with woodcuts).
@_register('luther_passional1521')
def _load_luther_passional1521():
    path = _root / 'corpora/german/DTA/1521_luther_passional/1521_luther_passional.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Luther, Das Newe Testament Deutzsch (1522; the "September Testament" —
# Luther's German translation of the New Testament). DTA-pipeline parse;
# the legacy hand-coded entry is `luther`.
@_register('luther1522')
def _load_luther1522():
    path = _root / 'corpora/german/DTA/1522_luther_septembertestament/1522_luther_septembertestament.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Antonius Corvinus, Warhafftig bericht (1529; Wittenberg-printed report
# on the Reformation in Goslar and Braunschweig).
@_register('corvinus1529')
def _load_corvinus1529():
    path = _root / 'corpora/german/DTA/1529_corvinus_bericht/1529_corvinus_bericht.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Luther, Eyn Enchiridion oder Handbüchlein (1524; early devotional /
# prayer handbook, precursor to the Small Catechism).
@_register('luther_enchiridion1524')
def _load_luther_enchiridion1524():
    path = _root / 'corpora/german/DTA/1524_luther_enchiridion/1524_luther_enchiridion.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Luther, Das Elltern die kinder zur Ehe nicht zwingen (1524; pastoral
# tract on parental authority and marriage consent).
@_register('luther_elltern1524')
def _load_luther_elltern1524():
    path = _root / 'corpora/german/DTA/1524_luther_elltern/1524_luther_elltern.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Luther, 95 Theses (1557 German edition; Disputatio pro declaratione
# virtutis indulgentiarum, German translation by Luther).
@_register('luther_thesen1557')
def _load_luther_thesen1557():
    path = _root / 'corpora/german/DTA/1557_luther_thesen/1557_luther_thesen.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Alexius Crosner, Ein Sermon vom Hochwirdigen heiligen Sacrament
# (1531; Wittenberg sermon on the Eucharist, with preface by Luther).
@_register('crosner_sacrament1531')
def _load_crosner_sacrament1531():
    path = _root / 'corpora/german/DTA/1531_crosner_sermon/1531_crosner_sermon.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Anonym, Newe zeyttung (1535; news pamphlet on the fall of Münster on
# 25 June 1535, ending the Anabaptist kingdom).
@_register('zeyttung1535')
def _load_zeyttung1535():
    path = _root / 'corpora/german/DTA/1535_anonym_zeyttung/1535_anonym_zeyttung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Erhard Schnepf, Ordnung in Eesachen (1536; Württemberg marriage
# ordinance / ecclesiastical regulation on betrothal and divorce).
@_register('schnepf1536')
def _load_schnepf1536():
    path = _root / 'corpora/german/DTA/1536_schnepf_eesachen/1536_schnepf_eesachen.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Alexius Crosner, Ein Sermon von der heiligen Christlichen Kirchen
# (1531; Wittenberg sermon on the Reformation church, with preface by
# Luther).
@_register('crosner_kirchen1531')
def _load_crosner_kirchen1531():
    path = _root / 'corpora/german/DTA/1531_crosner_sermon2/1531_crosner_sermon2.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Splendor Solis (1590; anonymous German alchemical treatise; same text
# as the legacy `splendor`/`splendor0`, parsed via the DTA pipeline).
@_register('splendorsolis1590')
def _load_splendorsolis1590():
    path = _root / 'corpora/german/DTA/1590_nn_splendorsolis/1590_nn_splendorsolis.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# =============================================================================
# English: EEBO-TCP pipeline. Each text is one TCP ID; Phase I texts are CC0.
# =============================================================================

# Caxton, Recuyell of the Historyes of Troye (1473; TCP A05232). First book
# printed in English.
@_register('caxton_troye_1473')
def _load_caxton_troye_1473():
    path = _root / 'corpora/english/EEBO/1473_caxton_troye/1473_caxton_troye.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Caxton, Game and Playe of the Chesse (1474; TCP A18343). Caxton's
# second printed book, translation of Cessolis.
@_register('caxton_chesse_1474')
def _load_caxton_chesse_1474():
    path = _root / 'corpora/english/EEBO/1474_caxton_chesse/1474_caxton_chesse.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Caxton, Parvus Catho (1476; TCP A18231). Bilingual Latin/English print
# of the Distichs of Cato; build.py promotes the Latin distichs from
# <lg><head>/<l> into leading <l> siblings so the body rows interleave
# Latin and English in original reading order.
@_register('caxton_cato_1476')
def _load_caxton_cato_1476():
    path = _root / 'corpora/english/EEBO/1476_caxton_cato/1476_caxton_cato.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Lydgate, Stans puer ad mensam (1476; TCP A06567). Caxton's print of
# Lydgate's Middle English courtesy poem on table manners.
@_register('lydgate_stans_1476')
def _load_lydgate_stans_1476():
    path = _root / 'corpora/english/EEBO/1476_lydgate_stans/1476_lydgate_stans.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Lydgate, The Horse, the Goose, and the Sheep (1477; TCP A06553).
# Caxton's print of Lydgate's Middle English debate poem.
@_register('lydgate_horsegoosesheep_1477')
def _load_lydgate_horsegoosesheep_1477():
    path = _root / 'corpora/english/EEBO/1477_lydgate_horsegoosesheep/1477_lydgate_horsegoosesheep.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Dictes or Sayings of the Philosophers (1477; TCP A69207). Caxton's
# print of Earl Rivers' English translation; collected sayings of
# ancient philosophers (one of Caxton's most important early prints).
@_register('dictes_1477')
def _load_dictes_1477():
    path = _root / 'corpora/english/EEBO/1477_dictes/1477_dictes.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Caxton, Parvus Catho — 1477 edition (TCP A18230). Bilingual Latin/
# English print of the Distichs of Cato; distinct TEI encoding from the
# 1476 edition (`<l>` siblings under `<div>`, no `<lg>` wrapping —
# build.py wraps them in `<lg>` so the parser includes them).
@_register('caxton_cato_1477')
def _load_caxton_cato_1477():
    path = _root / 'corpora/english/EEBO/1477_caxton_cato/1477_caxton_cato.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Chaucer, Parliament of Fowls (1477; TCP A18559). Caxton's print of a
# Chaucer collection opening with the Parliament of Fowls and including
# other short pieces (e.g. Lenvoy a Scogan).
@_register('chaucer_parliament_1477')
def _load_chaucer_parliament_1477():
    path = _root / 'corpora/english/EEBO/1477_chaucer_parliament/1477_chaucer_parliament.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Caxton, Sarum Pie advertisement (1477; TCP A18294). Single-broadside
# advertisement for the Sarum-Use liturgical "pyes"; the first printed
# English advertisement.
@_register('caxton_advertisement_1477')
def _load_caxton_advertisement_1477():
    path = _root / 'corpora/english/EEBO/1477_caxton_advertisement/1477_caxton_advertisement.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# Chaucer, Canterbury Tales (1477; TCP A18548). Caxton's first edition.
# Distinct from the legacy `chaucer` RefText, which is a different
# (modern-spelling) transcription.
@_register('chaucer_canterbury_1477')
def _load_chaucer_canterbury_1477():
    path = _root / 'corpora/english/EEBO/1477_chaucer_canterbury/1477_chaucer_canterbury.csv'
    return reftext.from_corpus_build_csv(path, language='english')


# eebo: combined RefText across all EEBO-TCP-pipeline English texts.
# Also exposed as `english` — `from voynpy.corpora import english` yields
# the full EEBO corpus (same instance). No `english_legacy` aggregate
# exists; `chaucer` and `wycliffe` remain standalone legacy RefTexts.
@_register('english')
def _load_english():
    return _get('eebo')


@_register('eebo')
def _load_eebo():
    parts = [(name, _get(name)) for name in ('caxton_troye_1473', 'caxton_chesse_1474', 'caxton_cato_1476', 'lydgate_stans_1476', 'lydgate_horsegoosesheep_1477', 'dictes_1477', 'caxton_cato_1477', 'chaucer_parliament_1477', 'caxton_advertisement_1477', 'chaucer_canterbury_1477')]
    tklist = [t for _, rt in parts for t in rt.tklist]
    charlist = list(''.join(tklist))
    rt = reftext.RefText('english', tklist, charlist)
    rt.df = pd.concat(
        [p.df.assign(doc=name) for name, p in parts],
        ignore_index=True,
    )[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    return rt


# dta: combined RefText across all corpus_build-pipeline DTA texts.
# Also exposed as `german` — so `from voynpy.corpora import german` yields
# the full DTA corpus (same instance). The older hand-coded aggregate is
# `german_legacy`.
@_register('german')
def _load_german():
    return _get('dta')


@_register('dta')
def _load_dta():
    parts = [(name, _get(name)) for name in ('brunfels', 'almanach1473', 'dracole1485', 'meerwunder1472', 'almanach1481', 'promptuarium1483', 'kuchemaistrey1490', 'crescentiis1493', 'springer1509', 'ellenbog1524', 'tzeen1530', 'almanach1487', 'dracole1488', 'has1490', 'fusspfad1492', 'almanach1492', 'morgener1497', 'gottfried1497', 'rechnungsbuch1500', 'has1500', 'has1516', 'luther_passional1521', 'bucer1521', 'luther1522', 'luther_enchiridion1524', 'luther_elltern1524', 'corvinus1529', 'crosner_sacrament1531', 'crosner_kirchen1531', 'zeyttung1535', 'schnepf1536', 'luther_thesen1557', 'splendorsolis1590')]
    tklist = [t for _, rt in parts for t in rt.tklist]
    charlist = list(''.join(tklist))
    rt = reftext.RefText('german', tklist, charlist)
    rt.df = pd.concat(
        [p.df.assign(doc=name) for name, p in parts],
        ignore_index=True,
    )[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    return rt

# German legacy: aggregate of the three hand-coded pre-DTA texts. `german`
# itself now points to the DTA combined reftext (see lazy loader above).
reftext_list = [simp, kuche, promptuarium]
namelist = ['simp','kuche','prom']

german_legacy_df = pd.DataFrame()
for obj, name in zip(reftext_list, namelist):
    opus_df = obj.df.copy()
    opus_df.columns = ['line', 'textstring']
    opus_df['op'] = name
    opus_df = opus_df[['op','line','textstring']]
    german_legacy_df = pd.concat([german_legacy_df, opus_df], ignore_index = True)

german_legacy_fulltext = ' '.join([k for k in german_legacy_df.textstring])
german_legacy_tklist = [''.join([k for k in word if k.isalpha()]) for word in german_legacy_fulltext.split()]
german_legacy_charlist = list(''.join(german_legacy_tklist))
german_legacy = reftext.RefText('german', german_legacy_tklist, german_legacy_charlist)
german_legacy.df = german_legacy_df


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


