"""Build the sentence-level CSV for Crüger, Cupediæ Astrosophicæ [...] Darinnen die allerkunst (1631)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.refine import merge_or_demote_short_body

HERE = Path(__file__).parent
DOC_ID = "crueger_cupediae_1631"
STEM = "1631_crueger_cupedi"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    # Per-text override: this astrology/calendar text has scattered body rows
    # that are just space-separated lists of single letters (alphabet runs:
    # "a b c d e f g h i k l m n o p q r s t u", "w x y z", "l l", "r s t u
    # x y z"). They appear in cabbalistic-letter discussions and as
    # post-number-stripping artifacts of measurement tables. Demote rows
    # whose tokens are all single letters to item.
    for r in rows:
        if r.block_type == 'body':
            tokens = r.textstring_simple.split()
            if tokens and all(len(t) == 1 for t in tokens):
                r.block_type = 'item'
    rows = merge_or_demote_short_body(rows)
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
