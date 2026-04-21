"""Shared schema for reference-corpus CSVs.

One row per sentence. Paragraphs are grouped via `para_id`; the terminal
sentence of each paragraph is flagged by `is_para_final` — the primary
key for VMS terminal-sequence comparison.
"""

import csv
import re
from dataclasses import asdict, dataclass
from typing import Optional

COLUMNS = [
    "doc_id",
    "block_type",
    "para_id",
    "sent_id",
    "is_para_final",
    "page_n",
    "textstring_rich",
    "textstring_base",
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
    textstring_rich: str
    textstring_base: str
    textstring_simple: str


_ROMAN_RE = re.compile(
    r"^M{0,4}(CM|CD|D?C{0,4})(XC|XL|L?X{0,4})(IX|IV|V?I{0,4})$",
    re.IGNORECASE,
)

def _letter_count(s: str) -> int:
    return sum(1 for ch in s if ch.isalpha())


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
    i = pos - 1
    while i >= 0 and not s[i].isspace() and s[i] not in ".!?":
        i -= 1
    token = s[i + 1:pos]
    if not token:
        return True
    if token.isdigit():
        return False
    if len(token) <= 2:
        return False
    if _ROMAN_RE.match(token):
        return False
    j = pos + 1
    while j < len(s) and s[j].isspace():
        j += 1
    if j >= len(s):
        return True
    if s[j].islower():
        return False
    if s[j].isalpha():
        k = j + 1
        while k < len(s) and s[k].isalpha():
            k += 1
        if k - j == 1 and k < len(s) and s[k] == ".":
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
