"""Per-text row refinement helpers, used by build.py after parse_tei.

These functions implement common "ad-hoc human decisions" that fix specific
text idiosyncrasies (recipe-title heads in cookbooks, citation fragments in
religious texts, verse-line wraps in poetry, etc.) — patterns the general
parser can't infer without context.
"""
from __future__ import annotations

from .schema import Row


def merge_or_demote_short_body(rows: list[Row], max_words: int = 2) -> list[Row]:
    """Eliminate fragment-length body rows by either merging or demoting.

    For each body row with `<= max_words` tokens in its textstring_simple:
    - If the preceding body row's textstring_orig does NOT end with `.!?`,
      the fragment is treated as a continuation (verse-line wrap, sentence
      tail) and merged into the prev row's text columns.
    - Otherwise the fragment is treated as a standalone artifact
      (signature initial, biblical-citation residue, stray label) and
      demoted to `item` so the default body-only loader excludes it.

    Returns a new list (merged rows are dropped from the output).
    """
    out: list[Row] = []
    for r in rows:
        if r.block_type != "body" or len(r.textstring_simple.split()) > max_words:
            out.append(r)
            continue
        if out and out[-1].block_type == "body":
            prev = out[-1]
            if prev.textstring_orig.rstrip().endswith((".", "!", "?")):
                r.block_type = "item"
                out.append(r)
            else:
                prev.textstring_simple = prev.textstring_simple + " " + r.textstring_simple
                prev.textstring_rich = prev.textstring_rich + " " + r.textstring_rich
                prev.textstring_orig = prev.textstring_orig + " " + r.textstring_orig
                if r.is_para_final:
                    prev.is_para_final = True
        else:
            r.block_type = "item"
            out.append(r)
    return out
