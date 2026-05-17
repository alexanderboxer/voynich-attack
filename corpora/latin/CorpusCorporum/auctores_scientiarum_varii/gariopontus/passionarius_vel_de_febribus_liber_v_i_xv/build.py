"""Build the sentence-level CSV for Gariopontus, Passionarius vel De febribus, liber V, i-xv (c. 1059).

Source: Corpus Corporum (mlat.uzh.ch), cc_idno 12203.

Corpus: Auctores scientiarum varii
Author: Gariopontus
Work:   Passionarius vel De febribus, liber V, i-xv
"""

from pathlib import Path

from voynpy.corpus_build.corpus_corporum import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
CC_IDNO = "12203"
STEM = "passionarius_vel_de_febribus_liber_v_i_xv"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading cc_idno={CC_IDNO} from Corpus Corporum...")
        download_xml(CC_IDNO, XML_PATH)
    rows = parse_tei(str(XML_PATH), CC_IDNO)
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
