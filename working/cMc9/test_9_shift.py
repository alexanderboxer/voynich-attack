"""Test the hypothesis: leading '9,' = −1, trailing ',9' = +1.

For each base token X with a known letter assignment, check whether
9,X and X,9 exist, and what their distributional properties are. If the
rule holds, 9,X should behave like (letter − 1) and X,9 like (letter + 1).

Under 23-letter classical Latin (A B C D E F G H I K L M N O P Q R S T V X Y Z):
  I (9)  →  9,I = H (8)      I,9 = K (10)
  S (18) →  9,S = R (17)     S,9 = T (19)
  X (21) →  9,X = V (20)     X,9 = Y (22)
  C (3)  →  9,C = B (2)      C,9 = D (4)
"""

from __future__ import annotations

from collections import Counter

from voynpy.corpora import vms, vms1, vms2


def _token_cols(df):
    return [c for c in df.columns if c.startswith("t") and c[1:].isdigit()]


def tokens_of(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        for c in cols:
            t = row[c]
            if isinstance(t, str) and t != "$":
                yield t


cnt = Counter(tokens_of(vms))
cnt1 = Counter(tokens_of(vms1))
cnt2 = Counter(tokens_of(vms2))
tot_1 = sum(cnt1.values())
tot_2 = sum(cnt2.values())


# Known anchors
ANCHORS = [
    ("cc,o,x",    "i"),    # from tripling + YYZ
    ("8,a,m",     "s"),    # from YYZ + neighbors
    ("c,M,c,9",   "x"),    # from frequency cliff + context (tentative)
    ("cc,o,Z",    "c"),    # from 21r.3 concisa/circumcisa
]


def row_for(tok):
    n = cnt.get(tok, 0)
    n1 = cnt1.get(tok, 0)
    n2 = cnt2.get(tok, 0)
    p1 = 100 * n1 / tot_1 if tot_1 else 0
    p2 = 100 * n2 / tot_2 if tot_2 else 0
    cliff = f"{p1/p2:.1f}x" if p2 > 0 else "—"
    return n, n1, p1, n2, p2, cliff


print(f"{'base':>14} {'letter':>4} | {'form':>22} | {'n':>5} {'vms1':>5} {'p1':>6} {'vms2':>5} {'p2':>6} cliff")
print("-" * 95)
for base, letter in ANCHORS:
    # the bare token
    n, n1, p1, n2, p2, cliff = row_for(base)
    print(f"{base!r:>14} {letter:>4} | {'<bare>':>22} | {n:>5} {n1:>5} {p1:>5.3f}% {n2:>5} {p2:>5.3f}% {cliff:>5}")
    # 9,base (predicted letter - 1)
    tok_neg = f"9,{base}"
    n, n1, p1, n2, p2, cliff = row_for(tok_neg)
    print(f"{' ':>14} {' ':>4} | {tok_neg!r:>22} | {n:>5} {n1:>5} {p1:>5.3f}% {n2:>5} {p2:>5.3f}% {cliff:>5}    (predicted letter-1)")
    # base,9 (predicted letter + 1)
    tok_pos = f"{base},9"
    n, n1, p1, n2, p2, cliff = row_for(tok_pos)
    print(f"{' ':>14} {' ':>4} | {tok_pos!r:>22} | {n:>5} {n1:>5} {p1:>5.3f}% {n2:>5} {p2:>5.3f}% {cliff:>5}    (predicted letter+1)")
    print()


# Latin letter frequency reference (approx % of letters in classical Latin corpora)
LATIN_FREQ = {
    "a": 8.0, "b": 1.6, "c": 4.5, "d": 4.0, "e": 11.5, "f": 1.5,
    "g": 1.3, "h": 1.2, "i": 10.5, "k": 0.05, "l": 5.5, "m": 4.8,
    "n": 5.7, "o": 6.0, "p": 2.9, "q": 1.5, "r": 6.5, "s": 7.6,
    "t": 8.7, "u": 7.9, "v": 2.5, "x": 0.65, "y": 0.2, "z": 0.04,
}

# 23-letter classical alphabet — j=i, u=v for frequency purposes
CLASSICAL_PLUS1 = {"i": "k", "s": "t", "x": "y", "c": "d"}
CLASSICAL_MINUS1 = {"i": "h", "s": "r", "x": "v", "c": "b"}

print("=" * 95)
print("Expected letter + approximate Latin frequency under ±1 rule (23-letter classical):")
print("=" * 95)
for base, letter in ANCHORS:
    minus = CLASSICAL_MINUS1[letter]
    plus = CLASSICAL_PLUS1[letter]
    print(f"  {base!r} ({letter}, ~{LATIN_FREQ[letter]:.1f}%)")
    print(f"     9,{base} should be {minus!r} (~{LATIN_FREQ[minus]:.1f}% Latin)")
    print(f"     {base},9 should be {plus!r} (~{LATIN_FREQ[plus]:.2f}% Latin)")
