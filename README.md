# Voynich Attack

The Voynich Manuscript is the Holy Grail of cipher mysteries. Dating from
the late Middle Ages (*maybe*), the manuscript sports bizarre illustrations
of extraterrestrial-looking plants, bevies of bathing beauties in networks
of tubes, and thousands upon thousands of "words" written in an utterly
unknown alphabet.

By all the laws of cryptology, the Voynich should have been cracked decades
ago. It never has. Not a single word has ever been deciphered despite drawing
the gaze of the world's preeminent cryptographic agencies and the internet's
most obsessive amateurs. What harm, then, in one more foolish foray into
this most enchantingly cryptic enigma?

## Install

    pip install -e .

Requires Python 3.12+.

## Quickstart

    from voynpy.corpora import vms, latin, german

    vms.tkdf(1).head(10)     # top tokens in the Voynich
    vms.chardf(3).head(10)   # top 3-character sequences in the Voynich
    latin.tkdf(2).head(10)   # top Latin bigrams
    german.df.head()         # sentence-level access to the German corpus

Every reference corpus exposes `tkdf(n)` and `chardf(n)` for n-gram
frequency tables at arbitrary order, plus a `.df` attribute with the
underlying sentence-level data.

## What's in here

- **`transcription/`** — the Voynich transcription. See below.
- **`corpora/`** — reference texts in various languages, packaged as
  sentence-level CSVs with regenerable build scripts.
- **`voynpy/`** — the analysis package. `RefText` class, lazy corpus
  registry (`voynpy.corpora`), n-gram frequency methods, and a TEI/XML
  parsing pipeline (`voynpy.corpus_build`) for adding new reference texts.
- **`voynpy.pseudo_vms`** — symbol-sequence cipher generator (see [package README](voynpy/pseudo_vms/README.md)).

## The Voynich transcription

`transcription/vms.csv` is an independent, complete transcription of the
Voynich Manuscript block text, made directly from the imagery and not
derived from any prior transcription. The transcription scheme is a custom glyph alphabet; unicode mappings
are provided in `transcription/unicode_dict.json`.

If you use the transcription in your own work, please cite this repo.
See [`transcription/LICENSE`](transcription/LICENSE) for terms (CC-BY 4.0).

## Primary reference corpora

| Language | Source | Texts | Tokens |
|---|---|---:|---:|
| **German** | Deutsches Textarchiv (DTA) + Luther Bibel 1545 (Zeno.org) | 559 | 14,148,299 |
| **Latin** | Corpus Corporum (UZH) + Perseus classical | 71 | 4,349,322 |
| **Dutch** | Digitale Bibliotheek voor de Nederlandse Letteren (DBNL) | 12 | 1,670,838 |
| **French** | Project Gutenberg + Wikisource | 9 | 954,293 |
| **English** | EEBO-TCP | 10 | 507,704 |
| **Voynich** | own transcription | 1 | 33,669 |

Additional smaller corpora are also available via `voynpy.corpora` —
Spanish, Hebrew, Enochian, and some historical ciphers.

All corpora load lazily on first attribute access:

    from voynpy.corpora import latin, german, dutch, english, french, vms

Each reference text retains its **upstream license** (CC-BY, CC-BY-SA, or
public-domain depending on the source). See each source's site for terms
before redistributing.

## License

- **Code** (everything under `voynpy/`, build scripts, repo Python
  files) — [MIT](LICENSE)
- **Voynich transcription** (`transcription/`) — [CC-BY 4.0](transcription/LICENSE).
  Use freely, with attribution.
- **Reference corpora** (`corpora/`) — upstream licenses apply per text.
