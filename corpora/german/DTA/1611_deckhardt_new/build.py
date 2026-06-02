"""Build the sentence-level CSV for Deckhardt, New/ Kunstreich vnd Nützliches Kochbuch (1611)."""

import re
from pathlib import Path

from voynpy.corpus_build.dta import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "deckhardt_kochbuch_1611"
STEM = "1611_deckhardt_new"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

# Per-text override: this cookbook has descriptive recipe titles classified as
# <head> in the TEI ("Kapaunen oder Huͤnner auff Boͤmisch einzumachen.").
# Those are content for letter-frequency work, not structural markup.
# Promote heads to body, EXCEPT:
#   - structural markers (CAP. I., Cap. iij., references to Buch/Kochbuch)
#   - pure-numeral fragments ("iii", "iu" standing alone)
#   - the long title page (> 120 chars; recipe titles in deckhardt are < 80)
_KEEP_MARKER = re.compile(r"\b(capit|kapit|cap\.|cap\b)|buch", re.I)
_PURE_NUM = re.compile(r"^\s*[ivxlcm0-9]+\.?\s*$", re.I)
_TITLE_LEN_THRESHOLD = 120


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DOC_ID} from DTA...")
        download_xml(DOC_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    # Reverse parse_tei's auto-promotion of the title page (parser sees a long
    # head without a Kapitel marker and promotes to body; for this cookbook
    # the title page should stay as head).
    for r in rows:
        if r.para_id == 0 and r.sent_id == 0:
            r.block_type = 'head'
            break
    # Promote recipe-title heads to body. Keep as head:
    #   - structural markers (CAP. I., Cap. iij., buch/kochbuch references)
    #   - pure-numeral fragments ("iii" standing alone)
    #   - the title page (handled above; > 120 chars also acts as a guard)
    for r in rows:
        if r.block_type != 'head':
            continue
        t = r.textstring_simple
        if _KEEP_MARKER.search(t):
            continue
        if _PURE_NUM.match(t.strip()):
            continue
        if len(t) > _TITLE_LEN_THRESHOLD:
            continue
        r.block_type = 'body'
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
