"""Build sentence-level CSV for Der IX quaesten (1528; nine evil rulers / vices).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_qua001quae01`.

Source: https://www.dbnl.org/titels/titel.php?id=_qua001quae01

Text-specific fix: ``split_on_starter_words`` with the default
``COMMON_DUTCH_STARTERS`` set. This 1528 print uses mid-line
capitalisation rather than periods for sentence boundaries (default
parser leaves rows up to 1,050 letters), but proper nouns are
*capitalised* mid-sentence (Old-Testament and classical figures:
``Achab``, ``Israhel``, ``Benadap``, ``Iudas``, ``Pylatus``,
``Naboth``, ``Pilatus``, ``Ruben`` …). A simple Capital-after-
lowercase rule would over-split on every biblical name; the
starter-list approach splits only on the safe sentence-starter
words (``Ende, Doe, Dit, Die, …``).

The shared ``resplit_body_rows`` also filters non-Latin-alphabet
chunks, which drops the Greek printer's flourish at the end of the
colophon (``γμοθοωιλντομ`` — par 90, page H4v).
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import (
    download_xml,
    resplit_body_rows,
    split_on_starter_words,
)
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import format_report, validate

HERE = Path(__file__).parent
DOC_ID = "1528_ix_quaesten"
DBNL_ID = "_qua001quae01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = resplit_body_rows(rows, split_fn=split_on_starter_words)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
