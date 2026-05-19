"""Build the sentence-level CSV for the Luther Bibel 1545 (Zeno.org).

Source: <http://www.zeno.org/Literatur/M/Luther,+Martin/Luther-Bibel+1545>
License: Gemeinfrei (public domain) per Zeno.

Structure:
- ./html/      — cached HTML pages (committed), mirrors Zeno's URL tree.
- ./manifest.txt — list of leaf URLs (committed; alphabetically sorted).
- ./luther_bible_1545.csv — output (committed).

Run from this directory:
    python build.py        # parse local HTML → CSV
    python build.py fetch  # fetch any missing HTML, then parse
"""
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from voynpy.corpus_build.schema import Row, write_csv, split_sentences, split_sentences_with_offsets
from voynpy.corpus_build.normalize import rich_normalize, simple_normalize


PAGE_ANCHOR_RE = re.compile(r'\[([A-Za-z0-9]+)\]')


HERE = Path(__file__).parent
HTML_ROOT = HERE / 'html'
MANIFEST_PATH = HERE / 'manifest.txt'
CSV_PATH = HERE / 'luther_bible_1545.csv'

DOC_ID = 'luther_bible_1545'
BASE_URL = 'http://www.zeno.org'
URL_PREFIX = '/Literatur/M/Luther,+Martin/Luther-Bibel+1545/'

# ============================================================
# Fetching
# ============================================================

def url_to_local(url: str) -> Path:
    """Map a Zeno URL to its local HTML file path."""
    rel = url[len(URL_PREFIX):] if url.startswith(URL_PREFIX) else url.lstrip('/')
    return HTML_ROOT / (rel + '.html')

