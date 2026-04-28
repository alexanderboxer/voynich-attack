"""Build sentence-level CSV for Dits die Excellente Chronijcke van Vlaenderen (1531; chronicle of Flanders).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_dit004dits01`.

Source: https://www.dbnl.org/titels/titel.php?id=_dit004dits01

Text-specific fixes:

1. **``split_on_starter_words``** with the default
   ``COMMON_DUTCH_STARTERS`` set. The chronicle uses capitalised proper
   nouns mid-sentence (place and person names: ``Vlaendren``, ``Gallen``,
   ``Guyenne``, ``Iulius``, ``Troyanen``, ``Bretaengien``, ``Israel``,
   ``Italien``, ``Eneas``, ``Romeynen``, ``Lottrijcke`` …), so the simple
   Capital-after-lowercase rule would over-split. The starter-list rule
   splits only on safe sentence-starters (``Ende, Doe, Die, Dit, …``).

   The ``*``-prefixed front-matter pages (``*i.r``, ``*ij.r``, …,
   ``*vi.v``) hold the chronicle's own ``Prologhe`` — substantive
   period prose, not editorial paratext — so they remain classified
   as ``body``.

2. **Drop standalone single-letter / pure-Roman rows.** A handful of
   stranded rows (``B.``, 5× ``C``, ``M.iiijc.``) were extracted as
   their own body rows by the parser — likely chapter / section
   markers and a year marginal note. They have no analytical content
   and trip the validator's <2-letter and pure-Roman fail checks.

No bracket-marker drops needed; the source's ``[…]``-bracketed chapter
titles are period typographic convention (already classified as
``head``) and contain genuine source content.
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
DOC_ID = "1531_excellente_chronijck"
DBNL_ID = "_dit004dits01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"

_PURE_ROMAN_RE = re.compile(r"^[ivxlcdm.\s]+$")


def _drop_marker_rows(rows: list[Row]) -> list[Row]:
    """Drop body rows that are single-letter chapter/section markers
    (``B.``, ``C``, etc.) or pure Roman numerals (``M.iiijc.`` = year
    1400). These are stranded scribal/typographic markers, not source
    prose."""
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
