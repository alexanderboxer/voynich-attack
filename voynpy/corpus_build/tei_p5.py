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
from .schema import Row, split_sentences_with_offsets


def _letter_count_inline(s: str) -> int:
    return sum(1 for ch in s if ch.isalpha())

TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}

_TAG_PREFIX = f"{{{TEI_NS}}}"


def _tag(elem) -> str:
    t = elem.tag
    if isinstance(t, str) and t.startswith(_TAG_PREFIX):
        return t[len(_TAG_PREFIX):]
    return t if isinstance(t, str) else ""


def _find(elem, name):
    """Find first child with given local-name, namespace-agnostic.
    Tries TEI-P5 namespace first, then falls back to no-namespace
    (TEI Lite / TEI.2, used by DBNL)."""
    found = elem.find(f"tei:{name}", NS)
    if found is None:
        found = elem.find(name)
    return found


_PARA_KIND = {"p": "body", "head": "head", "closer": "body"}
# Atomic paragraph-producing tags: one row per element, no sentence-splitting
# within. Internal periods are treated as decorative scribal punctuation
# (e.g. citation lists "Auicenna. Primo. Secundo tertio. Quarto canonum").
# `titlePage` joins all its titlePart/byline/imprint descendants into a single
# head row — preserves long title pages like springer 1509.
_ATOMIC_KIND = {"item": "item", "titlePage": "head"}
# Multi-line paragraph containers: each child of the specified child-tag
# becomes one row within a single paragraph (para_id), with sent_id
# incrementing per line.  Value: (block_type, child_tag_that_is_a_line).
# Used for verse stanzas where the line boundaries are meaningful. We emit
# block_type='body' so verse-only texts (meerwunder, has_lob) are loadable
# with the default body-only loader config.
_PARA_MULTI_LINE_KIND = {
    "lg":  ("body", "l"),
}
_SKIP_INLINE = {"note", "figure", "fw", "gap"}
_SOFT_BREAK = {"lb", "cb"}
_CHOICE_PREFER = ("reg", "expan", "corr", "orig", "abbr", "sic")


_FACS_RE = re.compile(r"#f(\d+)")


def _update_page(elem, state: dict) -> None:
    n = elem.get("n")
    if n:
        state["page_n"] = n
        return
    facs = elem.get("facs")
    if facs:
        m = _FACS_RE.match(facs)
        if m:
            state["page_n"] = str(int(m.group(1)))
            return
    state["page_seq"] = state.get("page_seq", 0) + 1
    state["page_n"] = str(state["page_seq"])


_PAGE_MARK_OPEN = ""
_PAGE_MARK_CLOSE = ""
_PAGE_MARK_RE = re.compile(r"([^]*)")
_BIBL_OPEN = ""
_BIBL_CLOSE = ""
_BIBL_MARKS_RE = re.compile(r"[]")


def _emit_page_mark(state: dict) -> str:
    page = state.get("page_n") or ""
    return f"{_PAGE_MARK_OPEN}{page}{_PAGE_MARK_CLOSE}"


def _inline_text(elem, state: dict) -> str:
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        ctag = _tag(child)
        if ctag == "pb":
            _update_page(child, state)
            # Embed an in-band sentinel so per-sentence page_n can be
            # resolved later. Sentinels are alphanumeric/non-whitespace, so
            # they survive _post_process regexes; paragraph callers extract
            # marks via _post_process_paged, others strip them in _post_process.
            parts.append(_emit_page_mark(state))
        elif ctag in _SOFT_BREAK:
            parts.append("\n")
        elif ctag in _SKIP_INLINE:
            pass
        elif ctag == "supplied" and (child.get("resp") or "").startswith("#textsource"):
            # Editorial bibliographic supplement (DTA convention), not original
            # text. Other <supplied> elements (missing-letter reconstructions)
            # fall through to the default branch and are included inline.
            pass
        elif ctag == "choice":
            picked = None
            for pref in _CHOICE_PREFER:
                picked = _find(child, pref)
                if picked is not None:
                    break
            if picked is None and len(child):
                picked = child[0]
            if picked is not None:
                parts.append(_inline_text(picked, state))
        elif ctag == "bibl":
            # Wrap citation content with sentinel markers so the
            # surrounding parser can attach a trailing citation to its
            # preceding sentence (`\u0003` blocks the dot-boundary
            # check before it, `\u0004` forces a sentence boundary
            # after the citation closes).
            parts.append(_BIBL_OPEN)
            parts.append(_inline_text(child, state))
            parts.append(_BIBL_CLOSE)
        else:
            parts.append(_inline_text(child, state))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


