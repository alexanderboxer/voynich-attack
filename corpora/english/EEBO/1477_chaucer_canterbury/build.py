"""Build sentence-level CSV for Caxton's first edition of the
Canterbury Tales (1477).

Caxton's first print of Chaucer's Canterbury Tales (the famous "wHan
that Apprill with his shouris sote…" opening). TCP ID A18548 (Phase I,
CC0). Distinct from the legacy `chaucer` loader, which is a different
transcription.
Source: https://github.com/textcreationpartnership/A18548
"""

from pathlib import Path

from voynpy.corpus_build.eebo import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1477_chaucer_canterbury"
TCP_ID = "A18548"
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
