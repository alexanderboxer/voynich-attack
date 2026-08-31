#==================================================
# Imports
#==================================================
import numpy as np
import pandas as pd
from collections import Counter
from voynpy.corpora import german, latin, english, french, dutch


#==================================================
# Config
#==================================================
target_filename1 = 'nl_ngram_doubling_rates_per_1000_pairs.csv'
target_filename2 = 'nl_word_doubling_rates_per_1000_pairs.csv'
file_export_flag = False   


#==================================================
# Data
#==================================================
language_corpus_tuplelist = [
    ('German', german),
    ('Latin', latin),
    ('English', english),
    ('French', french),
    ('Dutch', dutch),
    ]


#==================================================
# Function: offset-averaged n-gram doubling-rate
#==================================================
def doubling_rate(charlist: list[str], n: int) -> float:
    '''
    Compute the offset-averaged non-overlapping n-gram doubling rate
    expressed as the count of adjacent identical n-gram pairs per 1,000
    adjacent-pair positions.

    Method
    ------
    The input character list is partitioned into non-overlapping n-grams
    and the number of adjacent identical n-gram pairs is tallied. Because
    this count is offset-dependent the count is averaged over all n
    possible starting offsets to eliminate the arbitrary alignment.

    Parameters
    ----------
    charlist : list of single-character strings
        Input sequence, whitespace pre-stripped by the caller.
    n : int, >= 1
        n-gram length.

    Returns
    -------
    float
        Doublings per 1,000 adjacent n-gram pairs.
    '''

    # Right-pad the charlist to a multiple of n to support reshaping
    N = len(charlist)
    padded_charlist = charlist + ['$'] * ((n - N % n) % n)
    padded_char_array = np.array(padded_charlist)

    # Initialize an empty list to store the doubling count at each offset
    doubling_count_list = list()

    # Loop through all n offsets and tally
    for offset in range(n):
        rolled_char_array = np.roll(padded_char_array, -offset)
        ngram_array = rolled_char_array.reshape([-1, n])
        adjacent_doubles = np.all(ngram_array[:-1] == ngram_array[1:], axis=1)
        doubling_count = adjacent_doubles.sum()
        doubling_count_list.append(doubling_count)

    # Average the doubling count across all offsets and return the rate per 1,000 pairs
    doubling_count_avg = np.mean(doubling_count_list)
    pairs_per_phase = (N / n) - 1
    doubling_rate_per_thousand = float(1000 * doubling_count_avg / pairs_per_phase)

    return doubling_rate_per_thousand


#==================================================
# Tabulate natural-language ngram-doubling rates 
#==================================================
ngram_lengths = [1,2,3,4,5]

doubling_rate_dict = dict()
for language, corpus in language_corpus_tuplelist:
    print('\nComputing {} n-gram doubling rates'.format(language))
    charlist = corpus.charlist
    doubling_rate_list = list()
    for n in ngram_lengths:
        print('\tn = {}'.format(n))
        doubling_rate_list.append(doubling_rate(charlist, n))
    doubling_rate_dict[language] = doubling_rate_list

# Collect the results in a pandas dataframe
df = pd.DataFrame(doubling_rate_dict, index=pd.Index(ngram_lengths, name = 'n'))


#==================================================
# Tabulate natural-language word-doubling rates 
#==================================================
doubled_words_stats_list = list()

for language, corpus in language_corpus_tuplelist:
    tklist = corpus.tklist
    adjacent_word_pairs = list(zip(tklist[:-1], tklist[1:]))
    adjacent_word_doubles = [k[0] for k in adjacent_word_pairs if k[0]==k[1]]
    n_doubles = len(adjacent_word_doubles)
    doubled_word_lengths = [len(k) for k in adjacent_word_doubles]

    # Populate a word_doubles dictionary
    word_doubles_dict = {
        'language': language,
        'n_pairs': len(adjacent_word_pairs),
        'n_doubles': n_doubles,
        'rate_per_1000': 1000 * n_doubles / len(adjacent_word_pairs),
        'avg_doubled_word_length': float(np.mean(doubled_word_lengths)),
    }

    # Update with info about the most common doubled words
    most_common_doubles = Counter(adjacent_word_doubles).most_common(2)
    for j, (word, word_count) in enumerate(most_common_doubles):
        word_doubles_dict['w{}'.format(j+1)] = word
        word_doubles_dict['w{}_pct'.format(j+1)] = 100 * word_count / n_doubles   

    doubled_words_stats_list.append(word_doubles_dict)

# Collect the results in a pandas dataframe
wdf = pd.DataFrame(doubled_words_stats_list).set_index('language')


#==================================================
# Export to file
#==================================================
if file_export_flag:
    df.to_csv(target_filename1)
    wdf.to_csv(target_filename2)
