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

# Multi-character scribal/citation abbreviations that aren't sentence-final.
# Most common: "cap." / "capit." (Latin capitulum, German Capitel) — used
# in chapter citations like "vj. cap. Johannis", "ij. cap. Genesis".
_KNOWN_ABBREVS = frozenset({
    "cap", "capit", "capitl", "capitel", "capittel", "capittell",
})



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
    if token.lower() in _KNOWN_ABBREVS:
        return False
    j = pos + 1
    while j < len(s) and s[j].isspace():
        j += 1
    if j >= len(s):
        return True
    if s[j].islower():
        return False
    if s[j].isdigit():
        # Biblical / scribal citation pattern: book abbreviation followed
        # by chapter (and verse) number — e.g. "Gen. 22", "Gal. 3",
        # "Johan. 11", "Reg. 17". The period belongs to the citation, not
        # to a sentence boundary.
        return False
    if s[j] == "\x03":
        # Sentinel: a TEI <bibl> citation begins immediately after this
        # period. Trailing biblical citations attach to their preceding
        # text, so suppress the boundary here. The matching `\x04` close
        # sentinel forces the boundary at the end of the citation.
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
    # Enumeration list: at the current dot, look forward for a chain of
    # `Word.` patterns (capitalized, ≥3 letters) ending in a lowercase
    # continuation. Scribal lists like "Hemmel. Sunne. Mane. vnde sternen"
    # use periods as separators, not sentence boundaries.
    cur = j
    chain_count = 0
    check_pos = cur
    while cur < len(s):
        ws = cur
        check_pos = ws
        while cur < len(s) and s[cur].isalpha():
            cur += 1
        if cur - ws < 3 or not s[ws].isupper():
            break
        pp = cur
        while pp < len(s) and s[pp].isspace():
            pp += 1
        if pp >= len(s) or s[pp] != ".":
            break
        chain_count += 1
        cur = pp + 1
        while cur < len(s) and s[cur].isspace():
            cur += 1
        check_pos = cur
    if chain_count >= 1 and check_pos < len(s) and s[check_pos].islower():
        return False
    return True


def split_sentences_with_offsets(s: str) -> list[tuple[int, str]]:
    """Split on `.!?` only and return (start_offset_in_s, sentence) pairs.

    Terminal punctuation stays attached to its sentence. `!` and `?` are
    always boundaries; `.` uses the heuristic in `_is_dot_boundary` to avoid
    splitting on abbreviations and numerals. Letter-less segments are merged
    back into the preceding sentence (keeping the predecessor's offset).
    """
    if not s or not s.strip():
        return []

    def _push(out: list, raw_start: int, raw_end: int) -> None:
        seg = s[raw_start:raw_end]
        stripped = seg.strip()
        if not stripped:
            return
        lead = len(seg) - len(seg.lstrip())
        out.append((raw_start + lead, stripped))

    raw: list[tuple[int, str]] = []
    start = 0
    for i, ch in enumerate(s):
        if ch == "!" or ch == "?":
            _push(raw, start, i + 1)
            start = i + 1
        elif ch == "\x04":
            # `\x04` closes a <bibl> citation. Default: force a sentence
            # boundary so the citation attaches to the *preceding* text
            # (trailing-citation convention). Two exceptions, both detected
            # by looking past intervening whitespace:
            #   - Next is `\x03` (start of another <bibl>): chain consecutive
            #     citations onto the same preceding sentence.
            #   - Next is a lowercase letter: the citation is mid-sentence
            #     (e.g. "Hiere. 29. vnd Exo. 21. ſagt Moſes…") and should
            #     merge with the following continuation rather than break.
            k = i + 1
            while k < len(s) and s[k].isspace():
                k += 1
            if k < len(s) and (s[k] == "\x03" or s[k].islower()):
                continue
            _push(raw, start, i + 1)
            start = i + 1
        elif ch == "." and _is_dot_boundary(s, i):
            _push(raw, start, i + 1)
            start = i + 1
    _push(raw, start, len(s))

    merged: list[tuple[int, str]] = []
    for off, t in raw:
        if _letter_count(t) < 1:
            # Letter-less fragment (e.g. trailing date "1473." after a split
            # at "Octobris."): glue back onto the predecessor.
            if merged:
                prev_off, prev_t = merged[-1]
                merged[-1] = (prev_off, prev_t + " " + t)
            continue
        if merged and len(t.split()) == 1:
            # Single-word "sentence" almost always arises from a typographic
            # period inside a multi-word phrase ("vierdẽ. Capittel.",
            # "v. xij.") rather than a real boundary. Merge into predecessor.
            prev_off, prev_t = merged[-1]
            merged[-1] = (prev_off, prev_t + " " + t)
            continue
        if merged and all(
            _ROMAN_RE.match(tok.rstrip(".").replace("j", "i").replace("J", "I"))
            for tok in t.split()
            if tok.rstrip(".")
        ):
            # Multi-token pure-Roman "sentence" — almost always a date that
            # got separated from its anchor ("anno domini. M.D.XCIII." →
            # second half is "M D XCIII" standing alone). The single-word
            # rule above only catches one-token Romans; this catches the
            # multi-token form. Merge into predecessor.
            prev_off, prev_t = merged[-1]
            merged[-1] = (prev_off, prev_t + " " + t)
            continue
        merged.append((off, t))

    # Move trailing inline dialogue speaker labels (all-caps abbreviations
    # like "ANTO.", "AVCT.", "AVCTOR") from the end of one sentence to the
    # start of the next. Some Reformation dialogues typeset speaker tags
    # inline rather than via TEI <sp>/<speaker>, so the splitter ends up
    # leaving the label dangling at the end of the previous speech.
    for i in range(len(merged) - 1):
        cur_off, cur_t = merged[i]
        peeled: list[str] = []
        while True:
            parts = cur_t.rsplit(None, 1)
            if len(parts) < 2:
                break
            if not _is_speaker_label(parts[1]):
                break
            peeled.append(parts[1])
            cur_t = parts[0].rstrip()
        if peeled:
            prefix = " ".join(reversed(peeled))
            next_off, next_t = merged[i + 1]
            merged[i] = (cur_off, cur_t)
            merged[i + 1] = (next_off, prefix + " " + next_t)
    return merged


def _is_speaker_label(token: str) -> bool:
    """A token looks like an inline dialogue speaker label if it is at least
    3 alphabetic characters, all uppercase, optionally followed by `.`, and
    not a Roman numeral (which would otherwise sweep up dates like XXIX,
    MDXXII, etc.)."""
    word = token.rstrip(".")
    if len(word) < 3 or not word.isalpha() or not word.isupper():
        return False
    if _ROMAN_RE.match(word.replace("J", "I")):
        return False
    return True


def split_sentences(s: str) -> list[str]:
    """Split on `.!?`; see split_sentences_with_offsets for details."""
    return [t for _, t in split_sentences_with_offsets(s)]


def write_csv(rows: list[Row], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