_HYPHEN_LB_RE = re.compile(r"-\s*\n\s*(\S)?")
_LB_RE = re.compile(r"\s*\n\s*")
_WS_RE = re.compile(r"\s+")


def _hyphen_lb_sub(m) -> str:
    """Hyphen + line-break handling: rejoin only when the next non-whitespace
    character is lowercase (a genuine hyphenated word continuation). When the
    following text starts with uppercase (e.g. a sibling element's content
    such as a proper noun, place name, or section heading), keep them
    separated by a space rather than gluing the words together."""
    nxt = m.group(1) or ""
    if nxt and nxt.islower():
        return nxt
    return " " + nxt


def _strip_marks(s: str) -> tuple[str, list[tuple[int, "Optional[str]"]]]:
    """Strip page sentinels and return (clean_text, list of (offset, page))."""
    out: list[str] = []
    marks: list[tuple[int, "Optional[str]"]] = []
    out_len = 0
    last = 0
    for m in _PAGE_MARK_RE.finditer(s):
        seg = s[last:m.start()]
        out.append(seg)
        out_len += len(seg)
        marks.append((out_len, m.group(1) or None))
        last = m.end()
    out.append(s[last:])
    return "".join(out), marks


def _sub_with_marks(
    pattern, replacement, text: str,
    marks: list[tuple[int, "Optional[str]"]],
) -> tuple[str, list[tuple[int, "Optional[str]"]]]:
    """Apply pattern.sub(replacement, text) and rebase mark offsets. Marks
    inside a substituted span are repositioned to the start of the replacement.
    `replacement` may be a string or a callable taking re.Match → str."""
    is_callable = callable(replacement)
    out_parts: list[str] = []
    out_len = 0
    last = 0
    mi = 0
    n_marks = len(marks)
    new_marks: list[tuple[int, "Optional[str]"]] = []
    for m in pattern.finditer(text):
        seg = text[last:m.start()]
        out_parts.append(seg)
        while mi < n_marks and marks[mi][0] < m.start():
            off, page = marks[mi]
            new_marks.append((out_len + (off - last), page))
            mi += 1
        out_len += len(seg)
        repl = replacement(m) if is_callable else replacement
        out_parts.append(repl)
        while mi < n_marks and marks[mi][0] <= m.end():
            new_marks.append((out_len, marks[mi][1]))
            mi += 1
        out_len += len(repl)
        last = m.end()
    seg = text[last:]
    out_parts.append(seg)
    while mi < n_marks:
        off, page = marks[mi]
        new_marks.append((out_len + (off - last), page))
        mi += 1
    return "".join(out_parts), new_marks


def _strip_ends_with_marks(
    text: str, marks: list[tuple[int, "Optional[str]"]],
) -> tuple[str, list[tuple[int, "Optional[str]"]]]:
    lstripped = text.lstrip()
    leading = len(text) - len(lstripped)
    rstripped = lstripped.rstrip()
    new_len = len(rstripped)
    new_marks = [
        (min(max(0, off - leading), new_len), page) for off, page in marks
    ]
    return rstripped, new_marks


def _post_process(s: str) -> str:
    # Strip sentinels first so they don't break hyphen-rejoin /
    # whitespace-collapse logic, then run the standard cleanup. Both page
    # sentinels and <bibl> sentinels are stripped here — non-paragraph
    # callers don't use sentence-level page tracking or trailing-citation
    # boundary semantics.
    s = _PAGE_MARK_RE.sub("", s)
    s = _BIBL_MARKS_RE.sub("", s)
    s = _HYPHEN_LB_RE.sub(_hyphen_lb_sub, s)
    s = _LB_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


def _post_process_paged(s: str) -> tuple[str, list[tuple[int, "Optional[str]"]]]:
    """Like _post_process but extract page sentinels into (offset, page) marks
    measured against the returned clean text. Marks are tracked through each
    regex substitution and the final end-strip."""
    text, marks = _strip_marks(s)
    text, marks = _sub_with_marks(_HYPHEN_LB_RE, _hyphen_lb_sub, text, marks)
    text, marks = _sub_with_marks(_LB_RE, " ", text, marks)
    text, marks = _sub_with_marks(_WS_RE, " ", text, marks)
    text, marks = _strip_ends_with_marks(text, marks)
    return text, marks


_SECTION_LETTER_RE = re.compile(r"^\s*[A-Za-z]\.?\s*$")


def _rendition_has_red(elem) -> bool:
    rend = elem.get("rendition")
    if not rend:
        return False
    return "#red" in rend.split()


def _cell_full_text(cell, state: dict) -> str:
    return _post_process(_inline_text(cell, state))


