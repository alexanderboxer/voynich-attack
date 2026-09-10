"""Report generators for VMS analysis.
"""

# ==============================================================================
# Imports
# ==============================================================================
import csv
from pathlib import Path
from datetime import date


# ==============================================================================
# Config
# ==============================================================================
_ROOT = Path(__file__).resolve().parent.parent
_VOYPARS = _ROOT / "sequences" / "voypars.csv"

# Tokens rendered in `code` by tkreport. Everything else is plain text; the
# target itself is code+bold.
KEY_TOKENS = frozenset({
    '8,a,m',
    'cc,o,x',
})

_BUCKET_TAIL = ("-1", "-2", "-3", "p1", "p2", "p3", "ABA", "-")


# ==============================================================================
# Auxiliary Functions
# ==============================================================================
def paragraphs(path=None):
    """[(site_id, [tokens]), ...] from voypars.csv, in manuscript order."""
    with Path(path or _VOYPARS).open() as f:
        return [(row["idx"],
                 [t.strip() for t in row["textstring"].split(";") if t.strip()])
                for row in csv.DictReader(f)]


def _window(toks, center, size=12, before=5):
    return [toks[i] if 0 <= i < len(toks) else "¶"
            for i in range(center - before, center - before + size)]


def _loc(pos, para_len, run_len, toks, follower):
    nxt = toks[pos + run_len] if pos + run_len < len(toks) else "¶"
    if follower is not None and nxt == follower:
        return f"->{follower}"
    if run_len >= 2:
        return f"x{run_len}"
    if para_len - pos <= 3:
        return f"-{para_len - pos}"
    if pos <= 2:
        return f"p{pos + 1}"
    left = toks[pos - 1] if pos > 0 else "¶"
    return "ABA" if left == nxt and left != "¶" else "-"


def _bucket_sort_key(label, order):
    if label.startswith("x"):
        return (len(order) - 1, -int(label[1:]))
    return (order.index(label) if label in order else 999, 0)


def _cell(tok, is_target, key):
    if tok == "¶":
        return "¶"
    if is_target:
        return f"**`{tok}`**"
    return f"`{tok}`" if tok in key else tok


# ==============================================================================
# Function: tkreport
# ==============================================================================
def tkreport(token, target_filepath=None, *, follower=None, key=None,
             paras=None):
    """Write every occurrence of `token` with 12-token context.

    One row per RUN of consecutive `token`; a doubling collapses to a single
    row flagged `xN`. The run's first token sits at t6 and `¶` pads slots
    outside the paragraph. Rows are grouped: `->follower` if given, then
    distance from the paragraph end (-1, -2, -3), then paragraph-initial
    (p1, p2, p3), then ABA (same token both sides), then runs, then interior.

    target_filepath  where to write; defaults to
                     `<token minus commas>.md` in the current
                     directory, e.g. `8,a,m` -> `8am.md`
    follower  token that, when it follows, sorts those rows to the top
    key       tokens to render in `code` (default KEY_TOKENS)
    paras     pre-loaded paragraphs(), to avoid re-reading the CSV in a loop

    Prints where it wrote. Returns nothing, so the path does not echo in
    the REPL. If the target already exists it asks before overwriting, and
    declines when there is no terminal to ask on.
    """
    out = (Path(target_filepath) if target_filepath is not None
           else Path.cwd() / f"{token.replace(',', '')}.md")
    if out.exists():
        try:
            reply = input(f"{out} already exists\nOverwrite (y/n)? ")
        except EOFError:          # non-interactive: never clobber silently
            reply = "n"
        if reply.strip().lower() not in ("y", "yes"):
            return
    paras = paragraphs() if paras is None else paras
    key = (KEY_TOKENS if key is None else frozenset(key)) - {token}
    order = ((f"->{follower}",) if follower is not None else ()) + _BUCKET_TAIL

    runs = []
    for site, toks in paras:
        i, n = 0, len(toks)
        while i < n:
            if toks[i] == token:
                j = i
                while j < n and toks[j] == token:
                    j += 1
                runs.append((site, i, j - i, n, toks))
                i = j
            else:
                i += 1
    if not runs:
        print(f"Token {token} does not appear in the transcription")
        return

    rows = [{"site": site, "pos": pos, "para_len": para_len, "run_len": run_len,
             "loc": _loc(pos, para_len, run_len, toks, follower),
             "window": _window(toks, pos)}
            for site, pos, run_len, para_len, toks in runs]
    rows.sort(key=lambda r: (_bucket_sort_key(r["loc"], order),
                             r["site"], r["pos"]))


    L = [f"# Token Report: `{token}`\n",
         "| # | site | pos | loc | t1 | t2 | t3 | t4 | t5 | **t6** | t7 | "
         "t8 | t9 | t10 | t11 | t12 |",
         "|--:|---|--:|:-:|" + "---|" * 12]
    for n, r in enumerate(rows, 1):
        run_slots = set(range(5, 5 + r["run_len"]))
        cells = " | ".join(_cell(t, i in run_slots, key)
                           for i, t in enumerate(r["window"]))
        L.append(f"| {n} | `{r['site']}` | {r['pos']}/{r['para_len']} | "
                 f"{r['loc']} | {cells} |")

    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote file to {out}")
