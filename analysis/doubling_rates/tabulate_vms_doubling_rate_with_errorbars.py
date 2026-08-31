#==================================================
# Imports
#==================================================
import numpy as np
from voynpy.corpora import vms

BLOCK_TOKEN_THRESHOLD = 1000


#==================================================
# Function: count double tokens
#==================================================
def count_doubles(tkstring: str) -> int:
    tklist = tkstring.split(';')
    ztktk = list(zip(tklist[:-1], tklist[1:]))
    n_doubles = sum([True if k[0]==k[1] and '?' not in k[0] else False for k in ztktk])
    return n_doubles


#==================================================
# Function: assign blocks
#==================================================
def assign_blocks(ntk_list: list[int], block_token_threshold: int) -> list[int]:
    '''
    Group consecutive folios into blocks of at least a threshold token count.

    Parameters
    ----------
    ntk_list : list of int
        Token count of each folio, in manuscript order.
    block_token_threshold : int, >= 1
        Minimum tokens per block.

    Returns
    -------
    list of int
        1-based block index for each folio, parallel to ntk_list.
    '''
    block_idx_list = list()
    running_sum, block_idx = 0, 1
    for n in ntk_list:
        if running_sum >= block_token_threshold:
            running_sum = 0
            block_idx += 1
        running_sum += n
        block_idx_list.append(block_idx)
    return block_idx_list


#==================================================
# Tabulate VMS per-line tokenstrings
#==================================================
vms_df = vms.df.copy()
tkcols = [k for k in vms_df.columns if k not in ['folio','par','line']]
vms_df['tkstring'] = vms_df[tkcols].apply(lambda X: ';'.join([k for k in X if k != '$']), axis=1)
vms_df['ntk'] = vms_df.tkstring.apply(lambda x: len(x.split(';')))
vms_df['idx']= np.cumsum(vms_df.folio != vms_df.folio.shift(1))


#==================================================
# Tabulate VMS per-folio tokenstrings and count doubles
#==================================================
folio_df = vms_df.groupby('idx').agg({'folio': 'first', 'ntk': 'sum', 'tkstring': lambda x: ';'.join(x)})
folio_df['n_doubles'] = folio_df.tkstring.apply(count_doubles)


#==================================================
# Assign a grouping block-id to each folio
#==================================================
folio_df['block'] = assign_blocks(folio_df.ntk.to_list(), BLOCK_TOKEN_THRESHOLD)


#==================================================
# Count doubles-per-1k-pairs for each block
#==================================================
block_df = folio_df.groupby('block').agg({'folio': lambda x: list(x), 'ntk': 'sum', 'n_doubles': 'sum'})
block_df['n_doubles_per_1k_pairs'] = [1000 * k[0] / (k[1] - 1) for k in zip(block_df.n_doubles, block_df.ntk)]


#==================================================
# Mean and standard error
#==================================================
xx = block_df.n_doubles_per_1k_pairs.to_list()
mean_rate = np.mean(xx)
sem = np.std(xx, ddof=1) / np.sqrt(len(xx))


#==================================================
# Grand mean
#==================================================
vms_tklist = vms.tklist.copy()
vms_tkstring = ';'.join(vms_tklist)
vms_doubles = count_doubles(vms_tkstring)
n_doubles_per_1k_pairs = 1000 * vms_doubles / (len(vms_tklist) - 1)


#==================================================
# Report
#==================================================
print('\n\nVoynich Token-Doubling Rate')
print(f'{n_doubles_per_1k_pairs:.2f} ± {sem:.1f} per 1,000 token-pairs (Grand Mean)')
print(f'{mean_rate:.2f} ± {sem:.1f} per 1,000 token-pairs (Block Mean)')