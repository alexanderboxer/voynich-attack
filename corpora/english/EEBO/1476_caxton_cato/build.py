"""Build sentence-level CSV for Caxton's Parvus Catho (1476).

Caxton's printed edition of the Distichs of Cato. TCP ID A18231 (Phase I,
CC0). Source: https://github.com/textcreationpartnership/A18231

Bilingual structure: each <lg> wraps a <head><l>...</l></head> Latin
distich followed by <l> children of Caxton's English verse translation.
The parser's lg-walk only emits direct <l> children, so the Latin would
otherwise be dropped. We pre-process the XML to promote the Latin <l>s
out of <head> and into leading <l> siblings of <lg>, so the body rows
contain Latin first, then English, in original reading order.
"""

from pathlib import Path

from lxml import etree

from voynpy.corpus_build.eebo import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1476_caxton_cato"
TCP_ID = "A18231"
XML_PATH = HERE / f"{TCP_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"
PROCESSED_XML = HERE / f"{TCP_ID}.latin-promoted.xml"

_TEI_NS = "{http://www.tei-c.org/ns/1.0}"
_LG = f"{_TEI_NS}lg"
_HEAD = f"{_TEI_NS}head"
_L = f"{_TEI_NS}l"
_GAP = f"{_TEI_NS}gap"

# EEBO-TCP transcribers mark hand-illuminated drop-cap initials they
# couldn't / wouldn't reconstruct as <gap reason="illegible" extent="1
# letter"/>. The first body line of this text starts with such a gap,
# producing "Vm aīduerterem…" where the original reads "Cum animaduerterem"
# (the opening of the Distichs of Cato). We restore the C here.
#
# Keys are 0-indexed positions among `<gap extent="1 letter">` elements
# in document order. Add more entries as you identify reconstructable
# initials (other Latin distichs in this text also begin with drop-cap
# gaps; their letters could be inferred by anyone with the Latin source).
_DROP_CAP_INITIALS = {
    0: "C",  # "Cum animum aduerterem…"
}


def _restore_drop_caps(tree) -> int:
    """Replace each `<gap extent="1 letter">` listed in _DROP_CAP_INITIALS
    with its known initial letter; leave others as-is. Returns the count
    of gaps restored."""
    restored = 0
    idx = 0
    # Collect first to avoid mutating during iteration.
    gaps = [g for g in tree.getroot().iter(_GAP) if g.get("extent") == "1 letter"]
    for gap in gaps:
        letter = _DROP_CAP_INITIALS.get(idx)
        idx += 1
        if letter is None:
            continue
        parent = gap.getparent()
        prev = gap.getprevious()
        tail = gap.tail or ""
        # Splice the letter (and any tail) into the previous sibling's tail
        # (or parent's text if the gap was the first child).
        if prev is None:
            parent.text = (parent.text or "") + letter + tail
        else:
            prev.tail = (prev.tail or "") + letter + tail
        parent.remove(gap)
        restored += 1
    return restored


def _promote_lg_head_lines(src: Path, dst: Path) -> None:
    """For each <lg>: move every <l> inside <head> to be a leading sibling
    of the existing <l>s (preserving order), then drop the now-empty <head>.
    Also restores known drop-cap initials. Writes the modified tree to `dst`."""
    tree = etree.parse(str(src))
    # Restore drop caps first (gap order changes after head-promotion).
    restored = _restore_drop_caps(tree)
    promoted = 0
    for lg in tree.getroot().iter(_LG):
        head = lg.find(_HEAD)
        if head is None:
            continue
        latin_ls = head.findall(_L)
        if not latin_ls:
            lg.remove(head)
            continue
        head_idx = list(lg).index(head)
        for i, l in enumerate(latin_ls):
            head.remove(l)
            lg.insert(head_idx + i, l)
        lg.remove(head)
        promoted += 1
    tree.write(str(dst), encoding="utf-8", xml_declaration=True)
    print(f"  restored {restored} drop-cap initial(s); promoted Latin lines from {promoted} <lg>/<head> blocks")


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {TCP_ID} from EEBO-TCP...")
        download_xml(TCP_ID, XML_PATH)
    _promote_lg_head_lines(XML_PATH, PROCESSED_XML)
    rows = parse_tei(str(PROCESSED_XML), DOC_ID)
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
