"""Build sentence-level CSV for Dictes or Sayings of the Philosophers (1477).

Caxton's print of Earl Rivers' English translation of "Dits Moraulx des
Philosophes" — collected sayings of ancient philosophers. TCP ID A69207
(Phase I, CC0). Source: https://github.com/textcreationpartnership/A69207
"""

import re
from pathlib import Path

from voynpy.corpus_build.eebo import download_xml
from voynpy.corpus_build.normalize import rich_normalize, simple_normalize
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei

HERE = Path(__file__).parent
DOC_ID = "1477_dictes"
TCP_ID = "A69207"
XML_PATH = HERE / f"{TCP_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"

# Short rows like "And sayde.", "¶And said.", "He ansuerd." are speech-
# introducer fragments that the source separates from the actual quoted
# text by a period. They should attach to the following row (the quote).
# Match: optional ¶, a few words, ending with a form of `say`/`answer`
# followed by `.`.
_INTRODUCER_RE = re.compile(
    r"^¶?\s*\w+(?:\s+\w+){0,3}\s+(?:saide?|sayde?|ansuere?d|ansuerd)\.?\s*$",
    re.IGNORECASE,
)


def _merge_speech_introducers(rows):
    """Glue short speech-introducer rows to the next row's text."""
    out = []
    pending_intro = None
    for r in rows:
        if pending_intro is not None:
            r.textstring_orig = pending_intro.textstring_orig + " " + r.textstring_orig
            r.textstring_rich = rich_normalize(r.textstring_orig)
            r.textstring_simple = simple_normalize(r.textstring_rich)
            pending_intro = None
        if (
            r.block_type == "body"
            and len(r.textstring_orig) <= 30
            and _INTRODUCER_RE.match(r.textstring_orig)
        ):
            pending_intro = r
            continue
        out.append(r)
    # If a pending introducer has no successor, keep it as-is
    if pending_intro is not None:
        out.append(pending_intro)
    # Renumber sent_id within paragraphs
    by_para = {}
    last_idx = {}
    for r in out:
        by_para.setdefault(r.para_id, []).append(r)
    for pid, group in by_para.items():
        for i, r in enumerate(group):
            r.sent_id = i
            r.is_para_final = (i == len(group) - 1)
    return out


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {TCP_ID} from EEBO-TCP...")
        download_xml(TCP_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = _merge_speech_introducers(rows)
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
