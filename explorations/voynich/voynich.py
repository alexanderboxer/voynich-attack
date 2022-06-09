'''
voynich
'''
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
    """Reference text class"""

    nonalpha_keepers = ['.', '!', ';', '?', ':']

    def __init__(self, filepath, language):
        self.filepath = filepath
        self.language = language
        self.source = self._read_txt()
        self.wordstring = self._get_wordstring()
        self.tklist = self.wordstring.split()
        self.charlist = list(''.join(self.tklist))

    def _read_txt(self):
        with open(self.filepath, 'r') as f:
            s = f.read()
        return s

    def _get_wordstring(self):
        s = ' '.join([''.join([k for k in word if k.isalpha()]) for word in self.source.split()])
        return s

    def tkdf(self, order = 1):
        return self._ngram(self.tklist, order)

    def chardf(self, order = 1):
        return self._ngram(self.charlist, order)





caesarpath = '../../corpora/latin/caesar_bellogallico/caesar_bellogallico_alphaplus.txt'

caesar = RefText_txt(caesarpath, 'latin')

# ==============================================================================
# RefText_csv Child Class
# ==============================================================================

# ==============================================================================
# RefText Class
# ==============================================================================
class RefText:
    """Reference text class"""
    def __init__(self, filepath, read_from_col):
        self.filepath = filepath
        self.read_from_col = read_from_col
        self.df = self._read_csv()
        self.tklist = self._get_tklist()
        self.charlist = self._get_charlist()

    def _read_csv(self):
        df = pd.read_csv(self.filepath)
        return df

    def _get_tklist(self):
        nullchar = '$'
        tklist = [k for k in self.df.iloc[:,self.read_from_col:].fillna(nullchar).to_numpy().flatten() if k != nullchar]
        return tklist

    def _get_charlist(self):
        charlist = ','.join(self.tklist).split(',')
        return charlist

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
        return ndf

    def tkdf(self, order = 1):
        return self._ngram(self.tklist, order)

    def chardf(self, order = 1):
        return self._ngram(self.charlist, order)

# ==============================================================================
# Instantiate
# ==============================================================================
vmspath = '../../transcription/vms.csv'

vms = RefText(vmspath, read_from_col = 3)
