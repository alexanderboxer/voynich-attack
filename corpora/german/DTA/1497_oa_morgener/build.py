"""Build the sentence-level CSV for Morgener 1497 (DTA id oa_morgener_1497)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.normalize import rich_normalize, simple_normalize
from voynpy.corpus_build.schema import Row, write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "oa_morgener_1497"
STEM = "1497_oa_morgener"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


# The TEI source encodes the title as three <l> elements inside the same
# <lg type="poem"> as the ballad itself, so the parser emits them as three
# body paragraphs (rows 0–2) with hyphenated line breaks that don't get
# rejoined across paragraph boundaries. Collapse them into one head row.
_TITLE_FRAGMENTS = (
    "DEs Edlen Ritter Morge-",
    "ners Walfart in sant tho-",
    "mas land. Jn gesang Weisse:",
)
_TITLE_MERGED = "Des Edlen Ritter Morgeners Walfart in sant thomas land. Jn gesang Weisse:"


def _fix_title_page(rows: list[Row]) -> list[Row]:
    assert len(rows) >= 3, "expected at least 3 rows for title-page fixup"
    for i, expected in enumerate(_TITLE_FRAGMENTS):
        actual = rows[i].textstring_orig
        assert actual == expected, (
            f"title-page fixup: row {i} = {actual!r}, expected {expected!r}. "
            f"TEI source may have changed; review before re-applying fixup."
        )
    rich = rich_normalize(_TITLE_MERGED)
    head = Row(
        doc_id=rows[0].doc_id,
        block_type="head",
        para_id=rows[0].para_id,
        sent_id=0,
        is_para_final=True,
        page_n=rows[0].page_n,
        textstring_orig=_TITLE_MERGED,
        textstring_rich=rich,
        textstring_simple=simple_normalize(rich),
    )
    return [head] + rows[3:]


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = _fix_title_page(rows)
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
