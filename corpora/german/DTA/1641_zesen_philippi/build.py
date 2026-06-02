"""Build the sentence-level CSV for Zesen, Philippi Cæsii Deutsches Helicons Ander Theil (1641)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.refine import merge_or_demote_short_body

HERE = Path(__file__).parent
DOC_ID = "zesen_helikon02_1641"
STEM = "1641_zesen_philippi"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    # Per-text override: Zesen's verse collection uses TEI <l> elements
    # within <lg>. The parser emits one row per <l>, AND each <l> often
    # becomes its own paragraph. Physical-line wrappings ("die Sappho" /
    # "schwingt"; "...ich möcht es gerne" / "wissen") therefore become two
    # body rows in two paragraphs. Merge single-word body rows into the
    # preceding body row regardless of paragraph boundary — undoes
    # spurious line-wrap splits even across paragraphs.
    merged_rows = []
    n_merged = 0
    for r in rows:
        if (r.block_type == 'body'
                and len(r.textstring_simple.split()) == 1
                and merged_rows
                and merged_rows[-1].block_type == 'body'):
            prev = merged_rows[-1]
            prev.textstring_simple = prev.textstring_simple + ' ' + r.textstring_simple
            prev.textstring_rich = prev.textstring_rich + ' ' + r.textstring_rich
            prev.textstring_orig = prev.textstring_orig + ' ' + r.textstring_orig
            if r.is_para_final:
                prev.is_para_final = True
            n_merged += 1
            continue
        merged_rows.append(r)
    print(f"  merged {n_merged} single-word continuations into preceding row")
    merged_rows = merge_or_demote_short_body(merged_rows)
    write_csv(merged_rows, str(CSV_PATH))
    paras = {r.para_id for r in rows}
    by_block: dict[str, int] = {}
    for r in rows:
        by_block[r.block_type] = by_block.get(r.block_type, 0) + 1
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    print(f"  paragraphs: {len(paras)}")
    print(f"  rows by block_type: {by_block}")


if __name__ == "__main__":
    main()
