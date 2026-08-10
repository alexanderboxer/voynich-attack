"""Build sentence-level CSV for Rabelais Pantagruel (1532).

Source: Wikisource FR export of the ca. 1532 Claude Nourry (Lyon) first
edition, exported 2021-06-11 and preserved in this repo.
"""
from pathlib import Path

from voynpy.corpus_build.gutenberg import build_from_manifest

HERE = Path(__file__).parent
DOC_ID = "1532_rabelais_pantagruel"

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
