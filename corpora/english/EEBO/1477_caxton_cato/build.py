"""Build sentence-level CSV for Caxton's Parvus Catho — Latin/English (1477).

Caxton's print of the Distichs of Cato. TCP ID A18230 (Phase I, CC0).
Like the 1476 edition (A18231 / 1476_caxton_cato), this is bilingual —
each Latin distich is followed by Caxton's English verse translation —
but the TEI encoding differs: instead of `<lg><head><l/></head><l/></lg>`,
this edition has bare `<l>` siblings as direct children of each `<div>`
section, with no `<lg>` wrapping. The parser only emits `<l>` content
when it's inside `<lg>`, so we pre-process the XML to wrap each section's
`<l>` siblings in a single `<lg>` element. The resulting body rows
interleave Latin and English in original reading order.
"""

from pathlib import Path

from lxml import etree

from voynpy.corpus_build.eebo import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1477_caxton_cato"
TCP_ID = "A18230"
XML_PATH = HERE / f"{TCP_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"
PROCESSED_XML = HERE / f"{TCP_ID}.lg-wrapped.xml"

_TEI_NS = "{http://www.tei-c.org/ns/1.0}"
_DIV = f"{_TEI_NS}div"
_LG = f"{_TEI_NS}lg"
_L = f"{_TEI_NS}l"


def _wrap_bare_l_in_lg(src: Path, dst: Path) -> int:
    """For each <div> that has direct <l> children, group consecutive <l>s
    into a single <lg> element so the parser's lg-walk picks them up."""
    tree = etree.parse(str(src))
    wrapped = 0
    for div in tree.getroot().iter(_DIV):
        children = list(div)
        # Find runs of consecutive <l> children.
        i = 0
        while i < len(children):
            if children[i].tag != _L:
                i += 1
                continue
            j = i
            while j < len(children) and children[j].tag == _L:
                j += 1
            run = children[i:j]
            # Replace the run with one <lg> wrapping them.
            insert_idx = list(div).index(run[0])
            lg = etree.SubElement(div, _LG)
            div.remove(lg)  # remove (it was appended at end); re-insert at idx
            for l_elem in run:
                div.remove(l_elem)
                lg.append(l_elem)
            div.insert(insert_idx, lg)
            wrapped += 1
            # children list is stale; re-fetch
            children = list(div)
            i = insert_idx + 1
    tree.write(str(dst), encoding="utf-8", xml_declaration=True)
    return wrapped


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {TCP_ID} from EEBO-TCP...")
        download_xml(TCP_ID, XML_PATH)
    n = _wrap_bare_l_in_lg(XML_PATH, PROCESSED_XML)
    print(f"  wrapped {n} run(s) of bare <l> children in <lg>")
    rows = parse_tei(str(PROCESSED_XML), DOC_ID)
    # Specific reconstruction of the first Latin distich. The source has
    #   `a<gap/><macron>adùterē`
    # where the gap (1 illegible letter), the orphan macron, and the
    # u-with-grave together encode `nima…uer…m` of `animaduerterem`. The
    # combination is too irregular to handle in normalize.py — fix the
    # one row directly by substituting in textstring_simple.
    for r in rows:
        if r.block_type == "body" and "a aduteren" in r.textstring_simple:
            r.textstring_simple = r.textstring_simple.replace(
                "a aduteren", "animaduerterem"
            )
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
