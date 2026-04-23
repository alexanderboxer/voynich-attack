"""cc vs c^c: are they functionally different?

Compare counts and positional behavior of the cc-variants against the
c^c-variants, both as standalone tokens and as prefixes on c,M,c,9 / 8,a,m
containers. No 'cc-family' lumping — each form is counted separately.
"""

from __future__ import annotations

from collections import Counter

from voynpy.corpora import vms


def _token_cols(df):
    return [c for c in df.columns if c.startswith("t") and c[1:].isdigit()]


def tokens_of(rt):
    df = rt.df
    cols = _token_cols(df)
    for _, row in df.iterrows():
        for c in cols:
            t = row[c]
            if isinstance(t, str) and t != "$":
                yield t


def token_counts(rt):
    cnt = Counter()
    for t in tokens_of(rt):
        cnt[t] += 1
    return cnt


def prefix_counts_before(rt, target):
    """For all VMS tokens that end with `target` as a comma-subsequence,
    tally the prefix (glyphs before target within the same token). <NONE>
    = standalone target."""
    target_glyphs = target.split(",")
    pc = Counter()
    for t in tokens_of(rt):
        glyphs = t.split(",")
        if glyphs == target_glyphs:
            pc["<NONE>"] += 1
            continue
        m = len(target_glyphs)
        if len(glyphs) >= m and glyphs[-m:] == target_glyphs:
            prefix = ",".join(glyphs[: -m])
            pc[prefix] += 1
    return pc


# ---- Standalone token counts
cnt = token_counts(vms)
print("=" * 62)
print("STANDALONE token counts (whitespace-separated VMS tokens)")
print("=" * 62)
variants = [
    ("cc",        "c^c"),
    ("cc,c",      "c^c,c"),
    ("cc,o",      "c^c,o"),
    ("cc,9",      "c^c,9"),
    ("cc,c,9",    "c^c,c,9"),
    ("cc,c,o",    "c^c,c,o"),
    ("cc,o,9",    "c^c,o,9"),
    ("cc,o,x",    "c^c,o,x"),
    ("cc,o,Z",    "c^c,o,Z"),
]
print(f"  {'cc-form':>14} | {'count':>6}   {'c^c-form':>14} | {'count':>6}   ratio")
for cc_form, ccprime_form in variants:
    n_cc = cnt.get(cc_form, 0)
    n_ccp = cnt.get(ccprime_form, 0)
    r = f"{n_cc/n_ccp:.1f}x" if n_ccp else ("— " if n_cc == 0 else "∞")
    print(f"  {cc_form!r:>14} | {n_cc:>6}   {ccprime_form!r:>14} | {n_ccp:>6}   {r:>5}")


# ---- Prefix-on-target analysis
for target in ["c,M,c,9", "8,a,m"]:
    print()
    print("=" * 62)
    print(f"PREFIX counts on tokens containing {target!r}")
    print("=" * 62)
    pc = prefix_counts_before(vms, target)
    total = sum(pc.values())
    print(f"  total containers: {total}")
    cc_prefixes = {p: n for p, n in pc.items() if p.split(",")[0] == "cc" if p != "<NONE>"}
    ccp_prefixes = {p: n for p, n in pc.items() if p.split(",")[0] == "c^c" if p != "<NONE>"}
    cc_total = sum(cc_prefixes.values())
    ccp_total = sum(ccp_prefixes.values())
    print(f"  cc-variants total:  {cc_total:>5}  ({100*cc_total/total:.1f}%)")
    print(f"  c^c-variants total: {ccp_total:>5}  ({100*ccp_total/total:.1f}%)")
    print(f"  ratio cc : c^c  =  {cc_total/ccp_total:.2f}x" if ccp_total else "")
    # break out top of each
    print("  cc-variant prefixes (top 8):")
    for p, n in sorted(cc_prefixes.items(), key=lambda x: -x[1])[:8]:
        print(f"     {p!r:>12}: {n:4d}")
    print("  c^c-variant prefixes (top 8):")
    for p, n in sorted(ccp_prefixes.items(), key=lambda x: -x[1])[:8]:
        print(f"     {p!r:>12}: {n:4d}")
