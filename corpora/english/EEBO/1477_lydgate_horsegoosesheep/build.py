"""Build sentence-level CSV for Lydgate's Horse, Goose, and Sheep (1477).

John Lydgate's debate poem "The horse, the goose, and the sheep",
printed by Caxton. TCP ID A06553 (Phase I, CC0).
Source: https://github.com/textcreationpartnership/A06553
"""

from pathlib import Path

from voynpy.corpus_build.eebo import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1477_lydgate_horsegoosesheep"
TCP_ID = "A06553"
XML_PATH = HERE / f"{TCP_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {TCP_ID} from EEBO-TCP...")
        download_xml(TCP_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    # The text encodes collective-noun lists (an herd of hertes / of cranys
    # …) and proverbial sayings as <item>s, but for our purposes they're
    # part of the running body content — relabel them so the default
    # body-only loader picks them up.
    for r in rows:
        if r.block_type == "item":
            r.block_type = "body"
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
