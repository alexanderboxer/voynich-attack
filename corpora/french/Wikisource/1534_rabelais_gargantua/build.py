"""Build sentence-level CSV for Rabelais Gargantua (1534).

Source: Wikisource FR export of the 1535 François Juste (Lyon) edition, exported
2021-06-11 and preserved in this repo. The raw text is pre-existing (no fresh
download); this build.py just applies the shared ``build_from_manifest`` logic
to produce the standard 9-column CSV.
"""
from pathlib import Path

from voynpy.corpus_build.gutenberg import build_from_manifest

HERE = Path(__file__).parent
DOC_ID = "1534_rabelais_gargantua"

MANIFEST_PATH = HERE / "manifest.json"
RAW_PATH = HERE / "raw.txt"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not RAW_PATH.exists():
        raise SystemExit(f"raw.txt missing at {RAW_PATH}; expected pre-existing Wikisource export")
    result = build_from_manifest(MANIFEST_PATH, RAW_PATH, CSV_PATH)
    print(f"wrote {result['rows']} rows ({result['paragraphs']} paragraphs) -> {CSV_PATH}")
    ortho = result["orthography"]
    print(f"orthography verdict: {ortho['verdict']} "
          f"(period={ortho['period_total']}, modern={ortho['modern_total']})")
    for k, (p, m) in ortho["pairs"].items():
        if p > 0 or m > 0:
            print(f"  {k}: period={p} modern={m}")


if __name__ == "__main__":
    main()
