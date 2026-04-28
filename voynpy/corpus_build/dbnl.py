"""DBNL (Digitale Bibliotheek voor de Nederlandse Letteren) source helpers.

DBNL hosts diplomatic TEI Lite (TEI.2) transcriptions of Dutch texts. Each
text has a stable DBNL ID like `_ars002arsm01`. The XML is served from a
URL of the form `https://www.dbnl.org/nieuws/xml.php?id=<dbnl_id>`.

Note that DBNL XMLs use the older TEI.2 / TEI Lite DTD rather than TEI-P5;
the parser in `tei_p5.py` is namespace-flexible and handles both.

Many 15th-c. Dutch / Low German incunabula use mid-line capitalisation
rather than periods to mark sentence boundaries, which means the standard
period-based splitter under-splits them. This module provides:

- `resplit_body_rows(rows, split_fn=..., glue_fixes=...)` — row-mechanics
  plumbing for re-splitting, glue-fixing, and re-normalising body rows.
- `split_on_any_capital(text)` — aggressive splitter for texts with
  strict lowercase-proper-noun convention (Hollandish/Brabants 1477+
  incunabula: Alexander, parijs, arent_bosman …).
- `split_on_starter_words(text, *, starters=...)` — conservative splitter
  for texts where proper nouns may appear capitalised mid-sentence
  (e.g. souen_wysen 1478, where Lyppolt / Conrat / Ihesus appear
  capitalised). Splits only when the Capital word is in `starters`.
- `COMMON_DUTCH_STARTERS` — sensible default starter set covering Middle
  Dutch and Middle Low German sentence-starter words; per-text build.py
  can extend or override.

The right splitter to pass to `resplit_body_rows` is text-dependent — it
hinges on whether the text capitalises proper nouns mid-sentence.
"""

import re
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence
from urllib.request import urlopen

from .normalize import rich_normalize, simple_normalize
from .schema import Row

DBNL_XML_URL = "https://www.dbnl.org/nieuws/xml.php?id={dbnl_id}"


