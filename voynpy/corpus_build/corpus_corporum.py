"""Corpus Corporum (UZH, mlat.uzh.ch) source helpers.

Corpus Corporum aggregates ~226M words of Latin across 30 sub-corpora.
Texts are addressed by numeric `cc_idno` (e.g. 12134 for Cusanus's
*Apologia doctae ignorantiae*); the download endpoint returns a
standard TEI-P5 XML file.

License: Corpus Corporum is free for non-commercial use; per-text
licensing may vary by upstream provider (see each TEI header).
"""

from pathlib import Path
from urllib.request import urlopen

CC_XML_URL = "https://mlat.uzh.ch/php_modules/download.php?type=file-xml&idno={cc_idno}"


def download_xml(cc_idno: str | int, dest: str | Path) -> Path:
    """Download a Corpus Corporum text's TEI-P5 XML to `dest`."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(CC_XML_URL.format(cc_idno=cc_idno)) as resp:
        dest.write_bytes(resp.read())
    return dest
