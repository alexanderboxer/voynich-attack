"""Build sentence-level CSV for Lydgate's Stans puer ad mensam (1476).

John Lydgate's Middle English courtesy poem ("The boy standing at the
table"), printed by Caxton. TCP ID A06567 (Phase I, CC0).
Source: https://github.com/textcreationpartnership/A06567
"""

from pathlib import Path

from voynpy.corpus_build.eebo import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1476_lydgate_stans"
TCP_ID = "A06567"
XML_PATH = HERE / f"{TCP_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {TCP_ID} from EEBO-TCP...")
        download_xml(TCP_ID, XML_PATH)
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