def download_xml(dbnl_id: str, dest: str | Path) -> Path:
    """Download a DBNL document's TEI Lite XML to `dest`."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(DBNL_XML_URL.format(dbnl_id=dbnl_id)) as resp:
        dest.write_bytes(resp.read())
    return dest


SplitFn = Callable[[str], list[str]]


def resplit_body_rows(
    rows: Iterable[Row],
    *,
    split_fn: Optional[SplitFn] = None,
    glue_fixes: Sequence[tuple[str, str]] = (),
) -> list[Row]:
    """Re-split body rows using a per-text `split_fn` and apply per-text
    `glue_fixes` to fix proper-noun concatenation issues.

    The split rule itself is text-specific (15th-c. incunabula use varying
    capitalisation conventions) — callers supply the rule via `split_fn`,
    which takes the original-case string of one body row and returns a
    list of sentence strings. If `split_fn` is None, no splitting occurs.

    `glue_fixes` is a list of `(old, new)` string-replacement tuples
    applied to each chunk's text *after* splitting (so glue-fix-induced
    spaces don't themselves trigger splits).

    Per-paragraph sent_ids are renumbered after re-splitting, and the last
    row of each paragraph is flagged with `is_para_final=True`. Heads and
    other non-body rows are passed through unchanged (with glue fixes
    applied to their text)."""
    rows = list(rows)
    out: list[Row] = []
    current_para: int | None = None
    para_buffer: list[Row] = []

    def _flush(buf: list[Row]) -> None:
        new_rows: list[Row] = []
        for r in buf:
            if r.block_type != "body":
                orig = r.textstring_orig
                for old, new in glue_fixes:
                    orig = orig.replace(old, new)
                rich = rich_normalize(orig)
                simple = simple_normalize(rich)
                new_rows.append(Row(
                    doc_id=r.doc_id, block_type=r.block_type,
                    para_id=r.para_id, sent_id=0,
                    is_para_final=False, page_n=r.page_n,
                    textstring_orig=orig, textstring_rich=rich,
                    textstring_simple=simple,
                ))
                continue
            chunks = (
                split_fn(r.textstring_orig) if split_fn is not None
                else [r.textstring_orig]
            )
            for chunk in chunks:
                for old, new in glue_fixes:
                    chunk = chunk.replace(old, new)
                chunk = chunk.strip()
                if not chunk:
                    continue
                rich = rich_normalize(chunk)
                simple = simple_normalize(rich)
                # Drop chunks that have no Latin a-z content. Catches:
                # - isolated punctuation/markers left after a split (`.`, `¶`)
                # - non-Latin alphabet flourishes (e.g. Greek printer's
                #   marks like `γμοθοωιλντομ` at the end of ix_quaesten)
                # - digit-only chunks
                # Note: `c.isalpha()` would let Greek/Cyrillic through and
                # contaminate downstream Latin-0-based statistics.
                if not any("a" <= c <= "z" for c in simple):
                    continue
                new_rows.append(Row(
                    doc_id=r.doc_id, block_type=r.block_type,
                    para_id=r.para_id, sent_id=0,
                    is_para_final=False, page_n=r.page_n,
                    textstring_orig=chunk, textstring_rich=rich,
                    textstring_simple=simple,
                ))
        if not new_rows:
            return
        for j, r in enumerate(new_rows):
            r.sent_id = j
        new_rows[-1].is_para_final = True
        out.extend(new_rows)

    for r in rows:
        if current_para is None or r.para_id != current_para:
            if para_buffer:
                _flush(para_buffer)
            para_buffer = []
            current_para = r.para_id
        para_buffer.append(r)
    if para_buffer:
        _flush(para_buffer)
    return out


# ---------------------------------------------------------------------------
# Splitter implementations.
# ---------------------------------------------------------------------------

# Aggressive splitter: any Capital word that follows a lowercase letter +
# whitespace marks a sentence boundary. Suitable for texts where proper
# nouns are lowercase mid-sentence (Hollandish/Brabants 1477+ incunabula).
_ANY_CAP_RE = re.compile(r"([a-z])(\s+)([A-Z][a-z])")


def split_on_any_capital(text: str) -> list[str]:
    """Split *text* on any `[a-z]\\s+[A-Z][a-z]` boundary.

    Suitable for texts with strict lowercase-proper-noun convention —
    Alexander 1477, parijs_ende_vienna 1487, arent_bosman 1488, etc.
    """
    splits = [m.start(3) for m in _ANY_CAP_RE.finditer(text)]
    if not splits:
        return [text.strip()] if text.strip() else []
    chunks: list[str] = []
    last = 0
    for pos in splits:
        chunk = text[last:pos].strip()
        if chunk:
            chunks.append(chunk)
        last = pos
    tail = text[last:].strip()
    if tail:
        chunks.append(tail)
    return chunks


# Conservative splitter: split only when the Capital word is in a curated
# starter set. Suitable for texts where proper nouns may be capitalised
# mid-sentence (e.g. souen_wysen 1478).
_STARTER_BOUNDARY_RE = re.compile(r"(?:,)?\s+([A-Z][a-z]+)")
_PILCROW_RE = re.compile(r"\s*¶\s*")


# Default Middle Dutch / Middle Low German sentence-starter words. Per-text
# build.py may pass its own `starters` set if this default isn't right —
# e.g. to avoid over-splitting on a starter word that turns out to be a
# proper noun in that specific text.
COMMON_DUTCH_STARTERS = frozenset({
    # High-confidence Middle Dutch sentence starters
    "Ende", "Doe", "Daer", "Hier", "Die", "Dit", "Dat", "Het", "Hi", "Si",
    "Mer", "Want", "Als", "Alse", "Aldus", "Also", "Item",
    "Ic", "Ick", "Een", "Wat", "Nu", "Soe", "So", "Och", "O", "Doch",
    "Mijn", "Myn", "Du", "Ten", "Tot", "Op", "Om", "Oec", "Sy", "An", "In",
    "Heer", "Sunte", "Sinte", "Dese", "Eens", "Wanneer", "Hoe", "Waer",
    "Mettien", "Na", "Des", "Tegens", "Deen",
    # Middle Low German variants
    "Id", "He", "Se", "De", "Do", "Sich", "Hir", "Wente", "Auer", "Aver",
    "Vp", "Up", "Vnde", "Vnd", "Wol", "Wor", "Hoer", "Dy", "To", "Alsoo",
    "Nv",
})


def split_on_starter_words(
    text: str,
    *,
    starters: frozenset = COMMON_DUTCH_STARTERS,
    pilcrow: bool = True,
) -> list[str]:
    """Split *text* only when the Capital word at the boundary is in
    `starters`. Pilcrow (¶) glyphs are also treated as sentence markers
    if `pilcrow=True`.

    Suitable for texts where proper nouns may appear capitalised
    mid-sentence (e.g. souen_wysen 1478 has Lyppolt / Conrat / Ihesus
    capitalised in body prose). Pass a text-specific `starters` set if
    `COMMON_DUTCH_STARTERS` isn't quite right.
    """
    splits: list[int] = []
    for m in _STARTER_BOUNDARY_RE.finditer(text):
        if m.group(1) in starters:
            splits.append(m.start(1))
    if pilcrow:
        for m in _PILCROW_RE.finditer(text):
            splits.append(m.start())
    splits = sorted(set(splits))
    if not splits:
        return [text.strip()] if text.strip() else []
    chunks: list[str] = []
    last = 0
    for pos in splits:
        chunk = text[last:pos].strip().rstrip(",").strip().lstrip("¶").strip()
        if chunk:
            chunks.append(chunk)
        last = pos
    tail = text[last:].strip().rstrip(",").strip().lstrip("¶").strip()
    if tail:
        chunks.append(tail)
    return chunks
