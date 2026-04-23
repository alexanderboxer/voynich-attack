"""Generic TEI-P5 parser: XML → sentence-level Rows.

Walks `<text>/<body>` and emits one Row per (paragraph, sentence).

- `<p>` and `<head>` are paragraph-producing (block_type='body', 'head').
- `<div>` is traversed; no row for the div itself.
- `<note>`, `<figure>`, `<fw>`, `<gap>` contents are elided inline.
- `<pb/>` updates the running `page_n`.
- `<choice>` uses the first preferred child: reg > expan > corr > orig > abbr > sic.
- `<lb/>` / `<cb/>` are soft line breaks; hyphenated breaks join across lines.

Front and back matter are ignored in this MVP.
"""

import re
from typing import Optional

from lxml import etree

from .normalize import rich_normalize, simple_normalize
from .schema import Row, split_sentences

TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}

_TAG_PREFIX = f"{{{TEI_NS}}}"


def _tag(elem) -> str:
    t = elem.tag
    if isinstance(t, str) and t.startswith(_TAG_PREFIX):
        return t[len(_TAG_PREFIX):]
    return t if isinstance(t, str) else ""


_PARA_KIND = {"p": "body", "head": "head"}
# Multi-line paragraph containers: each child <l> becomes a row within a
# single paragraph (para_id), with sent_id incrementing per line.
_PARA_MULTI_LINE_KIND = {"lg": "verse"}
_SKIP_INLINE = {"note", "figure", "fw", "gap"}
_SOFT_BREAK = {"lb", "cb"}
_CHOICE_PREFER = ("reg", "expan", "corr", "orig", "abbr", "sic")


def _update_page(elem, state: dict) -> None:
    n = elem.get("n")
    if n:
        state["page_n"] = n
    else:
        state["page_seq"] = state.get("page_seq", 0) + 1
        state["page_n"] = str(state["page_seq"])


def _inline_text(elem, state: dict) -> str:
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        ctag = _tag(child)
        if ctag == "pb":
            _update_page(child, state)
        elif ctag in _SOFT_BREAK:
            parts.append("\n")
        elif ctag in _SKIP_INLINE:
            pass
        elif ctag == "choice":
            picked = None
            for pref in _CHOICE_PREFER:
                picked = child.find(f"tei:{pref}", NS)
                if picked is not None:
                    break
            if picked is None and len(child):
                picked = child[0]
            if picked is not None:
                parts.append(_inline_text(picked, state))
        else:
            parts.append(_inline_text(child, state))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


_HYPHEN_LB_RE = re.compile(r"-\s*\n\s*")
_LB_RE = re.compile(r"\s*\n\s*")
_WS_RE = re.compile(r"\s+")


def _post_process(s: str) -> str:
    s = _HYPHEN_LB_RE.sub("", s)
    s = _LB_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


_SECTION_LETTER_RE = re.compile(r"^\s*[A-Za-z]\.?\s*$")


def _emit_rows(orig: str, doc_id: str, block_type: str, para_id: int, state: dict) -> list[Row]:
    if not orig:
        return []
    sents = split_sentences(orig)
    if not sents:
        return []
    last_idx = len(sents) - 1
    out = []
    for i, sent in enumerate(sents):
        rich = rich_normalize(sent)
        out.append(
            Row(
                doc_id=doc_id,
                block_type=block_type,
                para_id=para_id,
                sent_id=i,
                is_para_final=(i == last_idx),
                page_n=state.get("page_n"),
                textstring_orig=sent,
                textstring_rich=rich,
                textstring_simple=simple_normalize(rich),
            )
        )
    return out


def _emit_multi_line_from_list(lines: list[str], doc_id: str, block_type: str, para_id: int, state: dict) -> list[Row]:
    """Emit one row per verse line from a pre-extracted list of line strings.
    sent_id increments per line within the paragraph."""
    if not lines:
        return []
    out = []
    last_idx = len(lines) - 1
    for i, orig in enumerate(lines):
        rich = rich_normalize(orig)
        out.append(
            Row(
                doc_id=doc_id,
                block_type=block_type,
                para_id=para_id,
                sent_id=i,
                is_para_final=(i == last_idx),
                page_n=state.get("page_n"),
                textstring_orig=orig,
                textstring_rich=rich,
                textstring_simple=simple_normalize(rich),
            )
        )
    return out


def _walk(elem, doc_id: str, counter: dict, state: dict) -> list[Row]:
    rows: list[Row] = []
    tag = _tag(elem)
    if tag in _PARA_KIND:
        block_type = _PARA_KIND[tag]
        orig = _post_process(_inline_text(elem, state))
        # Whole paragraph is just a section-letter marker (e.g. <p>B.</p>):
        # buffer it to prepend to the next paragraph. Don't emit a row.
        if _SECTION_LETTER_RE.match(orig):
            state["pending_prefix"] = state.get("pending_prefix", "") + orig + " "
            return rows
        pending = state.pop("pending_prefix", "")
        if pending:
            orig = (pending + orig).strip()
        para_rows = _emit_rows(orig, doc_id, block_type, counter["para_id"], state)
        if para_rows:
            counter["para_id"] += 1
            rows.extend(para_rows)
    elif tag in _PARA_MULTI_LINE_KIND:
        block_type = _PARA_MULTI_LINE_KIND[tag]
        # Walk children in document order. Accumulate direct <l> children
        # into a running paragraph; when a nested <lg> is hit, flush the
        # accumulation and recurse into the nested stanza. Document order
        # is preserved for paragraph numbering.
        pending: list[str] = []

        def flush():
            if not pending:
                return
            para_rows = _emit_multi_line_from_list(
                pending, doc_id, block_type, counter["para_id"], state
            )
            if para_rows:
                counter["para_id"] += 1
                rows.extend(para_rows)
            pending.clear()

        for child in elem:
            ctag = _tag(child)
            if ctag == "l":
                line_orig = _post_process(_inline_text(child, state))
                if line_orig:
                    pending.append(line_orig)
            elif ctag == "lg":
                flush()
                rows.extend(_walk(child, doc_id, counter, state))
            elif ctag == "pb":
                _update_page(child, state)
            # else: ignore (lb, notes, etc.)
        flush()
    elif tag == "pb":
        _update_page(elem, state)
    elif tag in _SKIP_INLINE:
        pass
    else:
        for child in elem:
            rows.extend(_walk(child, doc_id, counter, state))
    return rows


def parse_tei(xml_path: str, doc_id: str) -> list[Row]:
    """Parse a TEI-P5 XML into sentence-level Rows. Only `<text>/<body>` is walked."""
    tree = etree.parse(xml_path)
    root = tree.getroot()
    text_elem = root.find("tei:text", NS)
    if text_elem is None:
        raise ValueError(f"no <text> element in {xml_path}")
    body = text_elem.find("tei:body", NS)
    if body is None:
        raise ValueError(f"no <body> element in {xml_path}")
    counter = {"para_id": 0}
    state: dict = {"page_n": None, "page_seq": 0}
    return _walk(body, doc_id, counter, state)
