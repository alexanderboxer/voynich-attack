"""Sanity checks for parsed corpus_build CSVs.

Run after each new text is parsed to catch over-splitting (Roman numerals,
biblical citations leaking out as fragments), low-body texts (head- or
item-dominated outputs that need special handling or exclusion), and other
parser anomalies.

Three severity levels:
- **failures** — the parse is broken; should block the build.
- **warnings** — suspicious; flag for human review.
- **info** — descriptive stats, always printed.

Usage:
    from voynpy.corpus_build.validate import validate, format_report
    report = validate("path/to/parsed.csv")
    print(format_report(report))
    # raises if report.failures (caller may also choose to handle gracefully)
"""

import csv
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


ROMAN_LETTERS = set("ivxlcdm")
ROMAN_NUMERAL_RE = re.compile(r"^[ivxlcdm.\s]+$")
LETTER_RE = re.compile(r"[a-z]")
WORD_RE = re.compile(r"[a-z]+")


@dataclass
class Report:
    csv_path: str
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: dict = field(default_factory=dict)


def _letter_count(s: str) -> int:
    return len(LETTER_RE.findall(s))


def _percentile(sorted_vals: list[int], p: float) -> int:
    if not sorted_vals:
        return 0
    idx = int(len(sorted_vals) * p / 100)
    idx = max(0, min(idx, len(sorted_vals) - 1))
    return sorted_vals[idx]


def validate(csv_path: str | Path) -> Report:
    csv_path = str(csv_path)
    report = Report(csv_path=csv_path)

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        report.failures.append("CSV has zero rows")
        return report

    # 1. Block-type breakdown — both row counts and letter counts.
    by_block_rows: Counter = Counter()
    by_block_letters: Counter = Counter()
    for r in rows:
        bt = r.get("block_type") or ""
        n = _letter_count(r.get("textstring_simple", ""))
        by_block_rows[bt] += 1
        by_block_letters[bt] += n

    total_rows = sum(by_block_rows.values())
    total_letters = sum(by_block_letters.values())
    body_rows = by_block_rows.get("body", 0)
    body_letters = by_block_letters.get("body", 0)
    nonbody_letters = total_letters - body_letters

    body_row_pct = 100 * body_rows / max(total_rows, 1)
    body_letter_pct = 100 * body_letters / max(total_letters, 1)

    report.info["rows_by_block"] = dict(by_block_rows)
    report.info["letters_by_block"] = dict(by_block_letters)
    report.info["body_row_pct"] = round(body_row_pct, 1)
    report.info["body_letter_pct"] = round(body_letter_pct, 1)

    # Body-dominance thresholds
    if body_letter_pct < 30:
        report.failures.append(
            f"body letter % = {body_letter_pct:.1f}% (< 30) — text is mostly head/item; "
            f"consider a special-case build.py or excluding."
        )
    elif body_letter_pct < 50:
        report.warnings.append(
            f"body letter % = {body_letter_pct:.1f}% (< 50) — non-body content dominates; review."
        )
    if body_row_pct < 25:
        report.failures.append(f"body row % = {body_row_pct:.1f}% (< 25)")
    elif body_row_pct < 40:
        report.warnings.append(f"body row % = {body_row_pct:.1f}% (< 40)")
    if body_letters > 0 and nonbody_letters / body_letters > 2.0:
        report.failures.append(
            f"non-body letters / body letters = {nonbody_letters/body_letters:.2f}× (> 2)"
        )
    elif body_letters > 0 and nonbody_letters / body_letters > 0.5:
        report.warnings.append(
            f"non-body / body letter ratio = {nonbody_letters/body_letters:.2f}× (> 0.5)"
        )

    # 2. Sentence-length distribution (body rows only).
    body_lens = sorted(
        _letter_count(r.get("textstring_simple", ""))
        for r in rows if r.get("block_type") == "body"
    )
    if body_lens:
        report.info["body_sentence_letters"] = {
            "min": body_lens[0],
            "p5": _percentile(body_lens, 5),
            "median": _percentile(body_lens, 50),
            "p95": _percentile(body_lens, 95),
            "max": body_lens[-1],
        }
        if body_lens[0] < 2:
            n = sum(1 for x in body_lens if x < 2)
            report.failures.append(f"{n} body sentences have < 2 letters")
        if _percentile(body_lens, 5) < 10:
            report.warnings.append(
                f"p5 body sentence length = {_percentile(body_lens, 5)} letters (< 10) — "
                "many short sentences; possible over-splitting"
            )
        if _percentile(body_lens, 50) < 30:
            report.warnings.append(
                f"median body sentence length = {_percentile(body_lens, 50)} letters (< 30) — "
                "probable over-splitting"
            )

    # 3. Roman-numeral / abbreviation leak checks.
    pure_roman = []
    last_word_roman = []
    for r in rows:
        if r.get("block_type") != "body":
            continue
        simple = r.get("textstring_simple", "").strip()
        if simple and ROMAN_NUMERAL_RE.fullmatch(simple):
            pure_roman.append(r)
        words = WORD_RE.findall(simple)
        if words:
            last = words[-1]
            if 1 <= len(last) <= 5 and all(c in ROMAN_LETTERS for c in last):
                last_word_roman.append((r, last))

    report.info["pure_roman_sentences"] = len(pure_roman)
    report.info["sentences_ending_in_roman_word"] = len(last_word_roman)

    if pure_roman:
        report.failures.append(
            f"{len(pure_roman)} body sentences are pure Roman numerals — over-splitting"
        )
    body_count = max(body_rows, 1)
    if len(last_word_roman) > body_count * 0.01:
        report.warnings.append(
            f"{len(last_word_roman)} body sentences end in a Roman-numeral-only word "
            f"({100*len(last_word_roman)/body_count:.1f}% of body rows; > 1%) — possible "
            "Roman-numeral leak"
        )

    # 4. Empty / degenerate rows.
    empty_simple = sum(1 for r in rows if not r.get("textstring_simple", "").strip())
    if empty_simple:
        report.warnings.append(f"{empty_simple} rows have empty textstring_simple")

    # 5. Top short last-words (info — abbreviation candidates).
    last_short = Counter()
    for r in rows:
        if r.get("block_type") != "body":
            continue
        words = WORD_RE.findall(r.get("textstring_simple", "").strip())
        if words and len(words[-1]) <= 3:
            last_short[words[-1]] += 1
    report.info["top_short_last_words"] = last_short.most_common(15)

    return report


def format_report(report: Report) -> str:
    out: list[str] = []
    out.append(f"=== validate {report.csv_path} ===")
    if report.failures:
        out.append(f"\nFAILURES ({len(report.failures)}):")
        for f in report.failures:
            out.append(f"  ✗ {f}")
    if report.warnings:
        out.append(f"\nWARNINGS ({len(report.warnings)}):")
        for w in report.warnings:
            out.append(f"  ⚠ {w}")
    if report.info:
        out.append("\nINFO:")
        for k, v in report.info.items():
            out.append(f"  {k}: {v}")
    if not report.failures and not report.warnings:
        out.append("\n  ✓ all checks passed")
    return "\n".join(out)


def main() -> None:
    """CLI: `python -m voynpy.corpus_build.validate path/to.csv`."""
    import sys
    if len(sys.argv) < 2:
        print("usage: python -m voynpy.corpus_build.validate <csv_path>")
        sys.exit(2)
    report = validate(sys.argv[1])
    print(format_report(report))
    sys.exit(1 if report.failures else 0)


if __name__ == "__main__":
    main()