def _cell_red_text(cell, state: dict) -> str:
    parts = []
    for hi in cell.iter(f"{_TAG_PREFIX}hi"):
        if _rendition_has_red(hi):
            parts.append(_inline_text(hi, state))
    return _post_process(" ".join(parts))


def _row_is_all_red(cells, state: dict) -> bool:
    """True if at least one cell has text and every non-empty cell's text
    is fully contained inside <hi rendition="#red"> spans."""
    saw_text = False
    for cell in cells:
        full = _cell_full_text(cell, state)
        if not full:
            continue
        saw_text = True
        red = _cell_red_text(cell, state)
        if full != red:
            return False
    return saw_text


def _emit_rows(
    orig: str,
    doc_id: str,
    block_type: str,
    para_id: int,
    state: dict,
    page_at_start: Optional[str] = None,
    marks: Optional[list[tuple[int, Optional[str]]]] = None,
) -> list[Row]:
    """Emit one row per sentence in `orig`. If `marks` is provided, assign
    each sentence the page_n that was active at its starting offset (using
    `page_at_start` for sentences before the first mark). Otherwise fall
    back to the latest tracked page in `state`."""
    if not orig:
        return []
    sents_with_off = split_sentences_with_offsets(orig)
    if not sents_with_off:
        return []
    last_idx = len(sents_with_off) - 1
    fallback_page = state.get("page_n") if marks is None else page_at_start
    out = []
    for i, (sent_start, sent) in enumerate(sents_with_off):
        if marks:
            page = page_at_start
            for off, pn in marks:
                if off <= sent_start:
                    page = pn
                else:
                    break
        else:
            page = fallback_page
        # Strip <bibl> sentinels and collapse any whitespace they leave behind.
        clean = _BIBL_MARKS_RE.sub("", sent)
        clean = _WS_RE.sub(" ", clean).strip()
        if not clean:
            continue
        rich = rich_normalize(clean)
        out.append(
            Row(
                doc_id=doc_id,
                block_type=block_type,
                para_id=para_id,
                sent_id=len(out),
                is_para_final=(i == last_idx),
                page_n=page,
                textstring_orig=clean,
                textstring_rich=rich,
                textstring_simple=simple_normalize(rich),
            )
        )
    if out:
        out[-1].is_para_final = True
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
    if tag == "sp":
        # Drama / dialog speech: <sp><speaker>...</speaker><p>...</p></sp>.
        # Stash the speaker text in pending_prefix so the next <p> picks it
        # up at the start of its first emitted sentence; then walk the rest
        # of the children normally. Trim any trailing `.` from the speaker
        # — otherwise the period plus an uppercase first word in the speech
        # triggers `split_sentences` to break the speaker off into its own
        # row.
        speaker = _find(elem, "speaker")
        if speaker is not None:
            spk_text = _post_process(_inline_text(speaker, state)).rstrip(".")
            if spk_text:
                state["pending_prefix"] = state.get("pending_prefix", "") + spk_text + " "
        for child in elem:
            if _tag(child) == "speaker":
                continue
            rows.extend(_walk(child, doc_id, counter, state))
    elif tag in _PARA_KIND:
        block_type = _PARA_KIND[tag]
        page_at_start = state.get("page_n")
        orig, marks = _post_process_paged(_inline_text(elem, state))
        # Whole paragraph is just a section-letter marker (e.g. <p>B.</p>):
        # buffer it to prepend to the next paragraph. Don't emit a row.
        if _SECTION_LETTER_RE.match(orig):
            state["pending_prefix"] = state.get("pending_prefix", "") + orig + " "
            return rows
        pending = state.pop("pending_prefix", "")
        if pending:
            orig = pending + orig
            marks = [(off + len(pending), page) for off, page in marks]
            orig, marks = _strip_ends_with_marks(orig, marks)
        para_rows = _emit_rows(
            orig, doc_id, block_type, counter["para_id"], state,
            page_at_start=page_at_start, marks=marks,
        )
        if para_rows:
            counter["para_id"] += 1
            rows.extend(para_rows)
    elif tag in _ATOMIC_KIND:
        block_type = _ATOMIC_KIND[tag]
        orig = _post_process(_inline_text(elem, state))
        if orig and _letter_count_inline(orig) >= 1:
            rich = rich_normalize(orig)
            rows.append(Row(
                doc_id=doc_id,
                block_type=block_type,
                para_id=counter["para_id"],
                sent_id=0,
                is_para_final=True,
                page_n=state.get("page_n"),
                textstring_orig=orig,
                textstring_rich=rich,
                textstring_simple=simple_normalize(rich),
            ))
            counter["para_id"] += 1
    elif tag in _PARA_MULTI_LINE_KIND:
        block_type, line_tag = _PARA_MULTI_LINE_KIND[tag]
        # Walk children in document order. Default: accumulate direct
        # line-children into a running paragraph and flush on each nested
        # same-kind container (stanzas become paragraphs). Exception: a
        # flat <lg type="poem"> with no nested <lg>s (a stanza-less poem
        # like has_lob 1490) emits each <l> as its own paragraph.
        has_nested = any(_tag(c) == tag for c in elem)
        treat_as_flat = not has_nested and elem.get("type") == "poem"
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
            if ctag == line_tag:
                line_orig = _post_process(_inline_text(child, state))
                if not line_orig:
                    continue
                if treat_as_flat:
                    para_rows = _emit_multi_line_from_list(
                        [line_orig], doc_id, block_type, counter["para_id"], state
                    )
                    if para_rows:
                        counter["para_id"] += 1
                        rows.extend(para_rows)
                else:
                    pending.append(line_orig)
            elif ctag == tag:
                # same-kind nested container (e.g. <lg> inside <lg>)
                flush()
                rows.extend(_walk(child, doc_id, counter, state))
            elif ctag == "pb":
                _update_page(child, state)
            # else: ignore (lb, notes, etc.)
        flush()
    elif tag == "pb":
        _update_page(elem, state)
    elif tag == "table":
        # Each <row> becomes one paragraph. Header rows:
        # - the first row of the table, and any row immediately following a
        #   <cb/> column break (table continuation headers)
        # - any row with a merged cell (cols attribute; typically month names)
        # - any row whose non-empty cells contain only red-highlighted text
        #   (e.g. month-name divider rows in early printed almanacs).
        # All other rows are body data. Cells are concatenated into the
        # row's text. Table rows are ATOMIC — no sentence-splitting within
        # a row (internal periods are usually decorative around numerals or
        # transcription placeholders like `[---]`).
        header_next = True  # first row is a header
        for child in elem:
            ctag = _tag(child)
            if ctag == "cb":
                header_next = True
                continue
            if ctag != "row":
                continue
            cells = [c for c in child if _tag(c) == "cell"]
            is_header = (
                header_next
                or any(c.get("cols") for c in cells)
                or any(c.get("role") == "label" for c in cells)
                or _row_is_all_red(cells, state)
            )
            block_type = "head" if is_header else "body"
            # Join cell text with whitespace so adjacent-cell content stays
            # word-separated (otherwise e.g. a tune-incipit cell concatenates
            # directly into a psalm-number cell: "frayv. psalm" instead of
            # "fray v. psalm" — Souterliedekens 1540 Registere der wijsen).
            cell_texts = [_post_process(_inline_text(c, state)) for c in cells]
            orig = " ".join(t for t in cell_texts if t).strip()
            if orig and _letter_count_inline(orig) >= 1:
                rich = rich_normalize(orig)
                rows.append(Row(
                    doc_id=doc_id,
                    block_type=block_type,
                    para_id=counter["para_id"],
                    sent_id=0,
                    is_para_final=True,
                    page_n=state.get("page_n"),
                    textstring_orig=orig,
                    textstring_rich=rich,
                    textstring_simple=simple_normalize(rich),
                ))
                counter["para_id"] += 1
            header_next = False
    elif tag in _SKIP_INLINE:
        pass
    else:
        for child in elem:
            rows.extend(_walk(child, doc_id, counter, state))
    return rows


