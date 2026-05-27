"""Demo of PseudoVmsEncoder. Run with:

    python -m voynpy.pseudo_vms.demo

Walks through the main API: encode, decode, save/load, tune,
custom alphabet, corpus encoding.
"""
import random
import tempfile
from pathlib import Path

from voynpy.pseudo_vms import PseudoVmsEncoder


def section(label: str) -> None:
    print(f"\n{'=' * 6} {label} {'=' * (60 - len(label))}")


def main() -> None:
    # ─── Basic construction ──────────────────────────────────────────

    section("1. Construct an encoder with defaults")
    enc = PseudoVmsEncoder()
    print(enc)
    print(f"  Tokens generated: {sum(len(v) for v in enc._table.values())}")
    print(f"  Per-symbol range: "
          f"{min(len(v) for v in enc._table.values())} to "
          f"{max(len(v) for v in enc._table.values())}")

    # ─── Encode + decode ─────────────────────────────────────────────

    section("2. Encode a string and decode it back")
    sample = "The quick brown fox jumps over the lazy dog"
    cipher = enc.encode(sample, rng=random.Random(1))
    print(f"  input:   {sample!r}")
    print(f"  encoded: {cipher}")
    print(f"  decoded: {enc.decode_text(cipher)!r}")

    # ─── Inspect token table for a symbol ─────────────────────────────

    section("3. Inspect the cipher tokens for a symbol")
    print(f"  Top 5 tokens for 'e' (by weight):")
    for tok, w in sorted(enc.tokens_for('e'), key=lambda x: -x[1])[:5]:
        print(f"    {tok:<8}  weight={w:.4f}")

    # ─── Save and reload ─────────────────────────────────────────────

    section("4. Save the cipher table and reload it")
    with tempfile.TemporaryDirectory() as td:
        table_path = Path(td) / 'cipher_table.csv'
        enc.save(table_path)
        print(f"  Saved table to {table_path.name} ({table_path.stat().st_size:,} bytes)")
        reloaded = PseudoVmsEncoder.load(table_path)
        c1 = enc.encode(sample, rng=random.Random(99))
        c2 = reloaded.encode(sample, rng=random.Random(99))
        print(f"  Roundtrip identical: {c1 == c2}")

    # ─── Tune doubling rate ──────────────────────────────────────────

    section("5. Tune the doubling rate to a target")
    enc2 = PseudoVmsEncoder(doubling_strength=0.50)
    print(f"  Before: doubling_strength={enc2.doubling_strength}")
    pangram = ("the quick brown fox jumps over the lazy dog "
               "she sells seashells by the seashore "
               "peter piper picked a peck of pickled peppers") * 50
    new_p = enc2.tune_to_vms(target_doubling_rate=0.0092, sample_text=pangram)
    print(f"  After:  doubling_strength={new_p:.4f}")

    # ─── Custom alphabet ─────────────────────────────────────────────

    section("6. Encode with a custom alphabet (digits)")
    DIGITS = {str(d): 3 + d for d in range(10)}
    digit_enc = PseudoVmsEncoder(alphabet=DIGITS, doubling_strength=0.10)
    pi = "31415926535897932384"
    cipher = digit_enc.encode(pi, rng=random.Random(1))
    print(f"  input:   {pi}")
    print(f"  encoded: {cipher}")
    print(f"  decoded: {digit_enc.decode_text(cipher)}")

    # ─── Bulk corpus encoding ────────────────────────────────────────

    section("7. Encode a corpus CSV in bulk")
    print("  Skipped here (requires a corpus_build-schema CSV on disk).")
    print("  Usage:")
    print("    enc.encode_corpus(")
    print("        source_csv='path/to/source.csv',")
    print("        out_txt='path/to/output.txt',")
    print("        out_csv='path/to/metadata.csv',  # optional")
    print("    )")

    print()


if __name__ == '__main__':
    main()
