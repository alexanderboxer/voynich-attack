"""EEBO-TCP source helpers."""

from pathlib import Path
from urllib.request import urlopen

# Each TCP ID has its own GitHub repo under the textcreationpartnership org;
# the Phase I (CC0) XML lives at the root of master.
TCP_XML_URL = (
    "https://raw.githubusercontent.com/textcreationpartnership/{tcp_id}/master/{tcp_id}.xml"
)


def download_xml(tcp_id: str, dest: str | Path) -> Path:
    """Download an EEBO-TCP document's TEI-P5 XML to `dest`."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(TCP_XML_URL.format(tcp_id=tcp_id)) as resp:
        dest.write_bytes(resp.read())
    return dest
