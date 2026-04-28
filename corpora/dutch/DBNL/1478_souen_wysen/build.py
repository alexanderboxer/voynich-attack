"""Build sentence-level CSV for De historia van den souen wysen meisteren (ca.1478; Middle Low German / Middle Dutch incunable Seven Sages of Rome).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `_his022hist01`.

Source: https://www.dbnl.org/titels/titel.php?id=_his022hist01

Text-specific fix: ``split_on_starter_words`` with a text-specific
starter list. Unlike Alexander 1477, *proper nouns in this text are
capitalised mid-sentence* (``Lyppolt``, ``Conrat``, ``Ihesus``,
``Cristus``, ``Sunte pauwel``, ``Zacharias`` …), so the simple
"any Capital after lowercase = sentence break" rule used for the
Hollandish incunabula would over-split on every proper noun.

Splits only when the Capital word is in the curated `_STARTERS` set
(plus pilcrow ¶ as a sentence marker). The set is text-specific and
deliberately *narrower* than ``COMMON_DUTCH_STARTERS`` — it excludes
words like ``Heer``, ``Mijn``, ``Mer`` etc. that don't reliably mark
sentence starts in this Low German source.
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import (
    download_xml,
    resplit_body_rows,
    split_on_starter_words,
)
from voynpy.corpus_build.schema import write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import format_report, validate

HERE = Path(__file__).parent
DOC_ID = "1478_souen_wysen"
DBNL_ID = "_his022hist01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


# Text-specific starter list. Curated from inspection of long body rows
# in this specific text. Deliberately *narrower* than the COMMON list to
# avoid splits on words that turn out to be ambiguous in this source.
_STARTERS = frozenset({
    "Id", "He", "Se", "De", "Een", "Doe", "Do",
    "Sich", "Hier", "Hir", "Ende", "Wente", "Auer", "Aver",
    "Dat", "Item", "Also", "Alsoo", "Alse", "Wor", "To",
    "Vp", "Up", "An", "In", "Vnde", "Vnd", "Och", "Hoe",
    "Hoer", "Wat", "Sunte", "Sinte", "Mer", "Eens", "Wol",
    "Nu", "Nv", "So", "Dy", "Ick", "Ic",
})


def _split_fn(text: str) -> list[str]:
    return split_on_starter_words(text, starters=_STARTERS)


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = resplit_body_rows(rows, split_fn=_split_fn)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
