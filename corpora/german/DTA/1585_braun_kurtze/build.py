"""Build the sentence-level CSV for Braun, Kurtze vnd Einfeltige Predigt/ bey dem Begrebnis d (1585)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "524292"
STEM = "1585_braun_kurtze"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    write_csv(rows, str(CSV_PATH))
    paras = {r.para_id for r in rows}
    by_block: dict[str, int] = {}
    for r in rows:
        by_block[r.block_type] = by_block.get(r.block_type, 0) + 1
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    print(f"  paragraphs: {len(paras)}")
    print(f"  rows by block_type: {by_block}")


if __name__ == "__main__":
    main()
