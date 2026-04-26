"""Build the sentence-level CSV for Has 1516 (DTA id has_spruch_1516)."""

from pathlib import Path

from lxml import etree

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.normalize import rich_normalize, simple_normalize
from voynpy.corpus_build.schema import Row, write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "has_spruch_1516"
STEM = "1516_has_spruch"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# The body's first <p> encodes the entire ballad as one element with <lb/>
# tags between verse lines (same pattern as gottfried1497). parse_tei
# collapses those <lb/>s and emits one giant body row. We re-parse just the
# first <p> here, splitting on <lb/> to emit one row per verse line.
# No mid-verse typographic continuations in this text (verified by line-
# length audit). The second <p> (colophon "Gedꝛuͤckt zu Nuͤrnberg…") is
# left as parse_tei produced it.
_LB = "\x00"


def _walk(elem, parts: list, state: dict) -> None:
    if elem.text:
        parts.append((state["page_n"], elem.text))
    for c in elem:
        tag = etree.QName(c).localname
        if tag == "lb":
            parts.append((state["page_n"], _LB))
        elif tag == "pb":
            n = c.get("n")
            if n:
                state["page_n"] = n
        elif tag == "choice":
            for pref in ("corr", "reg", "expan", "orig", "sic"):
                sub = c.find(f"tei:{pref}", _NS)
                if sub is not None:
                    _walk(sub, parts, state)
                    break
        elif tag in {"note", "figure", "fw", "gap"}:
            pass
        else:
            _walk(c, parts, state)
        if c.tail:
            parts.append((state["page_n"], c.tail))


def _parse_verse_lines() -> list[tuple[str | None, str]]:
    tree = etree.parse(str(XML_PATH))
    text_elem = tree.getroot().find("tei:text", _NS)
    body = text_elem.find("tei:body", _NS)
    p_elem = body.find(".//tei:p", _NS)
    assert p_elem is not None, "no <p> in body"

    state: dict = {"page_n": None}
    for e in text_elem.iter():
        if e is p_elem:
            break
        if etree.QName(e).localname == "pb":
            n = e.get("n")
            if n:
                state["page_n"] = n

    parts: list[tuple[str | None, str]] = []
    _walk(p_elem, parts, state)

    lines: list[tuple[str | None, str]] = []
    buf: list[str] = []
    line_page: str | None = None
    for page, frag in parts:
        if frag == _LB:
            text = "".join(buf).strip()
            if text:
                lines.append((line_page, text))
            buf.clear()
            line_page = None
        else:
            buf.append(frag)
            if line_page is None and page is not None:
                line_page = page
    text = "".join(buf).strip()
    if text:
        lines.append((line_page, text))
    return lines


def _expand_verse_lines(rows: list[Row]) -> list[Row]:
    head_rows = [r for r in rows if r.block_type == "head"]
    body_rows = [r for r in rows if r.block_type == "body"]
    # Para 0 = head (title), para 1 = giant verse <p>, para 2+ = colophon.
    verse_rows = [r for r in body_rows if r.para_id == 1]
    colophon_rows = [r for r in body_rows if r.para_id != 1]
    assert len(verse_rows) == 1, f"expected 1 verse row, got {len(verse_rows)}"

    lines = _parse_verse_lines()

    new_rows = list(head_rows)
    para_id = max((r.para_id for r in head_rows), default=-1) + 1
    for page, text in lines:
        rich = rich_normalize(text)
        new_rows.append(Row(
            doc_id=verse_rows[0].doc_id,
            block_type="body",
            para_id=para_id,
            sent_id=0,
            is_para_final=True,
            page_n=page,
            textstring_orig=text,
            textstring_rich=rich,
            textstring_simple=simple_normalize(rich),
        ))
        para_id += 1
    # Renumber colophon para_ids to follow the verse rows.
    for r in colophon_rows:
        new_rows.append(Row(
            doc_id=r.doc_id,
            block_type=r.block_type,
            para_id=para_id,
            sent_id=r.sent_id,
            is_para_final=r.is_para_final,
            page_n=r.page_n,
            textstring_orig=r.textstring_orig,
            textstring_rich=r.textstring_rich,
            textstring_simple=r.textstring_simple,
        ))
        if r.is_para_final:
            para_id += 1
    return new_rows


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = _expand_verse_lines(rows)
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
