"""Build the sentence-level CSV for Walter, Beschreibung Einer Reiß auß Teutschland biß in das (1609)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "walter_beschreibung_1609"
STEM = "1609_walter_beschreibung"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    # Per-text override: this pilgrimage guide has a German→foreign-language
    # dictionary section in the back half (pages 160+) where 2-3 word entries
    # like 'mia', 'thelat mia', 'allff' (Hebrew/Aramaic/Arabic transliterations)
    # plus Latin verse interspersed would corrupt German letter-frequency
    # stats if left in body. Demote any body row with fewer than 10 words to
    # item so the default body-only loader excludes them. Loses some legit
    # short German rows (calendar headers, signature lines in the front
    # matter) but the trade is worth it.
    for r in rows:
        if r.block_type == 'body' and len(r.textstring_simple.split()) < 10:
            r.block_type = 'item'
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
