"""DTA (Deutsches Textarchiv) source helpers."""

from pathlib import Path
from urllib.request import Request, urlopen

DTA_XML_URL = "https://www.deutschestextarchiv.de/book/download_xml/{doc_id}"
# DTA serves a JS cookie-verification stub to clients that don't carry the
# `verified=1` cookie. We set it on every request so urlopen receives the
# real TEI XML rather than the bootstrap page. Works for both slug-style
# doc_ids (`luther_thesen_1557`) and numeric IDs (`527796`).
DTA_HEADERS = {"Cookie": "verified=1"}


def download_xml(doc_id: str, dest: str | Path) -> Path:
    """Download a DTA document's TEI-P5 XML to `dest`."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(DTA_XML_URL.format(doc_id=doc_id), headers=DTA_HEADERS)
    with urlopen(req) as resp:
        dest.write_bytes(resp.read())
    return dest
