# `voynpy.pseudo_vms`

Generates symbol-sequence cipher text from natural-language plaintext.
Each input symbol is encoded as a token of 2–6 hexadecimal characters
whose values sum to a target value associated with the symbol. The
cipher is parameterized so that the generated stream can be tuned to
match the statistical properties of a chosen target distribution.

## Install

Standard voynpy install:

    pip install -e .

## Quick start

    from voynpy.pseudo_vms import PseudoVmsEncoder

    enc = PseudoVmsEncoder()

    # encode → cipher tokens (space-separated)
    cipher = enc.encode("hello world")

    # decode → recovers plaintext (one symbol per token)
    enc.decode_text(cipher)         # "helloworld"

    # bulk encode a corpus_build-schema CSV
    enc.encode_corpus("source.csv", "cipher.txt", out_csv="metadata.csv")

    # save / reload the cipher table for reproducibility
    enc.save("cipher_table.csv")
    same = PseudoVmsEncoder.load("cipher_table.csv")

For a runnable walkthrough:

    python -m voynpy.pseudo_vms.demo

## Constructor parameters

| parameter | default | meaning |
|---|---|---|
| `alphabet` | `{a:3, b:4, …, z:28}` | symbol → integer value map |
| `zipf_exponent` | `1.0` | within-symbol sampling power law (`0`=uniform, `1`=Zipf-1) |
| `doubling_strength` | `0.26` | probability of reusing the previous token on consecutive same-symbol input |
| `tokens_per_char` | `500` | target token-count per symbol |
| `length_distribution` | `{2:10, 3:22, 4:26, 5:26, 6:16}` | target % share of tokens by length (sums to 100) |
| `seed` | `42` | RNG seed for deterministic table construction |
| `table_path` | `None` | if given (and exists), load a previously saved table |

## Methods

| method | purpose |
|---|---|
| `encode(text, rng=None)` | encode a plaintext string; newlines preserved as paragraph breaks |
| `encode_corpus(source_csv, out_txt, out_csv=None, …)` | bulk-encode a corpus_build-schema CSV |
| `decode(token)` | recover the symbol for a single token |
| `decode_text(cipher)` | recover the plaintext from a cipher stream |
| `tokens_for(symbol)` | list of `(token, weight)` for a symbol |
| `tune_to_vms(target_doubling_rate, sample_text)` | adjust `doubling_strength` to hit a target output doubling rate |
| `save(path)` | persist the cipher table to CSV |
| `load(path, **overrides)` *(classmethod)* | construct an encoder from a saved table |
| `compare_to_vms(vms_csv, pseudo_corpus_txt)` | diagnostic comparison of a generated corpus against `vms.csv` |

## Custom alphabets

The `alphabet` argument accepts any `{symbol_str: int_value}` mapping.
Each symbol gets its own table of cipher tokens whose values sum to
the symbol's integer value.

    DIGITS = {str(d): 3 + d for d in range(10)}
    enc = PseudoVmsEncoder(alphabet=DIGITS, doubling_strength=0.10)
    cipher = enc.encode("31415926535897932384")

## Reproducibility

Two reproducibility levels:

- **Seed-deterministic**: same code + same `seed` → identical cipher table.
- **Persisted-deterministic**: `enc.save(path)` writes the table to CSV;
  any future `PseudoVmsEncoder.load(path)` produces the exact same
  encoder behavior, regardless of code changes. Prefer this for
  experiments where the cipher must remain stable across time.

## Files in this package

- `encoder.py` — the `PseudoVmsEncoder` class
- `demo.py` — runnable demo of the main API
- `README.md` — this file
