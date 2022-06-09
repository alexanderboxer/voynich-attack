"""
Voynich reference text classes
"""
# ==============================================================================
# Import
# ==============================================================================
from collections import Counter
import pandas as pd 

# ==============================================================================
# RefText_base Base Class
# ==============================================================================
class RefText_base:
    """Reference text base class"""

    def _ngram(self, gramlist, order):
        order = max([1, order])
        N = len(gramlist)
        seqlist = list()
        for i in range(order):
            start_index = i
            stop_index = N + 1 - order + i
            seq = gramlist[start_index: stop_index]
            seqlist.append(seq)
        ndf = pd.DataFrame.from_dict(Counter(zip(*seqlist)), orient = 'index').reset_index()
        ndf.columns = ['gram', 'n']
        ndf['gram'] = [' - '.join([*k]) for k in ndf.gram]
        ndf = ndf.sort_values('n', ascending = False).reset_index(drop = True)
        nsum = ndf.n.sum()
        ndf['pct'] = ['{:.2f}'.format(100*k/nsum) for k in ndf.n]
        return ndf

    def tkdf(self, order = 1):
        return self._ngram(self.tklist, order)

    def chardf(self, order = 1):
        return self._ngram(self.charlist, order)

# ==============================================================================
# RefText_txt Child Class
# ==============================================================================
class RefText_txt(RefText_base):
    """Reference text child class / read from .txt file"""

    nonalpha_keepers = ['.', '!', ';', '?', ':']

    def __init__(self, filepath, language):
        self.filepath = filepath
        self.language = language
        self.source = self._read_txt()
        self.tklist = self._get_tklist()
        self.charlist = list(''.join(self.tklist))

    def _read_txt(self):
        with open(self.filepath, 'r') as f:
            s = f.read()
        return s

    def _get_tklist(self):
        tkstring = ' '.join([''.join([k for k in word if k.isalpha()]) for word in self.source.split()])
        tklist = tkstring.split()
        return tklist

# ==============================================================================
# RefText_csv Child Class
# ==============================================================================
class RefText_csv(RefText_base):
    """Reference text child class / read from .csv file"""

    def __init__(self, filepath, language, read_from_col):
        self.filepath = filepath
        self.language = language
        self.read_from_col = read_from_col
        self.df = pd.read_csv(self.filepath)
        self.tklist = self._get_tklist()
        self.charlist = ','.join(self.tklist).split(',')

    def _get_tklist(self):
        nullchar = '$'
        tklist = [k for k in self.df.iloc[:,self.read_from_col:].fillna(nullchar).to_numpy().flatten() if k != nullchar]
        return tklist

# ==============================================================================
# RefText_csv_alt Child Class
# ==============================================================================
class RefText_csv_alt(RefText_csv):
    """Reference text child class / read from .csv file / alt format: individual characters are not comma-separated"""

    def __init__(self, filepath, language, read_from_col):
        super().__init__(filepath, language, read_from_col)
        self.charlist = list(''.join([''.join([k for k in word if k.isalpha()]) for word in self.tklist]))

# ==============================================================================
# RefText_dataframe Child Class
# ==============================================================================
class RefText_dataframe(RefText_csv):
    """Reference text child class / instantiate directly from a pandas dataframe"""

    def __init__(self, dataframe, language, read_from_col):
        self.df = dataframe
        self.language = language
        self.read_from_col = read_from_col
        self.tklist = self._get_tklist()
        self.charlist = ','.join(self.tklist).split(',')

# ==============================================================================
# Instantiate reference text corpora
# ==============================================================================

# vms: full Voynich
vmspath = '../../transcription/vms.csv'
vms = RefText_csv(vmspath, language = 'voynich', read_from_col = 3)

# vms1: Voynich up to f103r
f013r_idx = vms.df[vms.df.folio == '103r'].index.tolist()[0]
vms1_df = vms.df.iloc[:f013r_idx].copy()
vms1 = RefText_dataframe(vms1_df, language = 'voynich', read_from_col = 3)

# vms2: Voynich from f103r
vms2_df = vms.df.iloc[f013r_idx:].copy()
vms2 = RefText_dataframe(vms2_df, language = 'voynich', read_from_col = 3)

# caesar: Caesar De Bello Gallico
caesarpath = '../../corpora/latin/caesar_bellogallico/caesar_bellogallico_lat0.txt'
caesar = RefText_txt(caesarpath, 'latin')

# heb: Torah
hebpath = '../../corpora/hebrew/torah/torah.txt'
heb = RefText_txt(hebpath, 'hebrew')

# enoch: MS 3188 Enochian 
enochpath = '../../corpora/enochian/ms3188.csv'
enoch = RefText_csv_alt(enochpath, 'enochian', read_from_col = 2)
