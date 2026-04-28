"""Build sentence-level CSV for Dit boecxken leert hoemen mach voghelen vanghen (1509; bird-catching handbook).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_dit005ditb01`.

Source: https://www.dbnl.org/titels/titel.php?id=_dit005ditb01
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import validate, format_report

HERE = Path(__file__).parent
DOC_ID = "1509_voghelen_vanghen"
DBNL_ID = "_dit005ditb01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
