"""
Voynich reference text class
"""
# ==============================================================================
# Import
# ==============================================================================
from collections import Counter
import pandas as pd

from voynpy.corpus_build.normalize import to_latin0 as _to_latin0

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
    dataframe = pd.read_csv(filepath, dtype = str, keep_default_na = False)
    textstring =  dataframe.iloc[:,read_from_col:].astype(str).apply(' '.join).iloc[0]
    tklist = [''.join([k for k in word if k.isalpha()]) for word in textstring.split()]
    if comma_split_tokens:
        charlist = ','.join(tklist).split(',')
    else:
        charlist = list(''.join(tklist))
    reftext = RefText(language, tklist, charlist)
    reftext.df = dataframe
    return reftext

def from_textstring_csv_var1(filepath, language, read_from_col = 0, comma_split_tokens = False):
    dataframe = pd.read_csv(filepath, dtype = str, keep_default_na = False)
    textstring =  dataframe.iloc[:,read_from_col:].astype(str).apply(' '.join).iloc[0]
    tklist = [''.join([k for k in word if (k.isalpha() or k == '&')]) for word in textstring.split()]
    tklist = [k for k in tklist if k != '']
    if comma_split_tokens:
        charlist = ','.join(tklist).split(',')
    else:
        charlist = list(''.join(tklist))
    reftext = RefText(language, tklist, charlist)
    reftext.df = dataframe
    return reftext

def from_textstring_csv_lat0(filepath, language):
    dataframe = pd.read_csv(filepath, dtype = str, keep_default_na = False, index_col = 0)
    textstring =  ' '.join([k for k in dataframe.textstring])
    tklist = [''.join([k for k in word]) for word in textstring.split()]
    tklist = [k for k in tklist if k != '']
    charlist = list(''.join(tklist))
    reftext = RefText(language, tklist, charlist)
    reftext.df = dataframe
    return reftext

def from_corpus_build_csv(filepath, language, block_types=("body",),
                          text_column="textstring_simple", latin0_fold=True):
    """Load a RefText from a corpus_build pipeline CSV (one row per sentence).

    `block_types`: iterable of block types to include; None = all rows.
      Default `('body',)` keeps just the running prose, excluding heads etc.
    `text_column`: which normalized text column to use (default: textstring_simple).
    `latin0_fold`: when True (default), fold tklist/charlist to a-z via NFKD
      + manual map (so chardf reports only base Latin letters). Set False to
      preserve the text column's native glyphs — useful when loading
      `textstring_rich` to inspect the full character inventory (ß, ü, ẽ,
      ñ, đ, ď, combining tildes).

    The RefText's `.df` is a trimmed, analysis-focused frame with columns:
      idx        — zero-padded 'par.line' string that sorts correctly
      par        — paragraph id (int)
      line       — sentence id within paragraph (int)
      par_end    — bool, True iff this is the final line of its paragraph
      textstring — the chosen normalized text (from `text_column`)
    """
    raw = pd.read_csv(filepath, dtype=str, keep_default_na=False)
    if block_types is not None:
        raw = raw[raw["block_type"].isin(list(block_types))]
    par_ints = raw["para_id"].astype(int).values
    line_ints = raw["sent_id"].astype(int).values
    par_end_bools = raw["is_para_final"].str.lower().isin(["true", "1", "yes"]).values
    par_width = max((len(str(v)) for v in par_ints), default=1)
    line_width = max((len(str(v)) for v in line_ints), default=1)
    idx_strs = [f"{p:0{par_width}d}.{l:0{line_width}d}" for p, l in zip(par_ints, line_ints)]
    df = pd.DataFrame({
        "idx": idx_strs,
        "par": par_ints,
        "line": line_ints,
        "par_end": par_end_bools,
        "textstring": raw[text_column].values,
    }).reset_index(drop=True)
    joined = " ".join(df["textstring"].astype(str).tolist())
    if latin0_fold:
        joined = _to_latin0(joined)
    tklist = [w for w in joined.split() if w]
    charlist = list("".join(tklist))
    rt = RefText(language, tklist, charlist)
    rt.df = df
    return rt


def from_mapped(source_reftext, char_map, language):
    new_charlist = [char_map.get(c, c) for c in source_reftext.charlist]
    new_tklist = []
    for tk in source_reftext.tklist:
        parts = tk.split(',')
        mapped_parts = [char_map.get(p, p) for p in parts]
        new_tklist.append(','.join(mapped_parts))
    mapped_reftext = RefText(language, new_tklist, new_charlist)
    if hasattr(source_reftext, 'df'):
        df = source_reftext.df.copy()
        def _map_cell(cell):
            if not isinstance(cell, str) or cell == '$':
                return cell
            parts = cell.split(',')
            return ','.join(char_map.get(p, p) for p in parts)
        token_cols = [c for c in df.columns if c.startswith('t') and c[1:].isdigit()]
        for col in token_cols:
            df[col] = df[col].map(_map_cell)
        mapped_reftext.df = df
    return mapped_reftext