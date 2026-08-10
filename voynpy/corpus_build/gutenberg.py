"""Project Gutenberg source helpers for pre-1600 vernacular text corpora.

Unlike DBNL / DTA / CorpusCorporum (which provide TEI XML), Project
Gutenberg publishes plain-text (UTF-8) editions. Each text is ingested
via a per-text ``manifest.json`` that specifies:

- ``gutenberg_id``  — the ebook ID (integer)
- ``doc_id``        — e.g. ``1461_villon_oeuvres``
- ``start_line``,
  ``end_line``      — 1-indexed inclusive bounds over the raw .txt,
                      selecting the period-language portion and excluding
                      Gutenberg boilerplate, editorial front/back matter,
                      modern translations, notes, glossaries, etc.
- ``strip_patterns`` — regex list applied to the selected slice to strip
                      intra-text editorial insertions (footnotes,
                      illustration markers, page references, etc.)

The module produces a report with a period-vs-modern orthography count
that flags likely modernization; each text's build.py prints the report
so a human reviewer can accept or reject the ingest.

Row shape follows ``voynpy.corpus_build.schema`` (9 columns; one row per
sentence, paragraphs tracked via ``para_id`` and ``is_para_final``).
"""

import json
import re
from pathlib import Path
from urllib.request import urlopen

from .normalize import rich_normalize, simple_normalize
from .schema import Row, split_sentences, write_csv


GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"


# Diagnostic pairs for period-vs-modern French orthography.
# (period_form, modern_form). Matched as whole-word occurrences on
# the lowercase text. Presence of many period forms and near-zero modern
# forms indicates preserved period orthography.
PERIOD_MODERNIZATION_PAIRS = [
    ("avoit", "avait"),
    ("estoit", "était"),
    ("auoit", "avait"),
    ("iustice", "justice"),
    ("iustement", "justement"),
    ("iettans", "jetant"),
    ("veue", "vue"),
    ("mesme", "même"),
    ("feust", "fût"),
    ("iceluy", "celui"),
    ("sçavoir", "savoir"),
]


def download_gutenberg(gid: int, dest: Path) -> None:
    """Fetch the plain-text Gutenberg edition and write to ``dest``."""
    url = GUTENBERG_URL.format(gid=gid)
    with urlopen(url) as f:
        data = f.read()
    dest.write_bytes(data)


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove content outside the ``*** START ... ***`` / ``*** END ... ***``
    markers. Applied defensively; per-manifest line bounds are the primary
    selection mechanism."""
    start_re = re.compile(r"^\*\*\* START OF .*?\*\*\*\s*$", re.MULTILINE)
    end_re = re.compile(r"^\*\*\* END OF .*?\*\*\*\s*$", re.MULTILINE)
    m_start = start_re.search(text)
    m_end = end_re.search(text)
    body_start = m_start.end() if m_start else 0
    body_end = m_end.start() if m_end else len(text)
    return text[body_start:body_end]


def slice_by_lines(text: str, start_line: int, end_line: int) -> str:
    """1-indexed inclusive line slice over ``text``."""
    lines = text.split("\n")
    return "\n".join(lines[start_line - 1:end_line])


def strip_editorial_patterns(text: str, patterns: list[str]) -> str:
    """Apply each regex in ``patterns`` as a substitution to a single space.
    Multi-space runs are then collapsed."""
    for pat in patterns:
        text = re.sub(pat, " ", text, flags=re.DOTALL)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def orthography_report(text: str) -> dict:
    """Count period-vs-modern form occurrences over ``text``.

    Returns a dict with:
      - verdict:      "period" | "modernized" | "inconclusive"
      - period_total, modern_total (whole-word counts summed over pairs)
      - pairs:        {"<period>/<modern>": (period_count, modern_count)}
    """
    lower = text.lower()
    results = {}
    period_total = 0
    modern_total = 0
    for period, modern in PERIOD_MODERNIZATION_PAIRS:
        p_count = len(re.findall(r"\b" + re.escape(period) + r"\b", lower))
        m_count = len(re.findall(r"\b" + re.escape(modern) + r"\b", lower))
        results[f"{period}/{modern}"] = (p_count, m_count)
        period_total += p_count
        modern_total += m_count
    if period_total == 0 and modern_total == 0:
        verdict = "inconclusive"
    elif period_total >= modern_total:
        verdict = "period"
    else:
        verdict = "modernized"
    return {
        "verdict": verdict,
        "period_total": period_total,
        "modern_total": modern_total,
        "pairs": results,
    }


def segment_paragraphs(text: str) -> list[list[str]]:
    """Split ``text`` into paragraphs (blank-line-delimited), then each
    paragraph into sentences via ``schema.split_sentences``. Returns a list
    of lists of sentence strings. Empty paragraphs are dropped."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_paragraphs = re.split(r"\n\s*\n", text)
    result: list[list[str]] = []
    for para in raw_paragraphs:
        flat = re.sub(r"\s+", " ", para).strip()
        if not flat:
            continue
        sentences = split_sentences(flat)
        if sentences:
            result.append(sentences)
    return result


def is_header_paragraph(sentences: list[str]) -> bool:
    """Heuristic: a paragraph is a "head" block if it is a single short
    line that is overwhelmingly uppercase (chapter or section title)."""
    if len(sentences) != 1:
        return False
    s = sentences[0]
    if len(s) > 100:
        return False
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return False
    if sum(1 for c in letters if c.isupper()) / len(letters) < 0.9:
        return False
    return True


def build_from_manifest(
    manifest_path: Path,
    raw_text_path: Path,
    csv_path: Path,
) -> dict:
    """End-to-end: read manifest, slice raw text, strip editorial noise,
    segment, write CSV, return an orthography report and row/paragraph
    counts. Per-text ``build.py`` scripts call this."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    doc_id = manifest["doc_id"]
    start_line = manifest["start_line"]
    end_line = manifest["end_line"]
    strip_patterns = manifest.get("strip_patterns", [])

    raw = raw_text_path.read_text(encoding="utf-8")

    body = slice_by_lines(raw, start_line, end_line)
    body = strip_editorial_patterns(body, strip_patterns)

    ortho = orthography_report(body)

    paragraphs = segment_paragraphs(body)
    rows: list[Row] = []
    for pid, sents in enumerate(paragraphs):
        block_type = "head" if is_header_paragraph(sents) else "body"
        for sid, sent in enumerate(sents):
            is_final = (sid == len(sents) - 1)
            rich = rich_normalize(sent)
            simple = simple_normalize(rich)
            rows.append(Row(
                doc_id=doc_id,
                block_type=block_type,
                para_id=pid,
                sent_id=sid,
                is_para_final=is_final,
                page_n=None,
                textstring_orig=sent,
                textstring_rich=rich,
                textstring_simple=simple,
            ))

    write_csv(rows, str(csv_path))

    return {
        "rows": len(rows),
        "paragraphs": len(paragraphs),
        "orthography": ortho,
    }
