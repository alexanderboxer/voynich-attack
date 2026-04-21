"""DTA (Deutsches Textarchiv) source helpers."""

from pathlib import Path
from urllib.request import urlopen

DTA_XML_URL = "https://www.deutschestextarchiv.de/book/download_xml/{doc_id}"


def download_xml(doc_id: str, dest: str | Path) -> Path:
    """Download a DTA document's TEI-P5 XML to `dest`."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(DTA_XML_URL.format(doc_id=doc_id)) as resp:
        dest.write_bytes(resp.read())
    return dest
