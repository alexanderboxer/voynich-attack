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
# Includes common Middle English / EEBO-TCP scribal abbreviation glyphs:
#   ꝑ (p with stroke)  → per
#   ꝓ (p with flourish) → pro
#   ꝯ (con ligature)    → con
#   ꝰ (modifier us)     → us
#   ꝙ (q with stroke)   → quod
_LATIN0_FOLD = {
    "đ": "d", "ð": "d", "þ": "th", "ƿ": "w",
    "æ": "ae", "œ": "oe", "ø": "o",
    "ł": "l", "ĸ": "k", "ſ": "s",
    "ꝑ": "per", "ꝓ": "pro", "ꝯ": "con", "ꝰ": "us", "ꝙ": "quod",
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
    """Lowercase; keep Unicode letters + all combining marks + whitespace.

    Virgule `/` is replaced with space to preserve word boundaries; all other
    punctuation is dropped. Glyphs are preserved as-is — no transformation
    of scribal forms (e.g. `uͤ` stays as u+U+0364, NOT folded to `ü`).
    Letter-transformation rules (umlaut folding, titulus expansion, etc.)
    are applied by `simple_normalize`, not here.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s).lower()
    # Virgule becomes a space so words on either side don't collide.
    s = s.replace("/", " ")
    out = []
    for ch in s:
        # `&` (ampersand) and `⁊` (U+204A, Tironian et) are
        # single-character words in medieval and early-modern typography
        # (`&` mostly Latin/Western, `⁊` German/Anglo-Saxon). Preserve
        # them through to the rich form so downstream rules can see
        # patterns like "&c~" / "⁊c~" and expand them to "etc".
        if ch.isalpha() or ch.isspace() or unicodedata.combining(ch) or ch in "&⁊":
            out.append(ch)
    return _WS_RE.sub(" ", "".join(out)).strip()


# Word-level abbreviations — scribal contractions that don't follow the
# default vowel+mark → vowel+n rule. Applied AFTER NFD decomposition so
# combining marks are uniformly detached from base letters (e.g. ñ = n +
# U+0303). Negative lookahead `(?![^\W\d_])` means "not followed by a
# letter" — needed because combining marks aren't \w chars so trailing
# \b doesn't fire at word end.
_ABBREVIATIONS_RE = [
    # vn + nasal-mark (tilde/macron/overline) = "vnd" (→ "und" after v→u).
    # Covers vñ, vn̄, vn̅ regardless of original NFC/NFD form.
    (re.compile(r"\bvn[\u0303\u0304\u0305](?![^\W\d_])"), "vnd"),
    # `&c~` and `⁊c~` (ampersand or Tironian et, plus c, plus optional
    # macron) are the universal medieval/Latin/early-modern abbreviations
    # for "et cetera"; expand to "etc". Macron is optional — `&c.` and
    # `&c` appear in print without it too.
    (re.compile(r"[&\u204A]c[\u0303\u0304\u0305]?"), "etc"),
    # Standalone `&` / `⁊` → "et" (the underlying Tironian "et" ligature).
    # Must come AFTER the &c rule above; otherwise this would consume the
    # `&` in `&c` first.
    (re.compile(r"[&\u204A]"), "et"),
    # ite + nasal-mark = Latin "item" (word-final abbreviation for m).
    # Overrides default +n; scribal marks are word-specific — sometimes m,
    # sometimes n — and "item" is a common Latin idiom in chronicles.
    (re.compile(r"\bite[\u0303\u0304\u0305](?![^\W\d_])"), "item"),
    # Digraph dď (d + d-with-caron) = "der", as a printed word unit. In
    # NFD `ď` decomposes to `d + U+030C` (caron), so match that form.
    (re.compile(r"dd\u030c"), "der"),
    # đ (d with stroke) = -der (stays precomposed under NFD): `ođ`→`oder`,
    # `anđ`→`ander`. Context in our texts so far is always der.
    (re.compile(r"đ"), "der"),

    # Latin scribal contractions. Final macron over `a` / `u` typically
    # expands to "+m" (`quā` -> "quam", `cū` -> "cum"); macron
    # over `i` in `oī…` / `hoī…` / `noī…` stems
    # signals a longer "omn"/"hom"/"nom" contraction (`hoīes` ->
    # "homines"). These patterns don't fire on the German texts (no qu+a~,
    # cu~, hoi~ word forms) so we apply them globally.
    # Word-final `u` + nasal mark expands to "+m". This is correct for
    # both Latin -um endings (Petrum, Iesum, Capernaum, opium, datum,
    # sexennium, pactum…) and the common German accusatives "zum"/"kum"/
    # "darum" — empirically ~33 correct vs 2 wrong on the existing
    # German + EEBO corpus. The one notable miss, "nū" -> "nun" (German
    # "now"), is handled by the specific rule below.
    (re.compile(r"\bnu[̃̄̅](?![^\W\d_])"), "nun"),
    (re.compile(r"u[̃̄̅](?![^\W\d_])"), "um"),
    # Word-final `a` + nasal mark stays "+n" by default — German has many
    # native -an/-ann endings (man, dan, wan, gethan, haubtman, etwan…)
    # where the macron is +n. We only special-case known Latin words.
    (re.compile(r"\bqua[̃̄̅](?![^\W\d_])"), "quam"),
    (re.compile(r"\bea[̃̄̅](?![^\W\d_])"), "eam"),
    (re.compile(r"\betia[̃̄̅](?![^\W\d_])"), "etiam"),
    (re.compile(r"\bipsa[̃̄̅](?![^\W\d_])"), "ipsam"),
    (re.compile(r"\baqua[̃̄̅](?![^\W\d_])"), "aquam"),
    # `aī` is a stem-abbreviation for `anim-` (animus / anima / animalis)
    # — the macron over `i` represents the missing `nim` / `nima` / `n`
    # depending on what follows. Hardcode the forms encountered so far:
    (re.compile(r"\bai[̃̄̅]alia(?![^\W\d_])"), "animalia"),
    (re.compile(r"\bai[̃̄̅]duerterem(?![^\W\d_])"), "animaduerterem"),
    (re.compile(r"\bai[̃̄̅]mus(?![^\W\d_])"), "animus"),
    (re.compile(r"\bai[̃̄̅]mo(?![^\W\d_])"), "animo"),
    (re.compile(r"\bai[̃̄̅]m(?![^\W\d_])"), "animam"),
    (re.compile(r"\bai[̃̄̅]o(?![^\W\d_])"), "animo"),
    # Specific stems where the macron represents more than "+m":
    (re.compile(r"\beni[̃̄̅](?![^\W\d_])"), "enim"),
    (re.compile(r"\boi[̃̄̅]a(?![^\W\d_])"), "omnia"),
    (re.compile(r"\boi[̃̄̅]s(?![^\W\d_])"), "omnis"),
    (re.compile(r"\bhoi[̃̄̅]es(?![^\W\d_])"), "homines"),
    (re.compile(r"\bhoi[̃̄̅]e(?![^\W\d_])"), "homine"),
    (re.compile(r"\bnoi[̃̄̅]e(?![^\W\d_])"), "nomine"),
    # Labial-assimilation rule: vowel + nasal mark + (p / b / m) → "+m".
    # In Latin/Middle English, the missing nasal assimilates to `m` before
    # labials (the same orthographic rule that turns con- into com- before
    # labials). Examples: `tēpred` → `tempred`, `cōp…` → `comp…`,
    # `nūber` → `number`. Specific enough to be safe alongside the German
    # default-`+n` rule.
    (re.compile(r"([aeiou])[̃̄̅]([pbm])"), r"\1m\2"),
    # `hō + nes` is another Latin abbreviation for `homines` (macron over
    # `o` represents `omi`), distinct from the `hoī + es` form.
    (re.compile(r"\bho[̃̄̅]nes(?![^\W\d_])"), "homines"),
    # `ḡ` (g with macron) is a rare Latin abbreviation for `gra` in early
    # printed books. Specific expansion for `ḡuiter` → `grauiter`.
    (re.compile(r"\bg[̃̄̅]uiter(?![^\W\d_])"), "grauiter"),
]

# Three combining marks (U+0303 tilde, U+0304 macron, U+0305 overline) are
# scribal equivalents — all encode an omitted nasal. Treat identically.
_NASAL_MARK = r"[\u0303\u0304\u0305]"
_VOWEL_NASAL_RE = re.compile(rf"([aeiou]){_NASAL_MARK}")
_N_NASAL_RE = re.compile(rf"n{_NASAL_MARK}")
_M_NASAL_RE = re.compile(rf"m{_NASAL_MARK}")


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
    # NFD first so combining marks are detached from base letters.
    # Word-level abbreviations then operate on a single canonical form
    # (e.g. `ñ` and `n̄` both look like `n` + combining mark).
    s = unicodedata.normalize("NFD", rich)
    for pat, repl in _ABBREVIATIONS_RE:
        s = pat.sub(repl, s)
    # Nasal marks (tilde/macron/overline) — default to +n convention
    s = _VOWEL_NASAL_RE.sub(r"\1n", s)
    s = _N_NASAL_RE.sub("nn", s)
    s = _M_NASAL_RE.sub("mm", s)
    # Drop any orphan nasal marks (e.g. DTA transcriptions where the base
    # letter was lost).
    s = s.replace("\u0303", "").replace("\u0304", "").replace("\u0305", "")
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
