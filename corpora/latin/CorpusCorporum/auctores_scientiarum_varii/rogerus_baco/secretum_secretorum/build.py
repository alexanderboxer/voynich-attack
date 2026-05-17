"""Build the sentence-level CSV for Rogerus Baco, Secretum secretorum (c. 1292).

Source: Corpus Corporum (mlat.uzh.ch), cc_idno 12207.

Corpus: Auctores scientiarum varii
Author: Rogerus Baco
Work:   Secretum secretorum

Per-text fix: the CC edition interpolates editorial page anchors of the
form `(p. NNN)` as body content. These are not Bacon's words; filter
them post-parse so they don't pollute body row stats.
"""

import re
from pathlib import Path

from voynpy.corpus_build.corpus_corporum import download_xml
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
CC_IDNO = "12207"
STEM = "secretum_secretorum"
XML_PATH = HERE / f"{STEM}.TEI-P5.xml"
CSV_PATH = HERE / f"{STEM}.csv"

# Match a row whose content is just an editorial page anchor like
# `(p. 47)`, `(P: 139)`, `[pag. 14]`, possibly wrapped in stray
# punctuation, whitespace, or a stray BOM/pipe character.
_PAGE_REF_RE = re.compile(
    r"^[\s.|﻿]*[(\[]\s*p(ag)?[.:]?\s*\d+\s*[)\]][\s.|﻿]*$",
    re.IGNORECASE,
)


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading cc_idno={CC_IDNO} from Corpus Corporum...")
        download_xml(CC_IDNO, XML_PATH)
    rows = parse_tei(str(XML_PATH), CC_IDNO)
    # Drop rows that are pure editorial page anchors like "(p. 39)".
    rows = [r for r in rows if not _PAGE_REF_RE.match(r.textstring_orig or "")]
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
