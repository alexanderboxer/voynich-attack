"""Build sentence-level CSV for Die historie vanden vromen ridder parijs ende van die schone vienna (1487; Middle Dutch romance).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_his017hist01`.

Source: https://www.dbnl.org/titels/titel.php?id=_his017hist01

Text-specific fix: ``split_on_any_capital``. This 1487 incunable shares
the Hollandish convention (proper nouns lowercase mid-sentence:
``paris``, ``vienne``, ``dyane``, ``eduwaert``, ``dolfijn``), so any
Capital after lowercase reliably marks a sentence boundary. No glue
fixes needed.
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import download_xml, resplit_body_rows, split_on_any_capital
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import format_report, validate

HERE = Path(__file__).parent
DOC_ID = "1487_parijs_ende_vienna"
DBNL_ID = "_his017hist01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = resplit_body_rows(rows, split_fn=split_on_any_capital)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
