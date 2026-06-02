"""Build the sentence-level CSV for Hoepner, Leich-Predigt/ Vber das Sprüchlein S. Luc. am 10 C (1637)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "510799"
STEM = "1637_hoepner_leich"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    # Per-text override: demote 1- or 2-word body rows to item — they're
    # signature initials ("A. B."), interjection fragments ("reiber",
    # "meynt"), or stray Latin degree markers ("Philosophiae Baccalaureus")
    # that are too short to contribute meaningful sentence statistics.
    n_demoted = 0
    for r in rows:
        if r.block_type == 'body' and len(r.textstring_simple.split()) <= 2:
            r.block_type = 'item'
            n_demoted += 1
    print(f"  demoted {n_demoted} 1-2 word body rows to item")
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
