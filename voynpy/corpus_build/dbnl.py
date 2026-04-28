"""DBNL (Digitale Bibliotheek voor de Nederlandse Letteren) source helpers.

DBNL hosts diplomatic TEI Lite (TEI.2) transcriptions of Dutch texts. Each
text has a stable DBNL ID like `_ars002arsm01`. The XML is served from a
URL of the form `https://www.dbnl.org/nieuws/xml.php?id=<dbnl_id>`.

Note that DBNL XMLs use the older TEI.2 / TEI Lite DTD rather than TEI-P5;
the parser in `tei_p5.py` is namespace-flexible and handles both.
"""

from pathlib import Path
from urllib.request import urlopen

DBNL_XML_URL = "https://www.dbnl.org/nieuws/xml.php?id={dbnl_id}"


def download_xml(dbnl_id: str, dest: str | Path) -> Path:
    """Download a DBNL document's TEI Lite XML to `dest`."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(DBNL_XML_URL.format(dbnl_id=dbnl_id)) as resp:
        dest.write_bytes(resp.read())
    return dest
