"""Filter tls-eebo.csv down to records with publication date before 1550.

Date strings take several forms: "1578", "1580-1620", "-1648" (= upper bound,
NOT a negative year), or "July 9, 1621". We extract the latest 4-digit year
(1000-1999) in the string and filter to year < 1550. Output is sorted by
that extracted year ascending.
"""

import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "tls-eebo.csv"
CUTOFF = 1550
OUT = HERE / f"tls-eebo-pre{CUTOFF}.csv"

YEAR_RE = re.compile(r"\b(1[0-9]{3})\b")


def latest_year(date_str: str) -> int | None:
    years = YEAR_RE.findall(date_str)
    return int(years[-1]) if years else None


def main() -> None:
    skipped_no_year = 0
    total = 0
    kept: list[tuple[int, dict]] = []
    with open(SRC, newline="", encoding="utf-8-sig") as f_in:
        r = csv.DictReader(f_in)
        src_fields = r.fieldnames
        for row in r:
            total += 1
            y = latest_year(row["Publication Date"])
            if y is None:
                skipped_no_year += 1
                continue
            if y < CUTOFF:
                kept.append((y, row))
    kept.sort(key=lambda x: x[0])
    # Column order: MARC ID, URL, Publication Date, Title, then the rest.
    leading = ["MARC ID", "URL", "Publication Date", "Title"]
    out_fields = leading + [c for c in src_fields if c not in leading]
    with open(OUT, "w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(f_out, fieldnames=out_fields)
        w.writeheader()
        for _, row in kept:
            w.writerow(row)
    print(f"read   {total} rows")
    print(f"kept   {len(kept)} (publication year < {CUTOFF})")
    print(f"no year  {skipped_no_year}")
    print(f"wrote  {OUT}")


if __name__ == "__main__":
    main()
