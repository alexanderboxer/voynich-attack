"""Build the sentence-level CSV for Fabritius, Medicina animae: Seelen Artzney (1638)."""

import re
from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "539478"
STEM = "1638_fabritius_medicina"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

# Per-text override: this is a religious text ("Soul-Medicine"), not a
# pharmacy text — the "medicina" in the title is metaphorical. It contains
# many one-line biblical citations like "Matth. 15. v. 9.", "Joh: 11. cap:
# ꝟ. 25.", "Eph: 2. ꝟ. 8. 9." that become fragmentary in textstring_simple
# after number-stripping ("matth u", "ioh cap", "eph"). Detect biblical-
# citation rows via the ORIG column pattern (capital book-name + . or :
# + digit) and demote to item.
_BIBL_CITATION = re.compile(
    r'^\s*\d?\s*\d?\s*[A-ZÄÖÜ][a-zA-ZäöüßſꝟĳɁ]{1,8}[.:]\s*\d+'
)


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    n_demoted = 0
    for r in rows:
        if r.block_type != 'body':
            continue
        # Demote when EITHER:
        # - orig starts with biblical-citation pattern AND simple has <5 words
        #   (bare citations like "Matth. 15. v. 9.", but not citation+verse-text)
        # - simple has <=2 words (Latin fragments like "Laus Christo",
        #   "Spiritualia sapit", or stray short sermon address fragments
        #   that contribute too little to be useful and corrupt sentence stats)
        nwords = len(r.textstring_simple.split())
        if _BIBL_CITATION.match(r.textstring_orig) and nwords < 5:
            r.block_type = 'item'
            n_demoted += 1
        elif nwords <= 2:
            r.block_type = 'item'
            n_demoted += 1
    print(f"  demoted {n_demoted} short / bare-citation body rows to item")
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
