"""Build sentence-level CSV for De Vorsterman Bijbel (1528/1531; Antwerp Dutch Bible printed by Willem Vorsterman).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_vor003vors01`.

Source: https://www.dbnl.org/titels/titel.php?id=_vor003vors01

Text-specific fixes (post-processing — nothing in the shared parser is
modified):

1. **Drop the modern editorial preface.** The DBNL XML prefixes the
   1528/1531 Vorsterman Bible text with ~600 paragraphs of *modern*
   Dutch by Hans Beelen and the DBNL digital-edition project
   (Verantwoording, methodology, contributor lists, etc.). The modern
   preface has empty ``page_n`` (no folio markers). The actual Bible
   has folio markers like ``π1r, π1v, a1r, a1v, …``. We filter rows
   by requiring a non-empty ``page_n``.

2. **Drop editor's bracket markers.** The DBNL editor inserted Dutch
   meta-annotations like ``[afbeelding]`` (= "[image]", 119 occurrences),
   ``[blanco]`` ("[blank page]"), ``[kolom]`` ("[column break]"),
   ``[Heiligenkalender]``, ``[Hier eyndet dat gheheele Oude Testament]``,
   ``[§ Tnyeuvve Testament al geheel: …]`` to mark structural features
   of the source. These are not source text and are dropped.

3. **Relabel front-matter π-pages from body → item.** Pages numbered
   with the Greek π prefix (``π1r, π1v, π2r, π2v``) are the title page,
   list of books, Antwerp printing privilege, and Willem Vorsterman's
   preface — all paratext, not running biblical prose. These get
   relabelled as ``item`` so the ``body`` block_type cleanly holds only
   the actual biblical text from ``a1r`` (Genesis 1) onward.

4. **``split_on_starter_words``** with the default
   ``COMMON_DUTCH_STARTERS`` set. Body content (post-relabel: the
   biblical verses themselves) is mostly well-split already by periods
   (median ~70 letters); the splitter handles any remaining long-row
   stragglers. Critical that the splitter avoids over-splitting on
   capitalised proper nouns (``Israel``, ``Dauid``, ``HEERE`` …) —
   hence the starter-list rather than aggressive rule.
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import (
    download_xml,
    resplit_body_rows,
    split_on_starter_words,
)
from voynpy.corpus_build.schema import Row, write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import format_report, validate

HERE = Path(__file__).parent
DOC_ID = "1531_vorsterman_bijbel"
DBNL_ID = "_vor003vors01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


import re

_BRACKET_ONLY_RE = re.compile(r"^\s*\[[^\]]*\]\s*$")


def _drop_modern_preface(rows: list[Row]) -> list[Row]:
    """Keep only rows with a folio page_n marker. The modern editorial
    preface has empty page_n; the actual 1528/1531 Vorsterman Bible has
    folio markers (π1r, π1v, a1r, a1v, …)."""
    return [r for r in rows if r.page_n]


def _drop_bracket_markers(rows: list[Row]) -> list[Row]:
    """Drop rows whose entire content is a bracketed editor's annotation
    (e.g. ``[afbeelding]``, ``[blanco]``, ``[Heiligenkalender]``,
    ``[Hier eyndet dat gheheele Oude Testament]``). These are DBNL
    editor's meta-annotations describing page structure or image
    placement, not source text."""
    return [r for r in rows if not _BRACKET_ONLY_RE.match(r.textstring_orig)]


def _relabel_front_matter(rows: list[Row]) -> list[Row]:
    """Relabel body rows on π-numbered pages as ``item``. These pages
    (π1r, π1v, π2r, π2v) hold title-page Latin, list of biblical books,
    Antwerp privilege, and Vorsterman's preface — paratext, not running
    biblical prose. Relabelling keeps the ``body`` block_type cleanly
    confined to the actual biblical text starting at ``a1r``."""
    out = []
    for r in rows:
        if r.block_type == "body" and r.page_n.lstrip().startswith("π"):
            r.block_type = "item"
        out.append(r)
    return out


def _drop_calendar_margin_artefacts(rows: list[Row]) -> list[Row]:
    """Drop body rows that are stranded TEI-flattening artefacts:

    - Single-letter body rows (``O``, ``e``, ``f``, ``g``): the source
      Heiligenkalender (saints' calendar) uses a-g dominical letters
      in margins; the parser flattens them as standalone body rows.
    - Stranded ``Ic`` drop-cap at par=25338 sent=0 (Isaiah 43:11): the
      sentence-initial drop-cap got separated from its body
      (``Ic ben die HERE`` follows in sent=1).

    Filter: drop body rows whose Latin a-z letter count is < 2, OR
    whose simple text equals exactly ``ic`` (the drop-cap).
    """
    out = []
    for r in rows:
        if r.block_type == "body":
            simple = r.textstring_simple.strip()
            n_letters = sum(1 for c in simple if "a" <= c <= "z")
            if n_letters < 2:
                continue
            if simple == "ic":
                continue
        out.append(r)
    return out


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = _drop_modern_preface(rows)
    rows = _drop_bracket_markers(rows)
    rows = _relabel_front_matter(rows)
    rows = resplit_body_rows(rows, split_fn=split_on_starter_words)
    rows = _drop_calendar_margin_artefacts(rows)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
