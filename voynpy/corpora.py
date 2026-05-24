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
caesarpath = _root / 'corpora/latin/legacy/caesar/caesar_lat0.csv'
caesar = reftext.from_textstring_csv(caesarpath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Vitruvius: De architectura
vitruviuspath = _root / 'corpora/latin/legacy/vitruvius/vitruvius_lat0.csv'
vitruvius = reftext.from_textstring_csv(vitruviuspath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Celsus: De medicina
celsuspath = _root / 'corpora/latin/legacy/celsus/celsus_lat0.csv'
celsus = reftext.from_textstring_csv(celsuspath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# Pliny: Naturalis historia
plinypath = _root / 'corpora/latin/legacy/pliny/pliny_lat0.csv'
pliny = reftext.from_textstring_csv(plinypath, language = 'latin', read_from_col = 1, comma_split_tokens = False)

# `latin` is registered below as a lazy loader (Corpus Corporum + classical legacy
# minus the Pliny duplicate). See the `@_register('latin')` block further down.

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


# === Batch 3 (1552–1579): post-Reformation German prose. =====================

# Hans Sachs, "Die kunigin peschlieff ein merwunder" (1552;
# Meistergesang on a queen + sea monster, MG 13 fol. 35r–35v).
@_register('sachs_meerwunder1552a')
def _load_sachs_meerwunder1552a():
    path = _root / 'corpora/german/DTA/1552_sachs_meerwunder1/1552_sachs_meerwunder1.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Württemberg, Newe Landtsordnung (1552; territorial law code,
# revised and expanded edition).
@_register('wuerttemberg1552')
def _load_wuerttemberg1552():
    path = _root / 'corpora/german/DTA/1552_wuerttemberg_landtsordnung/1552_wuerttemberg_landtsordnung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Johannes Brenz, Kirchenordnung (1555; church ordinance for the
# Duchy of Württemberg; doctrine + ceremony).
@_register('brenz_kirchenordnung1555')
def _load_brenz_kirchenordnung1555():
    path = _root / 'corpora/german/DTA/1555_brenz_kirchenordnung/1555_brenz_kirchenordnung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Hans Staden, Warhaftige Historia und beschreibung eyner Landtschafft
# der Wilden (1557; first-hand German account of Brazil and Tupinambá
# captivity).
@_register('staden1557')
def _load_staden1557():
    path = _root / 'corpora/german/DTA/1557_staden_landschafft/1557_staden_landschafft.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Heinrich Bullinger, Haußbuoch (1558; Zürich Reformed home-and-faith
# manual, by far the largest text in this batch ~20k rows).
@_register('bullinger1558')
def _load_bullinger1558():
    path = _root / 'corpora/german/DTA/1558_bullinger_haussbuoch/1558_bullinger_haussbuoch.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Hans Sachs, "Die irrfart Ulissi mit den Werbern und seiner gemahel
# Penelope" (written 1555, this edition 1561; Meistergesang Odyssey
# adaptation).
@_register('sachs_ulisses1561')
def _load_sachs_ulisses1561():
    path = _root / 'corpora/german/DTA/1561_sachs_ulisses/1561_sachs_ulisses.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Hans Sachs, "Königin Deudalinda mit dem Meerwunder" (1562;
# Meistergesang SG 15 fol. 104ff.).
@_register('sachs_meerwunder1562')
def _load_sachs_meerwunder1562():
    path = _root / 'corpora/german/DTA/1562_sachs_meerwunder2/1562_sachs_meerwunder2.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Melchior Walther, Ein Einfaltiger Vnd Christlicher Sermon oder
# Leichpredigt (1562; funeral sermon).
@_register('walther1562')
def _load_walther1562():
    path = _root / 'corpora/german/DTA/1562_walther_sermon/1562_walther_sermon.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Jacob Andreä, Ein Christliche Predig über der Leich (1564;
# funeral sermon).
@_register('andrea1564')
def _load_andrea1564():
    path = _root / 'corpora/german/DTA/1564_andrea_predig/1564_andrea_predig.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Anonymous, Kirchenordnung (1564; church ordinance, doctrine +
# sacraments).
@_register('kirchenordnung1564')
def _load_kirchenordnung1564():
    path = _root / 'corpora/german/DTA/1564_nn_kirchenordnung/1564_nn_kirchenordnung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Johannes Brenz, Kirchenordnung (1565; second Brenz ordinance in
# our corpus, distinct from 1555).
@_register('brenz_kirchenordnung1565')
def _load_brenz_kirchenordnung1565():
    path = _root / 'corpora/german/DTA/1565_brenz_kirchenordnung/1565_brenz_kirchenordnung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Braunschweig-Wolfenbüttel, Kirchenordnung (1569; church ordinance
# issued by Duke Julius).
@_register('braunschweig_kirchenordnung1569')
def _load_braunschweig_kirchenordnung1569():
    path = _root / 'corpora/german/DTA/1569_braunschweig_kirchenordnung/1569_braunschweig_kirchenordnung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Timotheus Kirchner, Bekentnis Von der Rechtfertigung (1569;
# confessional treatise on justification and good works).
@_register('kirchner_bekentnis1569')
def _load_kirchner_bekentnis1569():
    path = _root / 'corpora/german/DTA/1569_kirchner_bekentnis/1569_kirchner_bekentnis.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Braunschweig-Wolfenbüttel, Hofgerichtsordnung (1571; ducal court
# procedural code).
@_register('braunschweig_hofgerichtsordnung1571')
def _load_braunschweig_hofgerichtsordnung1571():
    path = _root / 'corpora/german/DTA/1571_braunschweig_hofgerichtsordnung/1571_braunschweig_hofgerichtsordnung.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Gallus Etschenreutter, Aller heilsamen Bäder vnd Brunnen Natur (1571;
# balneological / medicinal-springs treatise; high `item` block ratio
# reflects structured spring-by-spring listings).
@_register('etschenreutter1571')
def _load_etschenreutter1571():
    path = _root / 'corpora/german/DTA/1571_etschenreutter_baeder/1571_etschenreutter_baeder.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Nikolaus Selnecker, Kurtze Bekantnus (1571; brief confessional
# statement).
@_register('selnecker_bekantnus1571')
def _load_selnecker_bekantnus1571():
    path = _root / 'corpora/german/DTA/1571_selnecker_bekantnus/1571_selnecker_bekantnus.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Nikolaus Selnecker, Summa der warhafftigen Lehre (1571; companion
# longer confessional summary).
@_register('selnecker_summa1571')
def _load_selnecker_summa1571():
    path = _root / 'corpora/german/DTA/1571_selnecker_summa/1571_selnecker_summa.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Braunschweig-Wolfenbüttel, Repetition und Erklerung (1574;
# confessional restatement of public Schriften and Confessionen).
@_register('braunschweig_repetition1574')
def _load_braunschweig_repetition1574():
    path = _root / 'corpora/german/DTA/1574_braunschweig_repetition/1574_braunschweig_repetition.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Laurentius Dresserus, Leichpredigt (1578; funeral sermon).
@_register('dresserus1578')
def _load_dresserus1578():
    path = _root / 'corpora/german/DTA/1578_dresserus_leichpredigt/1578_dresserus_leichpredigt.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Tilemann Hesshus, Bekandtnus Von der Formula Concordiae (1578;
# anti-Formula-of-Concord confessional polemic).
@_register('hesshus1578')
def _load_hesshus1578():
    path = _root / 'corpora/german/DTA/1578_hesshus_bekendtnus/1578_hesshus_bekendtnus.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Anonymous, Erdichte Lesterschrifft (1578; defense of Hesshus against
# a "fabricated slanderous tract").
@_register('lesterschrifft1578')
def _load_lesterschrifft1578():
    path = _root / 'corpora/german/DTA/1578_nn_lesterschrifft/1578_nn_lesterschrifft.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Timotheus Kirchner, Zeugnusse und Aussage von D. Jacobs Andree
# Einigkeit (1579; theological controversy text).
@_register('kirchner_zeugnusse1579')
def _load_kirchner_zeugnusse1579():
    path = _root / 'corpora/german/DTA/1579_kirchner_zeugnusse/1579_kirchner_zeugnusse.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# Anonymous, Der Stadt Braunschweig Ordnung (1579; Braunschweig
# religious + civic ordinance).
@_register('braunschweig_ordnung1579')
def _load_braunschweig_ordnung1579():
    path = _root / 'corpora/german/DTA/1579_nn_braunschweig/1579_nn_braunschweig.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# === end Batch 3 ============================================================


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


# Luther Bibel 1545 (Zeno.org; Gemeinfrei). The complete 1545 Bible —
# 66+ books OT/NT/Apocrypha plus Luther's prefaces — at ~850k tokens.
@_register('luther_bible_1545')
def _load_luther_bible_1545():
    path = _root / 'corpora/german/zeno/luther_bible_1545/luther_bible_1545.csv'
    return reftext.from_corpus_build_csv(path, language='german')


# `german` aggregate: DTA German + Luther Bibel 1545 (combined ~2.3M tokens
# across both corpus_build pipelines). The standalone `dta` loader remains
# DTA-only for DTA-specific statistics; `luther_bible_1545` likewise stands
# alone. The older hand-coded aggregate is `german_legacy`.
@_register('german')
def _load_german():
    dta_rt = _get('dta')
    lb_rt = _get('luther_bible_1545')
    lb_df = lb_rt.df.copy()
    lb_df['doc'] = 'luther_bible_1545'
    lb_df = lb_df[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    tklist = list(dta_rt.tklist) + list(lb_rt.tklist)
    charlist = list(''.join(tklist))
    rt = reftext.RefText('german', tklist, charlist)
    rt.df = pd.concat([dta_rt.df, lb_df], ignore_index=True)
    return rt


# DBNL Dutch texts. Each text has its own loader; aggregates `dbnl` and
# `dutch` are defined below — they are identical (alias pattern) and
# cover all DBNL-pipeline Dutch texts.

@_register('alexander1477')
def _load_alexander1477():
    path = _root / 'corpora/dutch/DBNL/1477_alexander/1477_alexander.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('souen_wysen1478')
def _load_souen_wysen1478():
    path = _root / 'corpora/dutch/DBNL/1478_souen_wysen/1478_souen_wysen.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('parijs_ende_vienna1487')
def _load_parijs_ende_vienna1487():
    path = _root / 'corpora/dutch/DBNL/1487_parijs_ende_vienna/1487_parijs_ende_vienna.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('arent_bosman1488')
def _load_arent_bosman1488():
    path = _root / 'corpora/dutch/DBNL/1488_arent_bosman/1488_arent_bosman.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


# Ars moriendi 1488 (Peter van Os, Zwolle; DBNL pipeline; TEI Lite source).
# Anonymous Middle Dutch *art of dying* treatise. Diplomatic transcription
# preserves period orthography (uu-as-v digraph in `duuel`, `gh-` clusters,
# `ij` digraph etc.).
@_register('ars_moriendi1488')
def _load_ars_moriendi1488():
    path = _root / 'corpora/dutch/DBNL/1488_ars_moriendi/1488_ars_moriendi.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('voghelen_vanghen1509')
def _load_voghelen_vanghen1509():
    path = _root / 'corpora/dutch/DBNL/1509_voghelen_vanghen/1509_voghelen_vanghen.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('ix_quaesten1528')
def _load_ix_quaesten1528():
    path = _root / 'corpora/dutch/DBNL/1528_ix_quaesten/1528_ix_quaesten.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('excellente_chronijck1531')
def _load_excellente_chronijck1531():
    path = _root / 'corpora/dutch/DBNL/1531_excellente_chronijck/1531_excellente_chronijck.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('luther_slotelen1531')
def _load_luther_slotelen1531():
    path = _root / 'corpora/dutch/DBNL/1531_luther_slotelen/1531_luther_slotelen.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('vorsterman_bijbel1531')
def _load_vorsterman_bijbel1531():
    path = _root / 'corpora/dutch/DBNL/1531_vorsterman_bijbel/1531_vorsterman_bijbel.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('souterliedekens1540')
def _load_souterliedekens1540():
    path = _root / 'corpora/dutch/DBNL/1540_souterliedekens/1540_souterliedekens.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


@_register('ridderlycke_reyse1544')
def _load_ridderlycke_reyse1544():
    path = _root / 'corpora/dutch/DBNL/1544_ridderlycke_reyse/1544_ridderlycke_reyse.csv'
    return reftext.from_corpus_build_csv(path, language='dutch')


# dbnl: combined RefText across all DBNL-pipeline Dutch texts.
# Also exposed as `dutch` — `from voynpy.corpora import dutch` yields the
# full DBNL corpus (same instance).
@_register('dutch')
def _load_dutch():
    return _get('dbnl')


_DBNL_TEXTS: tuple[str, ...] = (
    'alexander1477',
    'souen_wysen1478',
    'parijs_ende_vienna1487',
    'arent_bosman1488',
    'ars_moriendi1488',
    'voghelen_vanghen1509',
    'ix_quaesten1528',
    'excellente_chronijck1531',
    'luther_slotelen1531',
    'vorsterman_bijbel1531',
    'souterliedekens1540',
    'ridderlycke_reyse1544',
)


@_register('dbnl')
def _load_dbnl():
    parts = [(name, _get(name)) for name in _DBNL_TEXTS]
    tklist = [t for _, rt in parts for t in rt.tklist]
    charlist = list(''.join(tklist))
    rt = reftext.RefText('dutch', tklist, charlist)
    rt.df = pd.concat(
        [p.df.assign(doc=name) for name, p in parts],
        ignore_index=True,
    )[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    return rt


@_register('dta')
def _load_dta():
    parts = [(name, _get(name)) for name in ('brunfels', 'almanach1473', 'dracole1485', 'meerwunder1472', 'almanach1481', 'promptuarium1483', 'kuchemaistrey1490', 'crescentiis1493', 'springer1509', 'ellenbog1524', 'tzeen1530', 'almanach1487', 'dracole1488', 'has1490', 'fusspfad1492', 'almanach1492', 'morgener1497', 'gottfried1497', 'rechnungsbuch1500', 'has1500', 'has1516', 'luther_passional1521', 'bucer1521', 'luther1522', 'luther_enchiridion1524', 'luther_elltern1524', 'corvinus1529', 'crosner_sacrament1531', 'crosner_kirchen1531', 'zeyttung1535', 'schnepf1536', 'luther_thesen1557', 'splendorsolis1590', 'sachs_meerwunder1552a', 'wuerttemberg1552', 'brenz_kirchenordnung1555', 'staden1557', 'bullinger1558', 'sachs_ulisses1561', 'sachs_meerwunder1562', 'walther1562', 'andrea1564', 'kirchenordnung1564', 'brenz_kirchenordnung1565', 'braunschweig_kirchenordnung1569', 'kirchner_bekentnis1569', 'braunschweig_hofgerichtsordnung1571', 'etschenreutter1571', 'selnecker_bekantnus1571', 'selnecker_summa1571', 'braunschweig_repetition1574', 'dresserus1578', 'hesshus1578', 'lesterschrifft1578', 'kirchner_zeugnusse1579', 'braunschweig_ordnung1579')]
    tklist = [t for _, rt in parts for t in rt.tklist]
    charlist = list(''.join(tklist))
    rt = reftext.RefText('german', tklist, charlist)
    rt.df = pd.concat(
        [p.df.assign(doc=name) for name, p in parts],
        ignore_index=True,
    )[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    return rt


# =============================================================================
# Corpus Corporum (UZH, mlat.uzh.ch) — Auctores scientiarum varii (67 texts).
# Each cc_<author>_<work> name loads a single CC text on demand.
# `latin_corpus_corporum` aggregates all 67.
# =============================================================================

_CC_AUCTORES_BASE = _root / 'corpora/latin/CorpusCorporum/auctores_scientiarum_varii'

_CC_AUCTORES: tuple[tuple[str, str, str], ...] = (
    # (reg_name, author_slug, work_slug)
    ('cc_alanus_merlini',              'alanus_de_insulis',           'explanatio_in_prophetia_merlini_ambrosii'),
    ('cc_aurelii',                     'anonymus',                    'liber_aurelii'),
    ('cc_aurelii_abbrev',              'anonymus',                    'liber_aurelii_versio_abbreviata'),
    ('cc_rhetorica_herennium',         'anonymus',                    'rhetorica_ad_herennium'),
    ('cc_augustinus_dialectica',       'augustinus_hipponensis',      'de_dialectica'),
    ('cc_avienus_ora_maritima',        'avienus_rufius_festus',       'ora_maritima'),
    ('cc_avienus_periegesis',          'avienus_rufius_festus',       'periegesis_seu_descriptio_orbis_terrarum'),
    ('cc_balbus_expositio',            'balbus',                      'expositio_et_ratio_omnium_formarum'),
    ('cc_bernardus_crisi',             'bernardus_gordonensis',       'tractatus_de_crisi_et_de_diebus_creticis'),
    ('cc_cardanus_subtilitate',        'cardanus_hieronymus',         'de_subtilitate'),
    ('cc_cato_re_rustica',             'cato',                        'de_re_rustica_vel_de_agri_cultura'),
    ('cc_cicero_legibus',              'cicero',                      'de_legibus'),
    ('cc_cicero_arati',                'cicero',                      'translatio_arati_phaenomenorum'),
    ('cc_galenus_pulsibus',            'claudius_galenus',            'synopsis_librorum_suorum_de_pulsibus'),
    ('cc_copernicus_revolutione',      'copernicus_nicolaus',         'de_revolutione_orbium_caelestium_liber_primus'),
    ('cc_erasmus_adagia',              'desiderius_erasmus',          'adagia'),
    ('cc_dicuil_mensura',              'dicuil',                      'de_mensura_orbis_terrae'),
    ('cc_schleusinger_cometis',        'eberhard_schleusinger',       'de_cometis'),
    ('cc_frontinus_aquis',             'frontinus_sextus_iulius',     'de_aquis'),
    ('cc_frontinus_strategemata',      'frontinus_sextus_iulius',     'strategemata'),
    ('cc_fronto_epistulae',            'fronto',                      'epistulae'),
    ('cc_gaius_institutiones',         'gaius',                       'institutiones'),
    ('cc_gariopontus_passionarius',    'gariopontus',                 'passionarius_vel_de_febribus_liber_v_i_xv'),
    ('cc_gerhardus_de_causis',         'gerhardus_cremonensis',       'liber_de_causis'),
    ('cc_gualterus_mahomete',          'gualterus_compendiensis',     'otia_de_mahomete'),
    ('cc_guilelmus_philosophia',       'guilelmus_de_conchis',        'de_philosophia'),
    ('cc_hyginus_astronomia',          'hyginus',                     'de_astronomia'),
    ('cc_hyginus_fabulae',             'hyginus',                     'fabulae'),
    ('cc_sacrobosco_sphaera',          'iohannes_de_sacrobosco',      'de_sphaera'),
    ('cc_sacrobosco_numerandi',        'iohannes_de_sacrobosco',      'tractatus_de_arte_numerandi'),
    ('cc_isidorus_etymologiae',        'isidorus_hispalensis',        'etymologiae'),
    ('cc_iustinianus_digesta',         'iustinianus',                 'digesta_iustiniani_augusti'),
    ('cc_firmicus_mathesis',           'julius_firmicus_maternus',    'mathesis'),
    ('cc_lambertus_aristotelis',       'lambertus_de_monte',          'de_salvatione_aristotelis'),
    ('cc_lavater_spectris',            'lavater_ludwig',              'de_spectris'),
    ('cc_macer_herbarum',              'macer_floridus',              'de_viribus_herbarum'),
    ('cc_manilius_astronomica',        'manilius',                    'astronomica'),
    ('cc_moneta_catharos',             'moneta_cremonensis',          'adversus_catharos_et_valdenses'),
    ('cc_cusanus_apologia',            'nicolaus_cusanus',            'apologia_doctae_ignorantiae'),
    ('cc_cusanus_beryllo',             'nicolaus_cusanus',            'de_beryllo'),
    ('cc_cusanus_coniecturis',         'nicolaus_cusanus',            'de_coniecturis'),
    ('cc_cusanus_docta_ignorantia',    'nicolaus_cusanus',            'de_docta_ignorantia'),
    ('cc_cusanus_mathematica',         'nicolaus_cusanus',            'de_mathematica_perfectione'),
    ('cc_cusanus_non_aliud',           'nicolaus_cusanus',            'de_non_aliud'),
    ('cc_cusanus_apice',               'nicolaus_cusanus',            'dialogus_de_apice_theoriae'),
    ('cc_cusanus_abscondito',          'nicolaus_cusanus',            'dialogus_de_deo_abscondito'),
    ('cc_cusanus_idiota_mente',        'nicolaus_cusanus',            'idiota_de_mente'),
    ('cc_cusanus_possest',             'nicolaus_cusanus',            'trialogus_de_possest'),
    ('cc_oresmius_proportionibus',     'oresmius_nicolaus',           'de_proportionibus_proportionum'),
    ('cc_plinius_naturalis_historia',  'plinius_maior',               'naturalis_historia'),
    ('cc_mela_chorographia',           'pomponius_mela',              'de_chorographia'),
    ('cc_ps_caesar_africo',            'ps_caesar',                   'de_bello_africo'),
    ('cc_ps_caesar_alexandrino',       'ps_caesar',                   'de_bello_alexandrino'),
    ('cc_ps_caesar_hispaniensi',       'ps_caesar',                   'de_bello_hispaniensi'),
    ('cc_ps_galenus_glauconem',        'ps_galenus',                  'ad_glauconem_liber_tertius'),
    ('cc_ps_galenus_pulsibus',         'ps_galenus',                  'de_pulsibus_ad_antonium'),
    ('cc_sammonicus_medicinalis',      'quintus_serenus_sammonicus',  'liber_medicinalis'),
    ('cc_baco_opus_majus',             'rogerus_baco',                'opus_majus'),
    ('cc_baco_opus_tertium',           'rogerus_baco',                'opus_tertium'),
    ('cc_baco_secretum',               'rogerus_baco',                'secretum_secretorum'),
    ('cc_seneca_naturales',            'seneca',                      'naturales_quaestiones'),
    ('cc_solinus_mirabilibus',         'solinus',                     'de_mirabilibus_mundi'),
    ('cc_suetonius_illustribus',       'suetonius',                   'de_viris_illustribus'),
    ('cc_varro_agricultura',           'varro',                       'de_agricultura'),
    ('cc_varro_lingua',                'varro',                       'de_lingua_latina'),
    ('cc_velleius_historiae',          'velleius',                    'historiae_romanae'),
    ('cc_witelo_perspectiva',          'witelo',                      'de_perspectiva_lib_1'),
)


def _make_cc_loader(author_slug: str, work_slug: str):
    def _load():
        path = _CC_AUCTORES_BASE / author_slug / work_slug / f"{work_slug}.csv"
        return reftext.from_corpus_build_csv(path, language='latin')
    return _load


for _reg_name, _author, _work in _CC_AUCTORES:
    _LOADERS[_reg_name] = _make_cc_loader(_author, _work)


@_register('latin_corpus_corporum')
def _load_latin_corpus_corporum():
    parts = [(name, _get(name)) for name, _, _ in _CC_AUCTORES]
    tklist = [t for _, rt in parts for t in rt.tklist]
    charlist = list(''.join(tklist))
    rt = reftext.RefText('latin', tklist, charlist)
    rt.df = pd.concat(
        [p.df.assign(doc=name) for name, p in parts],
        ignore_index=True,
    )[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    return rt


@_register('ellis_1854')
def _load_ellis_1854():
    """Ellis 1854 *Medical Formulary* — apothecary recipes.

    Sentence-level CSV matches `voynpy.corpus_build.schema` with an
    extra `heading` column. Each Ellis recipe is one paragraph (para_id);
    each line of a recipe is one sentence (sent_id).
    """
    path = _root / 'corpora/latin/apothecary/ellis_1854/ellis_1854.csv'
    return reftext.from_corpus_build_csv(path, language='latin')


# `latin` = Corpus Corporum (67 texts) + classical legacy (Caesar, Vitruvius,
# Celsus) + Ellis 1854 apothecary recipes. The legacy Pliny is intentionally
# omitted: CC includes the same Naturalis historia as
# cc_plinius_naturalis_historia, and that edition is preferred (corpus_build
# pipeline, structural metadata).
@_register('latin')
def _load_latin():
    cc = _get('latin_corpus_corporum')
    ellis = _get('ellis_1854')
    # Harmonize legacy classical .df into corpus_build schema so the combined
    # .df has one consistent column layout.
    def _legacy_to_corpus_build(rt, doc_name):
        df = rt.df.copy()
        df.columns = ['line', 'textstring']
        df['doc'] = doc_name
        df['idx'] = range(len(df))
        df['par'] = df.index + 1
        df['par_end'] = True
        return df[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    legacy_parts = [
        ('caesar', caesar),
        ('vitruvius', vitruvius),
        ('celsus', celsus),
    ]
    legacy_tklist = [t for _, rt in legacy_parts for t in rt.tklist]
    legacy_dfs = [_legacy_to_corpus_build(rt, name) for name, rt in legacy_parts]
    ellis_df = ellis.df.assign(doc='ellis_1854')[['doc', 'idx', 'par', 'line', 'par_end', 'textstring']]
    tklist = list(cc.tklist) + legacy_tklist + list(ellis.tklist)
    charlist = list(''.join(tklist))
    rt = reftext.RefText('latin', tklist, charlist)
    rt.df = pd.concat([cc.df, *legacy_dfs, ellis_df], ignore_index=True)
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


