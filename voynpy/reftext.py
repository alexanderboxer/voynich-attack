"""
Voynich reference text class
"""
# ==============================================================================
# Import
# ==============================================================================
from collections import Counter
import pandas as pd 

# ==============================================================================
# RefText class
# ==============================================================================
class RefText:
    """Reference text class"""

    def __init__(self, language, tklist, charlist):
        self.language = language
        self.tklist = tklist
        self.charlist = charlist

    def _get_charlist(self):
        charlist = list(''.join(self.tklist))
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
        ndf['gram'] = ['-'.join([*k]) for k in ndf.gram]
        ndf = ndf.sort_values('n', ascending = False).reset_index(drop = True)
        nsum = ndf.n.sum()
        ndf['pct'] = ['{:.2f}'.format(100*k/nsum) for k in ndf.n]
        return ndf

    def tkdf(self, order = 1):
        return self._ngram(self.tklist, order)

    def chardf(self, order = 1):
        return self._ngram(self.charlist, order)


# ==============================================================================
# Instantiation functions
# ==============================================================================
def from_string(s, language):
    tkstring = ' '.join([''.join([k for k in word if k.isalpha()]) for word in s.split()])
    tklist = tkstring.split()
    charlist = list(''.join(tklist))
    reftext = RefText(language, tklist, charlist)
    reftext.source = s
    return reftext

def from_txt(filepath, language):
    with open(filepath, 'r') as f:
        s = f.read()
    reftext = from_string(s, language)
    return reftext

def from_dataframe(dataframe, language, read_from_col = 0, comma_split_tokens = False):
    nullchar = '$'
    tklist = [k for k in dataframe.iloc[:,read_from_col:].fillna(nullchar).to_numpy().flatten() if k != nullchar]
    if comma_split_tokens:
        charlist = ','.join(tklist).split(',')
    else:
        charlist = list(''.join(tklist))
    reftext = RefText(language, tklist, charlist)
    reftext.df = dataframe
    return reftext

def from_csv(filepath, language, read_from_col = 0, comma_split_tokens = False):
    dataframe = pd.read_csv(filepath)
    reftext = from_dataframe(dataframe, language, read_from_col, comma_split_tokens)
    return reftext

def from_textstring_csv(filepath, language, read_from_col = 0, comma_split_tokens = False):
    dataframe = pd.read_csv(filepath)
    textstring =  dataframe.iloc[:,read_from_col:].astype(str).apply(' '.join)[0]
    tklist = [''.join([k for k in word if k.isalpha()]) for word in textstring.split()]
    if comma_split_tokens:
        charlist = ','.join(tklist).split(',')
    else:
        charlist = list(''.join(tklist))
    reftext = RefText(language, tklist, charlist)
    reftext.df = dataframe
    return reftext