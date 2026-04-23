"""YYZ word-endings across corpora.

For each word of length >= 3 in each corpus, check if the last three letters
match the YYZ pattern: L[-3] == L[-2] != L[-1]. Tally the trigrams.

Also: for corpus_build corpora (German), specifically examine the last
word of paragraph-final lines (par_end=True) — that's the VMS-paragraph
analog.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from voynpy.corpora import (
    caesar, vitruvius, celsus, pliny, latin,       # Latin
    brunfels, almanach1473, dracole1485, dta,       # German (corpus_build)
)
from voynpy import reftext


def yyz_word_endings(tklist):
    """All words ending in a YYZ trigram (L[-3]==L[-2]!=L[-1])."""
    endings = Counter()
    total_words = 0
    yyz_words = 0
    for w in tklist:
        w = w.lower()
        if len(w) < 3:
            continue
        total_words += 1
        a, b, c = w[-3], w[-2], w[-1]
        if a == b and b != c:
            yyz_words += 1
            endings[a + b + c] += 1
    return endings, total_words, yyz_words


# ---- Part 1: word-terminal YYZ across all corpora
corpora = [
    ("caesar",      caesar,      "Latin"),
    ("vitruvius",   vitruvius,   "Latin"),
    ("celsus",      celsus,      "Latin"),
    ("pliny",       pliny,       "Latin"),
    ("latin (all)", latin,       "Latin"),
    ("brunfels",    brunfels,    "German (ENHG)"),
    ("almanach1473", almanach1473, "German (ENHG)"),
    ("dracole1485", dracole1485, "German (Low)"),
    ("dta (all)",   dta,         "German combined"),
]

print("=" * 72)
print("WORD-TERMINAL YYZ ENDINGS BY CORPUS")
print("=" * 72)
for name, rt, lang in corpora:
    endings, total, yyz = yyz_word_endings(rt.tklist)
    if total == 0:
        continue
    print(f"\n--- {name} [{lang}] ---")
    print(f"  words >= 3 chars: {total:,}   YYZ-ending words: {yyz:,} ({100*yyz/total:.2f}%)")
    print(f"  top 12 YYZ trigrams:")
    for tri, n in endings.most_common(12):
        print(f"     {tri!r:>7}: {n:5d}  ({100*n/yyz:5.1f}%)")


# ---- Part 2: paragraph-final YYZ (corpus_build corpora only)
def paragraph_final_yyz(rt, name):
    # rt.df has par, par_end, textstring. Get the last word of each par_end=True
    endings = Counter()
    paras = 0
    yyz = 0
    # group by par, take last line's textstring
    df = rt.df
    for par in df.par.unique():
        rows = df[df.par == par]
        last_row = rows.iloc[-1]
        paras += 1
        words = str(last_row["textstring"]).split()
        if not words:
            continue
        last = words[-1].lower()
        if len(last) < 3:
            continue
        a, b, c = last[-3], last[-2], last[-1]
        if a == b and b != c:
            yyz += 1
            endings[a + b + c] += 1
    return endings, paras, yyz


print("\n")
print("=" * 72)
print("PARAGRAPH-FINAL YYZ ENDINGS (corpus_build corpora)")
print("=" * 72)
for name, rt in [("brunfels", brunfels), ("almanach1473", almanach1473), ("dracole1485", dracole1485)]:
    endings, paras, yyz = paragraph_final_yyz(rt, name)
    print(f"\n--- {name} ---")
    print(f"  paragraphs: {paras}   paragraph-final YYZ words: {yyz} ({100*yyz/paras:.1f}%)")
    print(f"  trigrams:")
    for tri, n in endings.most_common(12):
        print(f"     {tri!r:>7}: {n}")
