"""Build the sentence-level CSV for Hayn, Officina mystica (1645)."""

import re
from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.refine import merge_or_demote_short_body

HERE = Path(__file__).parent
DOC_ID = "360001"
STEM = "1645_hayn_officina"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

# Per-text override: this scholastic/mystical text uses A/B/C and a/b/c
# single-letter outline markers as the first "word" of many body
# paragraphs (e.g., "B Nachmals allerley Actiones Verrichtungen..." or
# "b sawr Schleebluttoder Sawrampffwasser"). Strip the leading single
# letter + space — they're not part of the sentence. EXCEPTION: the
# German vocative particle "O" ("O Friedrich, mein Sohn!") IS
# grammatical content; keep it.
_LEAD_SINGLE_LETTER = re.compile(r'^([A-Za-zÄÖÜäöüß])\s+')


def _strip_lead(text: str) -> str:
    m = _LEAD_SINGLE_LETTER.match(text)
    if not m:
        return text
    return text[m.end():]


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    stripped = 0
    for r in rows:
        if r.block_type != 'body':
            continue
        m = _LEAD_SINGLE_LETTER.match(r.textstring_simple)
        if not m:
            continue
        if m.group(1).lower() == 'o':
            continue  # German vocative
        r.textstring_simple = _strip_lead(r.textstring_simple)
        r.textstring_rich = _strip_lead(r.textstring_rich)
        r.textstring_orig = _strip_lead(r.textstring_orig)
        stripped += 1
    print(f"  stripped outline-letter prefix from {stripped} body rows")
    rows = merge_or_demote_short_body(rows)
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
