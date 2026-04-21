"""Normalization for reference-corpus CSVs.

Two layers:
- `base_normalize`: lowercase, letters + light punctuation, umlaut mapping
  from combining superscript e; preserves combining tilde (titulus) so
  downstream layers can expand it.
- `simple_normalize`: aggressive form derived from the base — titulus
  expansion, ß→ss, umlaut strip, j→i, v→u, punctuation removed.
"""

import re
import unicodedata

_ALLOWED_PUNCT = set(".,;:!?/")
_WS_RE = re.compile(r"\s+")
_COMBINING_TILDE = "\u0303"


def base_normalize(s: str) -> str:
    """Lowercase; keep Unicode letters + `.,;:!?/` + whitespace + combining
    tilde U+0303; drop the rest.

    Preserves ß, ü, ö, ä and other special letters as single graphemes, and
    preserves the combining tilde (titulus) so `simple_normalize` can expand
    forms like `m̃` that lack a precomposed codepoint.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s).lower()
    # 16th-c. German: a/o/u + combining superscript e (U+0364) encodes the
    # modern umlaut. Map to precomposed ä/ö/ü so the letter filter keeps them.
    s = s.replace("a\u0364", "ä").replace("o\u0364", "ö").replace("u\u0364", "ü")
    # Other combining marks (e.g. U+0366 superscript o) fall through and are
    # stripped by the filter below, leaving the bare host letter.
    out = []
    for ch in s:
        if ch.isalpha() or ch.isspace() or ch in _ALLOWED_PUNCT or ch == _COMBINING_TILDE:
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
_DROP_PUNCT_RE = re.compile(r"[.,;:!?]")


def simple_normalize(base: str) -> str:
    """Stricter form derived from `base_normalize` output.

    Conventions (arbitrary but consistent for German):
    - Abbreviation `vñ` → `vnd`
    - Titulus (combining tilde):
        vowel + ~   → vowel + n   (e.g. `heylẽ` → `heylen`)
        n + ~       → nn          (e.g. `mäñlichs` → `männlichs`)
        m + ~       → mm          (e.g. `genum̃en` → `genummen`)
    - ß → ss
    - Umlauts stripped: ä → a, ö → o, ü → u
    - j → i, v → u
    - Virgule `/` → space; all other punctuation removed
    """
    if not base:
        return ""
    s = base
    for pat, repl in _ABBREVIATIONS_RE:
        s = pat.sub(repl, s)
    # Decompose so all combining tildes are directly accessible
    s = unicodedata.normalize("NFD", s)
    s = _VOWEL_TILDE_RE.sub(r"\1n", s)
    s = _N_TILDE_RE.sub("nn", s)
    s = _M_TILDE_RE.sub("mm", s)
    # Drop any remaining orphan combining tildes (e.g. DTA transcription where
    # the base letter under the titulus was lost).
    s = s.replace("\u0303", "")
    s = unicodedata.normalize("NFC", s)
    s = s.replace("ß", "ss")
    s = s.replace("ä", "a").replace("ö", "o").replace("ü", "u")
    s = s.replace("j", "i").replace("v", "u")
    s = s.replace("/", " ")
    s = _DROP_PUNCT_RE.sub("", s)
    return _WS_RE.sub(" ", s).strip()
