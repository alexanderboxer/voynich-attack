"""Enrich tls-eebo-pre1550.csv with TCP ID and Status columns.

Join on MARC ID (tls-eebo) = EEBO (TCP.csv). Status='Free' means the text
is in the public domain and downloadable as TEI-P5 XML from
github.com/textcreationpartnership/<TCPID>/<TCPID>.xml.

Output: tls-eebo-pre1550-tcp.csv with two new leading columns (TCP ID,
TCP Status) followed by the original column order.
"""

import csv
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "tls-eebo-pre1550.csv"
TCP = HERE / "TCP.csv"
OUT = HERE / "tls-eebo-pre1550-tcp.csv"


def main() -> None:
    # MARC ID -> (TCP ID, Status)
    marc_to_tcp: dict[str, tuple[str, str]] = {}
    with open(TCP, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            eebo = row["EEBO"].strip()
            if eebo:
                marc_to_tcp[eebo] = (row["TCP"].strip(), row["Status"].strip())

    with open(SRC, newline="", encoding="utf-8") as f_in:
        r = csv.DictReader(f_in)
        src_fields = r.fieldnames
        rows = list(r)

    out_fields = ["TCP ID", "TCP Status"] + src_fields
    have_tcp = 0
    free = 0
    with open(OUT, "w", newline="", encoding="utf-8") as f_out:
        w = csv.DictWriter(f_out, fieldnames=out_fields)
        w.writeheader()
        for row in rows:
            tcp_id, status = marc_to_tcp.get(row["MARC ID"].strip(), ("", ""))
            out = {"TCP ID": tcp_id, "TCP Status": status, **row}
            w.writerow(out)
            if tcp_id:
                have_tcp += 1
                if status == "Free":
                    free += 1
    print(f"input rows:    {len(rows)}")
    print(f"with TCP ID:   {have_tcp}")
    print(f"  Free:        {free}")
    print(f"  other/empty: {have_tcp - free}")
    print(f"wrote          {OUT}")


if __name__ == "__main__":
    main()
