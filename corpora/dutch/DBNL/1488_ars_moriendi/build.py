"""Build sentence-level CSV for Ars moriendi (1488).

Anonymous Middle Dutch *art of dying* treatise, first edition Peter van Os,
Zwolle, 1488. DBNL provides a diplomatic TEI Lite transcription preserving
period orthography. DBNL ID `_ars002arsm01`.

Source: https://www.dbnl.org/titels/titel.php?id=_ars002arsm01
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1488_ars_moriendi"
DBNL_ID = "_ars002arsm01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
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
