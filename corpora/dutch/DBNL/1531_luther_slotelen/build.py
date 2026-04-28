"""Build sentence-level CSV for Vanden Slotelen (Luther 1531, Dutch translation of Latin work).

DBNL provides a diplomatic TEI Lite transcription.

Source: https://www.dbnl.org/titels/titel.php?id=luth001vand01_01

Note: the catalog title-page ID is `luth001vand01_01`, but DBNL's XML
endpoint serves the content under the bare title ID `luth001vand01`
(without the `_01` edition suffix). Requesting `luth001vand01_01`
returns 0 bytes from the XML endpoint despite HTTP 200 OK — a quirk
of DBNL's URL-to-content mapping for some texts. Use `luth001vand01`.

Text-specific fixes:

1. ``split_on_starter_words`` with the default ``COMMON_DUTCH_STARTERS``
   set. The treatise has capitalised theological proper nouns
   mid-sentence (``God``, ``Paus``, ``Christen``, ``Petrus``,
   ``Euangelie``, ``Sacrament``, ``Christus``, ``Heydenen``, ``Pausdom``,
   ``Turcken``…), so the simple Capital-after-lowercase rule would
   over-split on every theological term. The starter-list rule splits
   only on safe sentence-starters (``Ende, Doe, Die, Dit, …``).

2. Drop one stranded pure-Roman row (``.ij.`` at par=109 sent=14) — a
   chapter-internal numeral marker extracted as its own row by the
   parser.
"""

import re
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
DOC_ID = "1531_luther_slotelen"
DBNL_ID = "luth001vand01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"

_PURE_ROMAN_RE = re.compile(r"^[ivxlcdm.\s]+$")


def _drop_marker_rows(rows: list[Row]) -> list[Row]:
    """Drop body rows that are pure Roman numerals or have <2 Latin letters
    — stranded chapter/section markers."""
    out = []
    for r in rows:
        if r.block_type == "body":
            simple = r.textstring_simple.strip()
            n_letters = sum(1 for c in simple if "a" <= c <= "z")
            if n_letters < 2:
                continue
            if _PURE_ROMAN_RE.fullmatch(simple):
                continue
        out.append(r)
    return out


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = resplit_body_rows(rows, split_fn=split_on_starter_words)
    rows = _drop_marker_rows(rows)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
