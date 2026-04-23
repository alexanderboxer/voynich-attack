"""What letters precede and follow 'x' in our Latin corpora?

For each word in each corpus, collect the letter immediately before and after
every 'x'. This calibrates what the VMS neighbor distribution of c,M,c,9
should look like if c,M,c,9 = 'x'.
"""

from __future__ import annotations

from collections import Counter

from voynpy.corpora import caesar, vitruvius, celsus, pliny, latin


TARGET = "x"


def context_letters(rt):
    """Return (Counter before-letter, Counter after-letter, int total-x)."""
    before = Counter()
    after = Counter()
    n_x = 0
    for word in rt.tklist:
        word = word.lower()
        for i, ch in enumerate(word):
            if ch != TARGET:
                continue
            n_x += 1
            b = word[i - 1] if i > 0 else "<WORD_START>"
            a = word[i + 1] if i + 1 < len(word) else "<WORD_END>"
            before[b] += 1
            after[a] += 1
    return before, after, n_x


def top_table(cnt, top=10):
    tot = sum(cnt.values())
    items = cnt.most_common(top)
    return [(k, n, 100 * n / tot) for k, n in items], tot


corpora = [
    ("caesar",     caesar),
    ("vitruvius",  vitruvius),
    ("celsus",     celsus),
    ("pliny",      pliny),
    ("latin (all)", latin),
]

for name, rt in corpora:
    b, a, n = context_letters(rt)
    n_tokens = len(rt.tklist)
    print(f"\n=== {name}  ({n_tokens:,} words, 'x' appears {n} times = {100*n/sum(len(w) for w in rt.tklist):.2f}% of letters) ===")
    print("  before 'x':")
    items, tot = top_table(b, 10)
    for k, cnt, pct in items:
        print(f"    {k!r:>15}  {cnt:5d}  {pct:5.1f}%")
    print("  after 'x':")
    items, tot = top_table(a, 10)
    for k, cnt, pct in items:
        print(f"    {k!r:>15}  {cnt:5d}  {pct:5.1f}%")
