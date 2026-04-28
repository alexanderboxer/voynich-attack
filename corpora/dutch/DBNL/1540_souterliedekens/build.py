"""Build sentence-level CSV for Souterliedekens (1540; Dutch metrical psalter / verse).

DBNL provides a diplomatic TEI Lite transcription. DBNL ID `zuyl004sout02`.

Source: https://www.dbnl.org/titels/titel.php?id=zuyl004sout02

This is a verse text (psalm translations set to popular tunes). Each
``<l>`` (verse line) becomes a separate body row with a typically short
letter count (median ~24 letters), so the validator's "median < 30"
warning is *expected* and benign here — it indicates correct
line-by-line verse parsing, not over-splitting.

Text-specific fixes:

1. **Drop ``<2`` Latin-letter body rows.** Two stranded ``'V'`` rows
   (par=4520, par=5702) appear as orphan capital-V from verse-initial
   "V" (= "you" formal) where surrounding text was lost in the
   parse. Filtered as marker rows.

2. **Skip the splitter.** The verse rows are already line-split; no
   ``split_on_starter_words`` or ``split_on_any_capital`` is applied.
   Adding one would over-split short verse lines that happen to
   contain a sentence-starter capital.

The shared parser fix (joining ``<cell>`` text with whitespace, see
``tei_p5.py`` table handling) means this text's *Registere der wijsen*
psalm-index table now correctly emits ``"fray v. psalm"`` rather than
``"frayv. psalm"`` — psalm numbers are properly word-separated from
their tune incipits.

Note: ~10 verse rows contain hyphenated word fragments (``'Be-'``,
``'Ver-'``, ``'len'``, ``'ken'``, ``'sen'`` …) where source-side
end-of-line hyphenation wasn't rejoined across ``<lb/>`` breaks. Minor
(~0.1% of body rows) and not addressed here.
"""

from pathlib import Path

from voynpy.corpus_build.dbnl import download_xml
from voynpy.corpus_build.schema import Row, write_csv
from voynpy.corpus_build.tei_p5 import parse_tei
from voynpy.corpus_build.validate import format_report, validate

HERE = Path(__file__).parent
DOC_ID = "1540_souterliedekens"
DBNL_ID = "zuyl004sout02"
XML_PATH = HERE / f"{DBNL_ID}.xml"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def _drop_marker_rows(rows: list[Row]) -> list[Row]:
    """Drop body rows with <2 Latin a-z letters (orphan single-letter
    fragments)."""
    out = []
    for r in rows:
        if r.block_type == "body":
            simple = r.textstring_simple.strip()
            n_letters = sum(1 for c in simple if "a" <= c <= "z")
            if n_letters < 2:
                continue
        out.append(r)
    return out


def main() -> None:
    if not XML_PATH.exists():
        print(f"downloading {DBNL_ID} from DBNL...")
        download_xml(DBNL_ID, XML_PATH)
    rows = parse_tei(str(XML_PATH), DOC_ID)
    rows = _drop_marker_rows(rows)
    write_csv(rows, str(CSV_PATH))
    print(f"wrote {len(rows)} rows -> {CSV_PATH}")
    report = validate(CSV_PATH)
    print()
    print(format_report(report))
    if report.failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