def fetch_if_missing(url: str, sleep_seconds: float = 1.0) -> Path:
    """Fetch a URL if local file doesn't exist; return the local path."""
    local = url_to_local(url)
    if local.exists() and local.stat().st_size > 1000:
        return local
    local.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(BASE_URL + url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        local.write_bytes(resp.read())
    time.sleep(sleep_seconds)
    return local

# ============================================================
# Parsing
# ============================================================

def parse_zeno_page(html_bytes: bytes, book_name: str, chapter_num: int | None, block_type: str):
    """Parse one Zeno HTML page into a list of row dicts.

    For Bible chapter pages (with <sup>N</sup> verse markers):
      - One row per verse. sent_id = verse number, para_id = chapter number,
        page_n = book name.
      - Strips footnote anchors, cross-references (⇒ ...), woodcut descriptions.
    For preface pages (no verse markers):
      - One row per period-terminated sentence. sent_id sequential within
        the paragraph; para_id sequential within the page.
      - [IVa]-style page anchors are extracted to page_n; carry forward across
        paragraphs until next anchor.
    """
    html = html_bytes.decode('iso-8859-1')
    m = re.search(r'<div[^>]*class="zenoCOMain"[^>]*>', html)
    if not m:
        return []
    start = m.end()
    end_search = html.find('<div class="zenoCOFooter"', start)
    inner = html[start:end_search] if end_search >= 0 else html[start:]
    # Strip woodcut-description div blocks
    inner = re.sub(
        r'<div class="zenoIMBreak"[^>]*>.*?</div>\s*</div>\s*</div>',
        '', inner, flags=re.DOTALL
    )
    # Head-classified pages (Titelblatt, Privileg, TOCs): capture <h*>, <li>,
    # AND <p> content uniformly as head rows. Skip Bible-chapter parsing
    # path which doesn't apply.
    if block_type == 'head':
        items = []
        for m_block in re.finditer(
            r'<(h[1-6]|li|p)(\s+[^>]*)?>(.*?)</\1>', inner, re.DOTALL
        ):
            text = _strip_html_and_normalize_ws(m_block.group(3))
            if text:
                items.append(text)
        if not items:
            return []
        return [{
            'sent_id': i + 1,
            'para_id': 1,
            'page_n': book_name or '',
            'block_type': block_type,
            'textstring_orig': line,
        } for i, line in enumerate(items)]
    # Accept body <p>: either no class or class="zenoPLm4n0".
    # Skip zenoPLm0n4 (footnote/crossref content).
    p_blocks = []
    for m_p in re.finditer(r'<p(\s+class="([^"]*)")?[^>]*>(.*?)</p>', inner, re.DOTALL):
        cls = m_p.group(2)
        if cls is None or cls == 'zenoPLm4n0':
            p_blocks.append(m_p.group(3))
    if not p_blocks:
        # Fallback for pages that use only <h2>/<h3>/<h4> headings as content,
        # e.g. the Titelblätter title page where each line is a centered heading.
        # Emit each non-empty heading as its own row (head block).
        heading_lines = []
        for m_h in re.finditer(r'<h[1-6][^>]*>(.*?)</h[1-6]>', inner, re.DOTALL):
            text = _strip_html_and_normalize_ws(m_h.group(1))
            if text:
                heading_lines.append(text)
        if not heading_lines:
            return []
        return [{
            'sent_id': i + 1,
            'para_id': 1,
            'page_n': book_name or '',
            'block_type': block_type,
            'textstring_orig': line,
        } for i, line in enumerate(heading_lines)]

    def clean_paragraph_html(text: str) -> str:
        # Strip footnote-marker anchors
        text = re.sub(
            r'<a name="N\d+"></a><a href="[^"]*#F\d+"[^>]*><sup>[^<]*</sup></a>',
            '', text
        )
        # Strip ⇒ cross-references
        text = re.sub(
            r'<a href="[^"]*" class="zenoTXLinkInt">\s*&#x21D2;\s*</a>[^<;]*;?\s*',
            '', text
        )
        return text

    has_verse_anchors = any('<a name="1545_' in p for p in p_blocks)
    has_bare_sup = any(re.search(r'<sup>\s*\d+\s*</sup>', clean_paragraph_html(p)) for p in p_blocks)

    rows = []
    if has_verse_anchors or has_bare_sup:
        # Bible chapter mode
        full_body = '\n'.join(clean_paragraph_html(p) for p in p_blocks)
        parts = re.split(r'<sup>\s*(\d+)\s*</sup>', full_body)
        for i in range(1, len(parts), 2):
            vnum = int(parts[i])
            body = parts[i+1] if i+1 < len(parts) else ''
            text = _strip_html_and_normalize_ws(body)
            # Strip any leaked [180b]-style page anchors (Apokryphe + some chapter pages)
            text = PAGE_ANCHOR_RE.sub('', text).strip()
            text = re.sub(r'\s+', ' ', text).strip()
            # Skip empty/letterless verses (a few verse anchors have only
            # a virgule between them with no actual content)
            if text and any(c.isalpha() for c in text):
                rows.append({
                    'sent_id': vnum,
                    'para_id': chapter_num or 1,
                    'page_n': book_name or '',
                    'block_type': block_type,
                    'textstring_orig': text,
                })
    else:
        # Preface / non-chapter mode — paragraph + sentence-aware splitting.
        # Page anchors ([IVa]) are NOT sentence boundaries. Procedure:
        #   1. Strip anchors from each paragraph but record their offsets
        #      in the anchor-free text.
        #   2. Sentence-split the anchor-free text via voynpy's split_sentences
        #      (Roman-numeral- and abbreviation-aware).
        #   3. For each sentence, assign page_n based on the most recent
        #      anchor at or before that sentence's start offset.
        # Page_n is "<book_name> [<anchor>]" when a folio anchor is active,
        # else the bare book_name. Preface identity is always preserved.
        base_book = book_name or ''
        current_page = base_book
        for para_idx, body in enumerate(p_blocks, 1):
            body = clean_paragraph_html(body)
            clean = _strip_html_and_normalize_ws(body)
            # Find anchor positions in clean text, then build anchor-stripped
            # text remembering each anchor's offset in the stripped string.
            anchor_offsets = []  # list of (offset_in_stripped, page_label)
            stripped_parts = []
            cum = 0
            prev_end = 0
            for m_a in PAGE_ANCHOR_RE.finditer(clean):
                s, e = m_a.start(), m_a.end()
                seg = clean[prev_end:s]
                stripped_parts.append(seg)
                cum += len(seg)
                page_label = f'{base_book} [{m_a.group(1)}]' if base_book else m_a.group(1)
                anchor_offsets.append((cum, page_label))
                prev_end = e
            stripped_parts.append(clean[prev_end:])
            stripped = ''.join(stripped_parts)
            # Normalize whitespace from anchor-stripping seams
            stripped = re.sub(r'\s+', ' ', stripped).strip()

            def page_at(offset, default):
                page = default
                for anchor_off, anchor_page in anchor_offsets:
                    if offset >= anchor_off:
                        page = anchor_page
                    else:
                        break
                return page

            sent_idx = 1
            for offset, sentence in split_sentences_with_offsets(stripped):
                s = sentence.strip()
                if s:
                    rows.append({
                        'sent_id': sent_idx,
                        'para_id': para_idx,
                        'page_n': page_at(offset, current_page),
                        'block_type': block_type,
                        'textstring_orig': s,
                    })
                    sent_idx += 1
            # Carry forward latest anchor to next paragraph
            if anchor_offsets:
                current_page = anchor_offsets[-1][1]
    return rows


def _strip_html_and_normalize_ws(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&#x21D2;', '').replace('&amp;', '&').replace('&nbsp;', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ============================================================
# Canonical Bible book ordering
# ============================================================

# Canonical Bible book order — uses the book-hub URL segment names from Zeno.
# These match the segment between the section name and the chapter-leaf name.
_OT_CANONICAL = [
    'Das erste Buch Mose (Genesis)',
    'Das zweite Buch Mose (Exodus)',
    'Das dritte Buch Mose (Leviticus)',
    'Das vierte Buch Mose (Numeri)',
    'Das fünfte Buch Mose (Deuteronomium)',
    'Das Buch Josua',
    'Das Buch der Richter',
    'Das Buch Ruth',
    'Das erste Buch Samuel',
    'Das zweite Buch Samuel',
    'Das erste Buch der Könige',
    'Das zweite Buch der Könige',
    'Das erste Buch der Chronik',
    'Das zweite Buch der Chronik',
    'Das Buch Esra',
    'Das Buch Nehemia',
    'Das Buch Esther',
    'Das Buch Hiob',
    'Der Psalter',
    'Die Sprüche Salomonis',
    'Der Prediger Salomo',
    'Das Hohelied Salomonis',
    'Der Prophet Jesaia',
    'Der Prophet Jeremia',
    'Die Klaglieder Jeremiä',
    'Der Prophet Hesekiel',
    'Der Prophet Daniel',
    'Der Prophet Hosea',
    'Der Prophet Joel',
    'Der Prophet Amos',
    'Der Prophet Obadja',
    'Der Prophet Jona',
    'Der Prophet Micha',
    'Der Prophet Nahum',
    'Der Prophet Habakuk',
    'Der Prophet Zephanja',
    'Der Prophet Haggai',
    'Der Prophet Sacharja',
    'Der Prophet Maleachi',
]

_APOK_CANONICAL = [
    'Das Buch Judith',
    'Die Weisheit Salomonis',
    'Das Buch Tobias',
    'Das Buch Jesus Sirach',
    'Der Prophet Baruch',
    'Das erste Buch der Makkabäer',
    'Das zweite Buch der Makkabäer',
    'Zusätze zu den Büchern Esther und Daniel',
]

_NT_CANONICAL = [
    'Das Matthäusevangelium',
    'Das Markusevangelium',
    'Das Lukasevangelium',
    'Das Johannesevangelium',
    'Die Apostelgeschichte',
    'Der Brief des Paulus an die Römer',
    'Der erste Brief des Paulus an die Korinther',
    'Der zweite Brief des Paulus an die Korinther',
    'Der Brief des Paulus an die Galater',
    'Der Brief des Paulus an die Epheser',
    'Der Brief des Paulus an die Philipper',
    'Der Brief des Paulus an die Kolosser',
    'Der erste Brief des Paulus an die Thessalonicher',
    'Der zweite Brief des Paulus an die Thessalonicher',
    'Der erste Brief des Paulus an Timotheus',
    'Der zweite Brief des Paulus an Timotheus',
    'Der Brief des Paulus an Titus',
    'Der Brief des Paulus an Philemon',
    'Der Brief an die Hebräer',
    'Der Brief des Jakobus',
    'Der erste Brief des Petrus',
    'Der zweite Brief des Petrus',
    'Der erste Brief des Johannes',
    'Der zweite Brief des Johannes',
    'Der dritte Brief des Johannes',
    'Der Brief des Judas',
    'Die Offenbarung des Johannes',
]

# Maps each book-hub name to (section_index, book_index_in_section)
_BOOK_SORT_KEY = {}
for i, name in enumerate(_OT_CANONICAL):     _BOOK_SORT_KEY[name] = (1, i)
for i, name in enumerate(_APOK_CANONICAL):   _BOOK_SORT_KEY[name] = (2, i)
for i, name in enumerate(_NT_CANONICAL):     _BOOK_SORT_KEY[name] = (3, i)


def _find_book_in_preface_title(text: str):
    """For a preface-style leaf title like 'Luthers Vorrede auf das Buch Hiob',
    find the canonical-book sort key for the book it's actually ABOUT
    (independent of where Zeno filed the URL).

    Returns (section_idx, book_idx) if found, else None. Used to re-route
    mis-filed prefaces (e.g., Hiob's Vorrede that Zeno places under Esther).
    """
    text_l = text.lower()
    matches = []
    for book_name, (sec_idx, b_idx) in _BOOK_SORT_KEY.items():
        if book_name.lower() in text_l:
            matches.append((len(book_name), sec_idx, b_idx))
    if not matches:
        return None
    # Longest book-name match wins (e.g. "Das Buch Esther und Daniel" prefers
    # Esther vs Daniel ambiguity by picking the longest substring)
    matches.sort(reverse=True)
    return (matches[0][1], matches[0][2])


def canonical_sort_key(url: str):
    """Compute a canonical sort key for a leaf URL.

    Key shape: (section_idx, book_idx, within_book_idx, tie_breaker)
      section_idx: 0=Titelblatt, 1=OT, 2=Apok, 3=NT, 4=Privileg, 5=other
      book_idx: position in canonical book list (-1 for section-level
                prefaces / meta pages, which sort first within the section)
      within_book_idx: 0 for preface/non-chapter (sorts first within book),
                       chapter_num for chapter pages
    """
    rel = url[len(URL_PREFIX):] if url.startswith(URL_PREFIX) else url.lstrip('/')
    rel = urllib.parse.unquote_plus(rel)
    segments = rel.split('/')
    top = segments[0] if segments else ''

    if top == '[Titelblätter]':
        return (0, -1, 0, rel)
    if top == 'Apokryphe Schriften des Alten Testaments':
        section_idx = 2
    elif top == 'Das Alte Testament':
        section_idx = 1
    elif top == 'Das Neue Testament':
        section_idx = 3
    elif top == 'Privileg und Warnung':
        return (4, -1, 0, rel)
    else:
        return (5, -1, 0, rel)

    if len(segments) == 2:
        leaf = segments[1]
        # 2-segment URL: could be (a) a single-page book (its leaf is a
        # canonical book name, e.g. 2./3. Johannes which have no chapter
        # subpages), (b) a Vorrede about a specific book, or (c) a section-
        # level preface/meta page.
        if leaf in _BOOK_SORT_KEY:
            sec_idx, b_idx = _BOOK_SORT_KEY[leaf]
            # within=1 sorts after any Vorreden (within=0) about this book
            return (sec_idx, b_idx, 1, leaf)
        if 'Vorrede' in leaf:
            content_book = _find_book_in_preface_title(leaf)
            if content_book is not None:
                sec, b_idx = content_book
                return (sec, b_idx, 0, leaf)
        # Otherwise: section-level meta page (sorts first within section)
        return (section_idx, -1, 0, leaf)

    # 3+ segment URL: nested under a book_hub.
    book_hub = segments[1]
    leaf = segments[-1]
    book_key = _BOOK_SORT_KEY.get(book_hub)
    if book_key is None:
        # Unrecognized book_hub (e.g. NT's "[Vorbemerkungen]" wrapper).
        # Treat as section-level meta — sorts first in section, before any books.
        if 'Vorrede' in leaf:
            content_book = _find_book_in_preface_title(leaf)
            if content_book is not None:
                sec, content_b_idx = content_book
                return (sec, content_b_idx, 0, leaf)
        return (section_idx, -1, 0, leaf)
    book_idx = book_key[1]
    # Numbered chapter page (leaf ends with " N"): within = chapter number
    m_ch = re.search(r'\s+(\d+)$', leaf)
    if m_ch:
        return (section_idx, book_idx, int(m_ch.group(1)), leaf)
    # Vorrede page: re-route to its content-book slot if title differs from
    # the URL filing; otherwise stays with URL-filed book. within=0.
    if 'Vorrede' in leaf:
        content_book = _find_book_in_preface_title(leaf)
        if content_book is not None:
            sec, content_b_idx = content_book
            return (sec, content_b_idx, 0, leaf)
        return (section_idx, book_idx, 0, leaf)
    # Non-chapter, non-Vorrede leaf under a book_hub: single-page body
    # content (e.g. Philemon's "Die Epistel S. Pauli: An Philemon" leaf).
    # within=1 sorts after Vorreden, in the slot any chapter 1 would occupy.
    return (section_idx, book_idx, 1, leaf)


# ============================================================
# Manifest + URL → (book, chapter, block_type) mapping
# ============================================================

def url_to_metadata(url: str):
    """Map a leaf URL to (book_name, chapter_num, block_type) for parser.

    Examples:
      .../Das+Alte+Testament/Das+erste+Buch+Mose+(Genesis)/Genesis+1
        → book='Genesis', chapter=1, type='body'
      .../Das+Alte+Testament/Luthers+Vorrede+auf+das+Alte+Testament
        → book='Vorrede-AT', chapter=None, type='body' (preface = body)
      .../%5BTitelblätter%5D
        → book='Titelblatt', chapter=None, type='head'
      .../Privileg+und+Warnung/...
        → book='Privileg', chapter=None, type='head'
    """
    rel = url[len(URL_PREFIX):] if url.startswith(URL_PREFIX) else url.lstrip('/')
    # unquote_plus converts both %XX and `+`→space (Zeno uses `+` as space)
    rel = urllib.parse.unquote_plus(rel)
    segments = rel.split('/')
    top = segments[0] if segments else ''
    # ONLY Titelblatt and Privileg are 'head' (formal/ceremonial front/back matter).
    # Everything else under OT, NT, Apokryphe — including single-chapter books and
    # prefaces — is biblical/Lutheran prose, so 'body'.
    if top == '[Titelblätter]':
        return ('Titelblatt', None, 'head')
    if top == 'Privileg und Warnung':
        return ('Privileg', None, 'head')
    last_seg = segments[-1]
    # Bible chapter: last segment ends with " N" where N is a number
    m_ch = re.search(r'(.+)\s+(\d+)$', last_seg)
    if m_ch:
        return (m_ch.group(1), int(m_ch.group(2)), 'body')
    # Table-of-contents pages — "Die Bücher des Alten/Newen Testaments" etc.
    if last_seg.startswith('Die Bücher'):
        return (last_seg, None, 'head')
    # Single-chapter book or preface: last segment is the book/preface name itself.
    return (last_seg, None, 'body')


# ============================================================
# Main pipeline
# ============================================================

def load_manifest():
    if MANIFEST_PATH.exists():
        return MANIFEST_PATH.read_text().strip().split('\n')
    raise FileNotFoundError(
        f"Manifest not found at {MANIFEST_PATH}. "
        f"Re-run the recon step or restore manifest.txt from git."
    )


def main():
    fetch_mode = '--fetch' in sys.argv or 'fetch' in sys.argv

    manifest = load_manifest()
    print(f"  loaded {len(manifest)} leaf URLs from manifest")
    # Canonical Bible-reading-order sort: Titelblatt → OT → Apok → NT → Privileg,
    # with each book's prefaces before its chapters, in canonical book order.
    manifest = sorted(manifest, key=canonical_sort_key)

    if fetch_mode:
        print(f"  fetch mode: will download any missing HTML")
        missing = sum(1 for url in manifest if not url_to_local(url).exists())
        print(f"  {missing} HTML files missing")
        for i, url in enumerate(manifest, 1):
            try:
                fetch_if_missing(url)
                if i % 50 == 0:
                    print(f"  [{i}/{len(manifest)}] fetched")
            except Exception as e:
                print(f"  [{i}/{len(manifest)}] FAILED: {url} ({e})")

    # Parse all pages
    all_rows = []
    skipped = 0
    for url in manifest:
        local = url_to_local(url)
        if not local.exists():
            print(f"  SKIP (no HTML): {url}")
            skipped += 1
            continue
        book, chapter, btype = url_to_metadata(url)
        page_rows = parse_zeno_page(local.read_bytes(), book, chapter, btype)
        all_rows.extend(page_rows)

    print(f"  parsed {len(all_rows)} rows from {len(manifest) - skipped} pages ({skipped} skipped)")

    # Flag is_para_final: True for last row of each (para_id, page_n, block_type) triple
    # Build CSV rows
    rich_rows = []
    n = len(all_rows)
    for idx, r in enumerate(all_rows):
        is_final = (idx == n - 1) or (
            all_rows[idx+1]['para_id'] != r['para_id']
            or all_rows[idx+1].get('page_n') != r.get('page_n')
        )
        orig = r['textstring_orig']
        rich = rich_normalize(orig)
        simple = simple_normalize(rich)
        rich_rows.append(Row(
            doc_id=DOC_ID,
            block_type=r['block_type'],
            para_id=r['para_id'],
            sent_id=r['sent_id'],
            is_para_final=is_final,
            page_n=r.get('page_n') or None,
            textstring_orig=orig,
            textstring_rich=rich,
            textstring_simple=simple,
        ))

    write_csv(rich_rows, str(CSV_PATH))
    print(f"  wrote {len(rich_rows)} rows -> {CSV_PATH}")

    # Block-type breakdown
    from collections import Counter
    bt = Counter(r.block_type for r in rich_rows)
    print(f"  by block_type: {dict(bt)}")


if __name__ == '__main__':
    main()
