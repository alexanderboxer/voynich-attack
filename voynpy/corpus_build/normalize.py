"""Normalization for reference-corpus CSVs.

Two layers:
- `rich_normalize`: lowercase + letters + whitespace + combining tilde.
  All punctuation dropped (virgule first replaced with space to preserve
  word boundaries). Retains unusual glyphs — ß, ü/ö/ä, ẽ/ñ/ã/õ/ũ/ĩ, đ/ď,
  combining marks — for downstream processing.
- `simple_normalize`: aggressive form derived from rich — scribal
  abbreviation expansion, titulus rules, ß→ss, umlaut strip, j→i, v→u.
"""

import re
import unicodedata

_WS_RE = re.compile(r"\s+")
_COMBINING_TILDE = "\u0303"

# Latin Extended letters lacking NFKD decomposition to ASCII. Manual fold.
_LATIN0_FOLD = {
    "đ": "d", "ð": "d", "þ": "th", "ƿ": "w",
    "æ": "ae", "œ": "oe", "ø": "o",
    "ł": "l", "ĸ": "k", "ſ": "s",
}


def to_latin0(s: str) -> str:
    """Fold a string to a-z (Latin-0) plus whitespace.

    Lowercases, decomposes via NFKD and drops combining marks, maps known
    Latin Extended letters to ASCII equivalents, drops anything else not
    `a-z`. Used as the final guard of `simple_normalize` and by loaders
    that need a Latin-0 invariant on tklist/charlist.
    """
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    for k, v in _LATIN0_FOLD.items():
        s = s.replace(k, v)
    return "".join(c for c in s if ("a" <= c <= "z") or c.isspace())


def rich_normalize(s: str) -> str:
    """Lowercase; keep Unicode letters + whitespace + combining tilde U+0303.

    Virgule `/` is replaced with space to preserve word boundaries; all other
    punctuation is dropped. Preserves ß, ü/ö/ä, precomposed vowel-tilde forms
    (ẽ/ñ/ã/õ/ũ/ĩ), scribal letters (đ/ď), and combining tildes — so
    `simple_normalize` can expand them.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s).lower()
    # 16th-c. German: a/o/u + combining superscript e (U+0364) encodes the
    # modern umlaut. Map to precomposed ä/ö/ü so the letter filter keeps them.
    s = s.replace("a\u0364", "ä").replace("o\u0364", "ö").replace("u\u0364", "ü")
    # Virgule becomes a space so words on either side don't collide.
    s = s.replace("/", " ")
    # Other combining marks (e.g. U+0366 superscript o) fall through and are
    # stripped by the filter below, leaving the bare host letter.
    out = []
    for ch in s:
        if ch.isalpha() or ch.isspace() or ch == _COMBINING_TILDE:
            out.append(ch)
    return _WS_RE.sub(" ", "".join(out)).strip()


# Word-level abbreviations to expand before character-level rules.
# These encode scribal contractions that don't follow the regular titulus rule.
_ABBREVIATIONS_RE = [
    # vñ (v + combining-tilde n) = vnd (→ und after v→u). Stand-alone word.
    (re.compile(r"\bvñ\b"), "vnd"),
    # Digraph dď (d + d-with-caron) = der, as a printed word unit. Run
    # before the character-level `đ → der` so `ď` is fully consumed.
    (re.compile(r"dď"), "der"),
    # đ (d with stroke through ascender) = -der suffix: `ođ`→`oder`,
    # `anđ`→`ander`. Wikipedia (Scribal abbreviation) documents đ as
    # de-/der/-ud; context in our texts so far is always der.
    (re.compile(r"đ"), "der"),
]

_VOWEL_TILDE_RE = re.compile(r"([aeiou])\u0303")
_N_TILDE_RE = re.compile(r"n\u0303")
_M_TILDE_RE = re.compile(r"m\u0303")
# Macron (U+0304) is scribally equivalent to tilde — both encode an omitted
# nasal. Treat identically.
_VOWEL_MACRON_RE = re.compile(r"([aeiou])\u0304")


def simple_normalize(rich: str) -> str:
    """Stricter form derived from `rich_normalize` output.

    Conventions (arbitrary but consistent for German):
    - Scribal abbreviations: `vñ`→`vnd`, `dď`→`der`, `đ`→`der`
    - Titulus (combining tilde):
        vowel + ~   → vowel + n   (e.g. `heylẽ` → `heylen`)
        n + ~       → nn          (e.g. `mäñlichs` → `männlichs`)
        m + ~       → mm          (e.g. `genum̃en` → `genummen`)
    - ß → ss
    - Umlauts stripped: ä → a, ö → o, ü → u
    - j → i, v → u
    """
    if not rich:
        return ""
    s = rich
    for pat, repl in _ABBREVIATIONS_RE:
        s = pat.sub(repl, s)
    # Decompose so all combining marks are directly accessible
    s = unicodedata.normalize("NFD", s)
    # Tildes (U+0303)
    s = _VOWEL_TILDE_RE.sub(r"\1n", s)
    s = _N_TILDE_RE.sub("nn", s)
    s = _M_TILDE_RE.sub("mm", s)
    # Macrons (U+0304) — same convention as tildes
    s = _VOWEL_MACRON_RE.sub(r"\1n", s)
    # Drop any remaining orphan combining tildes/macrons (e.g. DTA
    # transcriptions where the base letter was lost).
    s = s.replace("\u0303", "").replace("\u0304", "")
    s = unicodedata.normalize("NFC", s)
    s = s.replace("ß", "ss")
    s = s.replace("ä", "a").replace("ö", "o").replace("ü", "u")
    # Typographic variants common in 15th-c. printing
    s = s.replace("ſ", "s").replace("ʒ", "z").replace("ı", "i")
    s = s.replace("j", "i").replace("v", "u")
    # Final invariant: anything that slipped through gets folded/dropped so
    # `textstring_simple` is guaranteed Latin-0 (a-z + whitespace only).
    s = to_latin0(s)
    return _WS_RE.sub(" ", s).strip()
