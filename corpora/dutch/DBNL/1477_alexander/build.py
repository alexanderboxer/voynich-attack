"""Build sentence-level CSV for Die historie ... alexanders (1477; anonymous Middle Dutch romance translation of the Alexander legend).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_ale002alex01`.

Source: https://www.dbnl.org/titels/titel.php?id=_ale002alex01

Text-specific fixes (post-processing only — nothing in the shared parser is
modified):

1. ``split_on_any_capital`` — this 1477 incunable uses commas + mid-line
   capitalisation rather than periods to mark sentence boundaries; the
   default period-based splitter therefore keeps entire paragraphs as
   single rows (median 1,254 letters, max 5,138). Proper nouns in this
   text are *lowercased mid-sentence* (e.g. ``alexander``, ``darius``,
   ``pertsen``), so any Capital letter starting a word is a reliable
   sentence-boundary signal in body text.

2. Two glued proper-noun fixes (``IaphetCam → Iaphet Cam``,
   ``EuropenAffrica → Europen Affrica``) — the parser failed to insert
   whitespace between two sibling inline elements at par=63 and par=64.
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import download_xml, resplit_body_rows, split_on_any_capital
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import format_report, validate

HERE = Path(__file__).parent
DOC_ID = "1477_alexander"
DBNL_ID = "_ale002alex01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"

_GLUE_FIXES: list[tuple[str, str]] = [
    ("IaphetCam", "Iaphet Cam"),
    ("EuropenAffrica", "Europen Affrica"),
]


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = resplit_body_rows(rows, split_fn=split_on_any_capital, glue_fixes=_GLUE_FIXES)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
