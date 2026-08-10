"""Build sentence-level CSV for Bonaventure des Périers, Nouvelles récréations (1558).

Source: Project Gutenberg #54819, P. L. Jacob (Paul Lacroix), ed., with Charles Nodier notice.
"""
from pathlib import Path

from voynpy.corpus_build.gutenberg import (
    build_from_manifest,
    download_gutenberg,
)

HERE = Path(__file__).parent
DOC_ID = "1558_bonaventure_perier"
GUTENBERG_ID = 54819

MANIFEST_PATH = HERE / "manifest.json"
RAW_PATH = HERE / "raw.txt"
CSV_PATH = HERE / f"{DOC_ID}.csv"


def main() -> None:
    if not RAW_PATH.exists():
        print(f"downloading Gutenberg #{GUTENBERG_ID}...")
        download_gutenberg(GUTENBERG_ID, RAW_PATH)
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
