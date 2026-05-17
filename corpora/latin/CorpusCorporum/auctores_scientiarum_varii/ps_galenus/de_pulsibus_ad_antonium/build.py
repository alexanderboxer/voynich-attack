"""Build the sentence-level CSV for Ps-Galenus, De pulsibus ad Antonium (c. 0).

Source: Corpus Corporum (mlat.uzh.ch), cc_idno 21599.

Corpus: Auctores scientiarum varii
Author: Ps-Galenus
Work:   De pulsibus ad Antonium
"""

from pathlib import Path

from voynpy.corpus_build.corpus_corporum import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
CC_IDNO = "21599"
STEM = "de_pulsibus_ad_antonium"
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
