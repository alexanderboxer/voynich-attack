"""Build sentence-level CSV for Die ridderlycke reyse van Vertimans (1544; Dutch translation of Varthema's *Itinerario*, Antwerp print).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `vart002ridd01`.

Source: https://www.dbnl.org/titels/titel.php?id=vart002ridd01

Text-specific fix: ``split_on_starter_words`` with the default
``COMMON_DUTCH_STARTERS`` set. The travel narrative has many capitalised
proper nouns mid-sentence (place names ``Portegale``, ``Narsinga``,
``Lisbonen``, ``Bisinagar``, ``Calcoeten``, ``Cuzin``, ``Helena`` …;
person names ``Bartholomeo``, ``Uincente``, ``Thomas``, ``Johan`` …;
religious / cultural terms ``Christenen``, ``Cristenen``, ``Paradijs``,
``Ascensione`` …), so the simple Capital-after-lowercase rule would
over-split. The starter-list rule splits only on safe sentence-starters
(``Ende, Doe, Die, Dit, …``).
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
DOC_ID = "1544_ridderlycke_reyse"
DBNL_ID = "vart002ridd01"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = resplit_body_rows(rows, split_fn=split_on_starter_words)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
