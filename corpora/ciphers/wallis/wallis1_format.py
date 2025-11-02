'''
Smooth and export a given text: Pantagruel + Gargantua
'''
# ==============================================================================
# Import modules
# ==============================================================================
import re
import json
import pandas as pd

# ==============================================================================
# Load data
# ==============================================================================
df0 = pd.read_csv('wallis1.csv').fillna('$')
kdf = pd.read_csv('wallis1_key.csv')

# ==============================================================================
# Token list
# ==============================================================================
tklist0 = [str(k) for k in df0.values.flatten() if k != '$']
tklist0 = [re.sub('\.0', '', k) for k in tklist0] # fix entries that for some reason are read as floats 

# modify
tklist = [k.replace("u","").replace("’","'") for k in tklist0] # remove underlines and apostrophes

# hand corrections
tklist[223] = '370' # was 170
tklist[263] = '436' # was 426
tklist[307] = '43' # was 49
tklist[1087] = '290' # was 280
tklist[1354] = '331' # (ri) was 342 (ti)

# ==============================================================================
# Key dictionary
# ==============================================================================
key_dict = kdf.astype(str).set_index('cipher').val.to_dict()

# additions:
key_dict.update({
    "11'": "un",
    "12'": "deux",
    "14'": "quatre",
    "16'": "six",
    "17'": "septem",
    "19'": "neuf",
    "20'": "dix",
    "30'": "vingt",
    "ψ": "s",
    "380": "pall", # not present in the original key, but present in the original decryption
    "437": "ha", # not present in the original key, but present in the original decryption
})

# ==============================================================================
# Plaintext
# ==============================================================================
plaintext = [key_dict[k] if k in key_dict.keys() else 'unk' for k in tklist]
ciphertuples = [(k[0],k[1],k[2]) for k in zip(range(len(tklist)), tklist, plaintext)]

'''
for tpl in ciphertuples:
    print(tpl)
'''

# ==============================================================================
# Character list
# ==============================================================================
charlist = [k for k in ''.join(tklist)]

# ==============================================================================
# Alpha tokens
# ==============================================================================
def tk2alpha(tk):

    alpha_dict = {
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "'": "prime", 
        "ψ": "psi",
    }

    tkalpha = ''.join([alpha_dict[k] if k in alpha_dict.keys() else 'Q' for k in tk])
    return tkalpha 

alpha_tklist = [tk2alpha(k) for k in tklist]
alpha_keys = [tk2alpha(k) for k in key_dict.keys()]
alpha_key_dict = dict(zip(alpha_keys, key_dict.values()))


# ==============================================================================
# Export as json
# ==============================================================================
wallis1_dict = {
    'tklist': tklist,
    'charlist': charlist,
    'key': key_dict,
    'alpha_tklist': alpha_tklist,
    'alpha_key': alpha_key_dict
}

j = json.dumps(wallis1_dict)
with open('wallis1.json', 'w') as f:
    f.write(j)