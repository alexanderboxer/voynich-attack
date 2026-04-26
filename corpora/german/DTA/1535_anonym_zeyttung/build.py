"""Build the sentence-level CSV for Anonym Zeyttung 1535
(DTA id anonym_zeyttung_1535)."""

from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.normalize import rich_normalize, simple_normalize
from voynpy.corpus_build.schema import Row, write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "anonym_zeyttung_1535"
STEM = "1535_anonym_zeyttung"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

# This text uses the virgule "/" as the all-purpose punctuation mark and
# has body paragraphs of ~600 tokens with no period inside. Split body
# rows at "/ Word" where Word is a clause-starting function word, so the
# resulting rows roughly correspond to sentences. Applied only to this
# text — other ENHG texts use periods more conventionally and don't need
# the virgule rule.
_VIRGULE_CLAUSE_STARTERS = frozenset({
    "Aber", "Also", "Auch", "Auff", "Aus", "Auß",
    "Bald",
    "Da", "Daher", "Damit", "Dann", "Darauff", "Darnach", "Darumb",
    "Demnach", "Doch", "Durch",
    "Es",
    "Für", "Fur",
    "Hat", "Hatten", "Hie", "Hierauff",
    "Ich", "Jch", "Item", "Jtem", "Ist", "Jst",
    "Ja",
    "Nach", "Nun",
    "Ob", "Oben", "Oder",
    "So", "Sol", "Sollen", "Sondern", "Sind",
    "Vber", "Vmb", "Vnd", "Vns", "Vnser", "Vor",
    "Wann", "Was", "Weil", "Wenn", "Wie", "Wirt", "Wo", "Wollen",
    "Zu", "Zur",
})


def _split_at_virgule_clauses(text: str) -> list[str]:
    """Split `text` at occurrences of `/ Word` where Word is a known clause
    starter. Returns a list of segments (each ending with `/` except the
    last). Whitespace at the boundary between segments is normalized."""
    segments: list[str] = []
    start = 0
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "/":
            j = i + 1
            while j < n and text[j].isspace():
                j += 1
            end = j
            while end < n and text[end].isalpha():
                end += 1
            if j < n and text[j].isupper() and text[j:end] in _VIRGULE_CLAUSE_STARTERS:
                segments.append(text[start:i + 1].strip())
                start = j
                i = j
                continue
        i += 1
    tail = text[start:].strip()
    if tail:
        segments.append(tail)
    return [s for s in segments if s]


def _expand_virgule_clauses(rows: list[Row]) -> list[Row]:
    out: list[Row] = []
    para_id = 0
    for r in rows:
        if r.block_type != "body":
            r.para_id = para_id
            out.append(r)
            if r.is_para_final:
                para_id += 1
            continue
        segs = _split_at_virgule_clauses(r.textstring_orig)
        if len(segs) <= 1:
            r.para_id = para_id
            out.append(r)
            if r.is_para_final:
                para_id += 1
            continue
        # Replace the row with one row per segment in this paragraph.
        last_idx = len(segs) - 1
        for i, seg in enumerate(segs):
            rich = rich_normalize(seg)
            out.append(Row(
                doc_id=r.doc_id,
                block_type=r.block_type,
                para_id=para_id,
                sent_id=i,
                is_para_final=(i == last_idx and r.is_para_final),
                page_n=r.page_n,
                textstring_orig=seg,
                textstring_rich=rich,
                textstring_simple=simple_normalize(rich),
            ))
        if r.is_para_final:
            para_id += 1
    return out


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = _expand_virgule_clauses(rows)
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