def parse_tei(xml_path: str, doc_id: str) -> list[Row]:
    """Parse a TEI-P5 XML into sentence-level Rows.

    `<text>/<front>` is walked first (preface/dedication content sometimes lives
    here, e.g. crescentiis 1493), then `<text>/<body>`. `<back>` is skipped.
    `<pb>` elements in front update page_n so body rows carry correct pages.
    """
    tree = etree.parse(xml_path)
    root = tree.getroot()
    text_elem = _find(root, "text")
    if text_elem is None:
        raise ValueError(f"no <text> element in {xml_path}")
    body = _find(text_elem, "body")
    if body is None:
        raise ValueError(f"no <body> element in {xml_path}")
    counter = {"para_id": 0}
    state: dict = {"page_n": None, "page_seq": 0}
    rows: list[Row] = []
    front = _find(text_elem, "front")
    if front is not None:
        rows.extend(_walk(front, doc_id, counter, state))
    rows.extend(_walk(body, doc_id, counter, state))
    # If a document has no body rows but has item rows (e.g. a ledger or
    # list-only text where every entry is an <item>), the items are the
    # running content — relabel them as body so the default body-only
    # loader picks them up.
    block_types = {r.block_type for r in rows}
    if "body" not in block_types and "item" in block_types:
        for r in rows:
            if r.block_type == "item":
                r.block_type = "body"
    return rows
