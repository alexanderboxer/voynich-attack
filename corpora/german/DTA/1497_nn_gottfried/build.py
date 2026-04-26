"""Build the sentence-level CSV for Gottfried 1497 (DTA id nn_gottfried_1497)."""

from pathlib import Path

from lxml import etree

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.normalize import rich_normalize, simple_normalize
from voynpy.corpus_build.schema import Row, write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "nn_gottfried_1497"
STEM = "1497_nn_gottfried"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# The TEI source encodes the entire ballad as a single <p> element with
# <lb/> tags between verse lines. parse_tei collapses <lb/> to whitespace
# and emits one giant body row. Here we re-parse the body <p> directly,
# splitting on <lb/> to emit one row per verse line, with page_n carried
# from the most recent <pb>.
#
# One mid-verse typographic continuation exists (where a verse wraps to a
# second print line via an extra <lb/>); merge it back into the prior line.
_VERSE_CONTINUATIONS = (
    ("Sein gleich fand man nit in", "kein lant"),
)

_LB = "\x00"  # in-band marker for <lb/> while accumulating fragments


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

    # Bring page_n up to the point just before <p> by replaying any earlier
    # <pb> elements in <text> in document order.
    state = {"page_n": None}
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

    for prev, cont in _VERSE_CONTINUATIONS:
        merged = False
        for i in range(len(lines) - 1):
            if lines[i][1] == prev and lines[i + 1][1] == cont:
                lines[i] = (lines[i][0], f"{prev} {cont}")
                del lines[i + 1]
                merged = True
                break
        assert merged, (
            f"continuation not found: {prev!r} -> {cont!r}. "
            f"TEI source may have changed; review before re-applying fixup."
        )

    return lines


def _expand_verse_lines(rows: list[Row]) -> list[Row]:
    head_rows = [r for r in rows if r.block_type == "head"]
    body_rows = [r for r in rows if r.block_type == "body"]
    assert len(body_rows) == 1, f"expected 1 body row, got {len(body_rows)}"

    lines = _parse_verse_lines()

    next_para = max((r.para_id for r in head_rows), default=-1) + 1
    new_rows = list(head_rows)
    for page, text in lines:
        rich = rich_normalize(text)
        new_rows.append(Row(
            doc_id=body_rows[0].doc_id,
            block_type="body",
            para_id=next_para,
            sent_id=0,
            is_para_final=True,
            page_n=page,
            textstring_orig=text,
            textstring_rich=rich,
            textstring_simple=simple_normalize(rich),
        ))
        next_para += 1
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
