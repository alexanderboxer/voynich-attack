"""Shared schema for reference-corpus CSVs.

One row per sentence. Paragraphs are grouped via `para_id`; the terminal
sentence of each paragraph is flagged by `is_para_final` — the primary
key for VMS terminal-sequence comparison.
"""

import csv
import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Optional

COLUMNS = [
    "doc_id",
    "block_type",
    "para_id",
    "sent_id",
    "is_para_final",
    "page_n",
    "textstring_orig",
    "textstring_rich",
    "textstring_simple",
]


@dataclass
class Row:
    doc_id: str
    block_type: str
    para_id: int
    sent_id: int
    is_para_final: bool
    page_n: Optional[str]
    textstring_orig: str
    textstring_rich: str
    textstring_simple: str


_ROMAN_RE = re.compile(
    r"^M{0,4}(CM|CD|D?C{0,4})(XC|XL|L?X{0,4})(IX|IV|V?I{0,4})$",
    re.IGNORECASE,
)

def _letter_count(s: str) -> int:
    return sum(1 for ch in s if ch.isalpha())


# Tokens whose stem signals that a following single-letter abbreviation
# refers to an alphabetical section (e.g. "buchstaben B."). Only then do we
# treat the intervening period as a non-boundary. Extensible for future texts.
_LETTER_REF_STEMS: tuple[str, ...] = (
    "buchstab",
    "buchstba",  # typo of "buchstab" in Brunfels para 174 (a/b transposed)
)

# Tokens whose stem signals that the following period continues a date/time
# duration clause rather than ending a sentence. Almanach 1473 pattern:
# "...nach mittag. Minuten .xix." — the event time and its minutes belong
# to the same statement.
_TIME_CONTEXT_STEMS: tuple[str, ...] = ("mittag",)


def _stem(token: str) -> str:
    """Lowercase and strip combining marks — for stem matching on tokens
    that may carry early-modern diacritics (`buͦchstaben`, `buchstabẽ`)."""
    s = unicodedata.normalize("NFD", token).lower()
    return "".join(c for c in s if not unicodedata.combining(c))


def _is_letter_ref_context(token: str) -> bool:
    return _stem(token).startswith(_LETTER_REF_STEMS)


def _is_time_context(token: str) -> bool:
    return _stem(token).startswith(_TIME_CONTEXT_STEMS)


def _is_dot_boundary(s: str, pos: int) -> bool:
    """Decide whether a `.` at `pos` ends a sentence.

    Returns False (not a boundary) when the period marks an abbreviation or
    numeral rather than a sentence end:
    - token immediately before is ≤ 2 letters (e.g. `L.`, `Dr.`)
    - token immediately before is all digits (e.g. `1.`, `2.`)
    - token immediately before is a Roman numeral (e.g. `iii.`, `xxxi.`)
    - the next non-space character is lowercase (mid-sentence continuation)
    - the next token is a single-letter abbreviation (e.g. `... buchstaben. L. von ...`)
    """
    # Skip whitespace between the token and the period ("Minuten . xix ."
    # — common in almanac-style data layout).
    i = pos - 1
    while i >= 0 and s[i].isspace():
        i -= 1
    token_end = i + 1
    while i >= 0 and not s[i].isspace() and s[i] not in ".!?":
        i -= 1
    token = s[i + 1:token_end]
    if not token:
        # No alphabetic content preceding this period — likely decorative
        # scribal punctuation (e.g. `.vij.  .xliij` between table cells, or
        # a period at start of text). Treat as non-boundary.
        return False
    if _is_time_context(token):
        return False
    if token.isdigit():
        return False
    if len(token) <= 2:
        return False
    # ENHG often writes the final `i` of a Roman numeral as `j` (ij, iij, vij,
    # xliij, etc.). Fold j→i before the Roman check.
    if _ROMAN_RE.match(token.replace("j", "i").replace("J", "I")):
        return False
    j = pos + 1
    while j < len(s) and s[j].isspace():
        j += 1
    if j >= len(s):
        return True
    if s[j].islower():
        return False
    if s[j].isalpha() and _is_letter_ref_context(token):
        k = j + 1
        while k < len(s) and s[k].isalpha():
            k += 1
        if k - j == 1:
            kk = k
            while kk < len(s) and s[kk].isspace():
                kk += 1
            if kk < len(s) and s[kk] == ".":
                return False
    return True


def split_sentences(s: str) -> list[str]:
    """Split on `.!?` only; virgules `/` stay inline (they are clause-level).

    Terminal punctuation stays attached to its sentence. `!` and `?` are
    always boundaries; `.` uses the heuristic in `_is_dot_boundary` to avoid
    splitting on abbreviations and numerals.
    """
    if not s or not s.strip():
        return []
    sents: list[str] = []
    start = 0
    for i, ch in enumerate(s):
        if ch == "!" or ch == "?":
            seg = s[start:i + 1].strip()
            if seg:
                sents.append(seg)
            start = i + 1
        elif ch == "." and _is_dot_boundary(s, i):
            seg = s[start:i + 1].strip()
            if seg:
                sents.append(seg)
            start = i + 1
    tail = s[start:].strip()
    if tail:
        sents.append(tail)
    return [t for t in sents if _letter_count(t) >= 1]


def write_csv(rows: list[Row], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
