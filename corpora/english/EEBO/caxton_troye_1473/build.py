"""Build sentence-level CSV for Caxton's Recuyell of the Historyes of Troye (1473).

First book printed in English. TCP ID A05232 (Phase I, CC0).
Source: https://github.com/textcreationpartnership/A05232
"""

from pathlib import Path

from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "caxton_troye_1473"
TCP_ID = "A05232"
XML_PATH = HERE / f"{TCP_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
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
