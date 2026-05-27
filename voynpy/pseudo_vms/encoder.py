"""Pseudo-VMS encoder.

Generates pseudo-VMS cipher text from natural-language plaintext.
Each NL symbol (letter, digit, etc.) maps to a cipher token whose
hex-character values sum to the symbol's value. The cipher is
parameterized so the resulting corpus statistically resembles real
VMS (token-length distribution, Zipf curve, doubling rate).

Quick start:

    from voynpy.pseudo_vms import PseudoVmsEncoder

    enc = PseudoVmsEncoder()
    cipher = enc.encode("Take ipecacuanha and water")
    # → "EEF74 EA94 FFFF74 EE930 ..."

    # Encode an entire corpus_build-schema CSV:
    enc.encode_corpus("input.csv", "output.txt")

    # Persist the cipher table for reproducibility:
    enc.save("my_cipher.csv")
    loaded = PseudoVmsEncoder.load("my_cipher.csv")

    # Auto-tune doubling to match VMS rate:
    enc.tune_to_vms(target_doubling_rate=0.0092, sample_text=plaintext)

    # Use a non-letter alphabet (e.g., for digits of π):
    PI_ALPHABET = {str(d): 3 + d for d in range(10)}
    pi_enc = PseudoVmsEncoder(alphabet=PI_ALPHABET)

Cipher design:
  - Cipher alphabet: 16 hex chars '0'-'9' + 'A'-'F' with values
      '0'-'9' → 0-9
      'A' → 10, 'B' → 11, 'C' → 12, 'D' → 13
      'E' → -1, 'F' → -2
  - Each NL symbol's tokens are 2-6 cipher chars summing to the symbol's value
  - Token ordering: negatives at far left sorted high-to-low (E before F),
    then positives sorted high-to-low (D, C, B, A, 9, ..., 1, 0)
  - Sampling biases: length distribution calibrated to real VMS;
    within-symbol weights follow a power law (zipf_exponent)
  - NL-symbol doubling preserved as same-token repeat with probability
    doubling_strength
"""
import csv
import random
import re
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Iterable, Mapping, Optional, Union


# ─── Cipher constants ─────────────────────────────────────────────────────────

HEX_CHARS = '0123456789ABCDEF'
HEX_VALUE = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'D': 13,
    'E': -1, 'F': -2,
}

# Token ordering: negatives prefix (high-to-low, so E before F),
# then positives high-to-low (D, C, B, A, 9, ..., 0).
NEGATIVES_HIGH_TO_LOW = ['E', 'F']
POSITIVES_HIGH_TO_LOW = list('DCBA9876543210')


# ─── Defaults ─────────────────────────────────────────────────────────────────

# 26-letter NL alphabet: a=3, b=4, ..., z=28
DEFAULT_ALPHABET: Mapping[str, int] = {
    chr(ord('a') + i): 3 + i for i in range(26)
}

# Length distribution calibrated against real VMS within the 2-6 char range
# (real VMS L2..L6 share: 10/22/26/26/16 in %).
DEFAULT_LENGTH_DISTRIBUTION: Mapping[int, int] = {2: 10, 3: 22, 4: 26, 5: 26, 6: 16}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _order_token(chars: Iterable[str]) -> str:
    """Apply the token ordering rule: negatives prefix (E before F),
    then positives high-to-low."""
    chars = list(chars)
    negs = sorted([c for c in chars if c in NEGATIVES_HIGH_TO_LOW],
                  key=lambda c: NEGATIVES_HIGH_TO_LOW.index(c))
    pos = sorted([c for c in chars if c not in NEGATIVES_HIGH_TO_LOW],
                 key=lambda c: POSITIVES_HIGH_TO_LOW.index(c))
    return ''.join(negs + pos)


def _enumerate_encodings(target_value: int, min_len: int = 2, max_len: int = 6):
    """Yield all distinct ordered tokens of length min_len..max_len whose
    cipher-char values sum to target_value.

    Returns a list of token strings (deduplicated by ordered form).
    """
    seen = set()
    out = []
    for n in range(min_len, max_len + 1):
        for combo in combinations_with_replacement(HEX_CHARS, n):
            if sum(HEX_VALUE[c] for c in combo) == target_value:
                tok = _order_token(combo)
                if tok not in seen:
                    seen.add(tok)
                    out.append(tok)
    return out


def _sample_with_length_bias(
    tokens: list[str],
    length_distribution: Mapping[int, int],
    total_target: int,
    rng: random.Random,
) -> list[str]:
    """Sample tokens stratified by length to match length_distribution.

    Strict: each length bucket is capped at its proportional target.
    Buckets with fewer tokens than the target contribute all they have;
    the total may end up less than total_target — this is by design,
    preserving the requested length proportions.
    """
    by_len = {n: [] for n in length_distribution}
    for tok in tokens:
        n = len(tok)
        if n in by_len:
            by_len[n].append(tok)

    targets = {n: round(length_distribution[n] / 100 * total_target)
               for n in length_distribution}

    out = []
    for n, target in targets.items():
        bucket = by_len[n]
        if len(bucket) >= target:
            out.extend(rng.sample(bucket, target))
        else:
            out.extend(bucket)
    return out


# ─── The class ────────────────────────────────────────────────────────────────

class PseudoVmsEncoder:
    """Encoder for the algebra-cipher pseudo-VMS scheme.

    The encoder builds a table of cipher tokens for each NL symbol on
    construction (or loads one from disk). It then encodes NL plaintext
    by sampling per-symbol tokens with the configured weights, preserving
    NL symbol-doublings as cipher-token repeats with the configured
    probability.

    Parameters
    ----------
    alphabet : mapping str → int
        NL-symbol → integer value mapping. Default: a..z = 3..28.
        Pass a custom dict for non-letter alphabets (e.g., digits of π).
    zipf_exponent : float
        Power-law exponent for within-symbol sampling. 0 = uniform,
        1 = Zipf-1 (matches VMS), > 1 = heavily peaked. Default 1.0.
    doubling_strength : float
        Probability that consecutive same NL symbols in the plaintext
        produce a same-cipher-token doubling. Language-specific; tune
        with `.tune_to_vms()` from a sample. Default 0.26 (calibrated
        for English; Latin typically wants ~0.16).
    tokens_per_char : int
        Target number of cipher tokens generated per NL symbol. Default 500.
        Actual count may be less for symbols with constrained encoding
        spaces (e.g., 'a'=3 has fewer length-6 encodings than 'z'=28).
    length_distribution : mapping int → int
        Target percentage share of tokens by length (must sum to 100).
        Default {2: 10, 3: 22, 4: 26, 5: 26, 6: 16} matches real VMS.
    seed : int
        RNG seed for deterministic sampling. Default 42.
    table_path : Path-like, optional
        If given AND the file exists, load the cipher table from CSV
        instead of generating from scratch. Use for reproducibility
        across versions / machines.
    """

    DEFAULT_DOUBLING_STRENGTH = 0.26

    def __init__(
        self,
        alphabet: Mapping[str, int] = DEFAULT_ALPHABET,
        zipf_exponent: float = 1.0,
        doubling_strength: float = DEFAULT_DOUBLING_STRENGTH,
        tokens_per_char: int = 500,
        length_distribution: Mapping[int, int] = DEFAULT_LENGTH_DISTRIBUTION,
        seed: int = 42,
        table_path: Optional[Union[str, Path]] = None,
    ):
        self.alphabet = dict(alphabet)
        self.zipf_exponent = float(zipf_exponent)
        self.doubling_strength = float(doubling_strength)
        self.tokens_per_char = int(tokens_per_char)
        self.length_distribution = dict(length_distribution)
        self.seed = int(seed)

        # Validate length_distribution sums to 100
        if abs(sum(self.length_distribution.values()) - 100) > 1e-6:
            raise ValueError(
                f"length_distribution must sum to 100, got "
                f"{sum(self.length_distribution.values())}"
            )

        if table_path is not None and Path(table_path).exists():
            self._load_table(Path(table_path))
        else:
            self._build_table()

        # Build the inverse map for decoding (each token sums to a unique
        # NL value, so decoding is unambiguous)
        self._token_to_symbol: dict[str, str] = {}
        for symbol, entries in self._table.items():
            for tok, _w in entries:
                self._token_to_symbol[tok] = symbol

    # ─── Table construction ──────────────────────────────────────────────

    def _build_table(self) -> None:
        """Build self._table: dict[symbol → list[(token, weight)]]."""
        rng = random.Random(self.seed)
        self._table: dict[str, list[tuple[str, float]]] = {}
        for symbol, value in self.alphabet.items():
            all_tokens = _enumerate_encodings(value)
            sampled = _sample_with_length_bias(
                all_tokens, self.length_distribution, self.tokens_per_char, rng
            )
            rng.shuffle(sampled)  # randomize Zipf-rank assignment
            weights = self._compute_weights(len(sampled))
            self._table[symbol] = list(zip(sampled, weights))

    def _compute_weights(self, n: int) -> list[float]:
        """Power-law weights ∝ 1/r^s, normalized to sum to 1."""
        if n == 0:
            return []
        if self.zipf_exponent == 0:
            return [1.0 / n] * n
        raw = [1.0 / ((r + 1) ** self.zipf_exponent) for r in range(n)]
        total = sum(raw)
        return [w / total for w in raw]

    # ─── Encoding ─────────────────────────────────────────────────────────

    def encode(self, text: str, rng: Optional[random.Random] = None) -> str:
        """Encode an NL plaintext string into a pseudo-VMS cipher stream.

        Multi-line input: each line becomes its own paragraph in the output
        (preserves VMS's paragraph structure). Within a line, tokens are
        space-separated; NL word boundaries are dropped (matching real VMS).

        NL symbol doublings (whitespace-collapsed) are preserved as same-
        cipher-token repeats with probability self.doubling_strength.
        """
        if rng is None:
            rng = random
        out_lines = []
        for line in text.splitlines() or [text]:
            tokens = self._encode_line(line, rng)
            out_lines.append(' '.join(tokens))
        return '\n'.join(out_lines)

    def _encode_line(self, line: str, rng: random.Random) -> list[str]:
        out = []
        prev_symbol = None
        prev_token = None
        for ch in self._normalize(line):
            if ch in self.alphabet:
                if ch == prev_symbol and rng.random() < self.doubling_strength:
                    tok = prev_token
                else:
                    entries = self._table[ch]
                    if not entries:
                        continue
                    toks, weights = zip(*entries)
                    tok = rng.choices(toks, weights=weights, k=1)[0]
                out.append(tok)
                prev_symbol = ch
                prev_token = tok
            # non-alphabet char: skip (cipher drops whitespace and punctuation);
            # prev_symbol/prev_token carry across the gap so cross-word
            # doublings (e.g. "es soll" → ...s+s...) are still preserved.
        return out

    def _normalize(self, text: str) -> str:
        """Default: lowercase if alphabet is all-lowercase letters; otherwise
        leave alone. Override per use case if needed."""
        if all(k.islower() and k.isalpha() for k in self.alphabet):
            return text.lower()
        return text

    def encode_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        rng_seed: Optional[int] = None,
    ) -> dict:
        """Encode a plain-text file. Each line in the input becomes one
        paragraph in the output (one line of space-separated cipher
        tokens). Blank lines are preserved as blank lines.

        Parameters
        ----------
        input_path : Path
            Plain-text file to encode.
        output_path : Path
            Where to write the cipher output.
        rng_seed : int, optional
            Seed for encoding randomness. If None, uses the encoder's
            construction seed.

        Returns
        -------
        dict with: total_paragraphs (non-empty output lines),
        total_tokens, mean_tokens_per_paragraph.
        """
        rng = random.Random(rng_seed if rng_seed is not None else self.seed)
        text = Path(input_path).read_text(encoding='utf-8')
        cipher = self.encode(text, rng=rng)
        Path(output_path).write_text(cipher, encoding='utf-8')

        non_empty_lines = [ln for ln in cipher.splitlines() if ln.strip()]
        total_tokens = sum(len(ln.split()) for ln in non_empty_lines)
        return {
            'total_paragraphs': len(non_empty_lines),
            'total_tokens': total_tokens,
            'mean_tokens_per_paragraph': total_tokens / max(len(non_empty_lines), 1),
        }

    def encode_corpus(
        self,
        source_csv: Union[str, Path],
        out_txt: Union[str, Path],
        out_csv: Optional[Union[str, Path]] = None,
        text_column: str = 'textstring_simple',
        block_type: str = 'body',
        group_by: Optional[str] = 'para_id',
        rng_seed: Optional[int] = None,
    ) -> dict:
        """Encode an entire corpus_build-schema CSV into pseudo-VMS.

        Rows are grouped by `group_by` (default: 'para_id') and each
        group becomes one output paragraph: the row texts in the group
        are concatenated and encoded as a single token stream. With
        `group_by=None`, every row becomes its own output paragraph.

        Parameters
        ----------
        source_csv : Path
            corpus_build-schema CSV (must have a textstring column).
        out_txt : Path
            Output .txt path for the pseudo-VMS corpus.
        out_csv : Path, optional
            Output .csv path for metadata.
        text_column : str
            Which column to encode. Default 'textstring_simple'.
        block_type : str
            If source has a 'block_type' column, filter to this value.
        group_by : str or None
            Column to group source rows on for paragraph aggregation.
            Default 'para_id' (one output paragraph per source paragraph).
            Set to None to emit one output paragraph per source row.
        rng_seed : int, optional
            If given, use this seed for encoding randomness.

        Returns
        -------
        dict with: total_paragraphs, total_tokens, mean_tokens_per_paragraph.
        """
        import pandas as pd

        source_csv = Path(source_csv)
        out_txt = Path(out_txt)
        rng = random.Random(rng_seed if rng_seed is not None else self.seed)

        df = pd.read_csv(source_csv, keep_default_na=False)
        if 'block_type' in df.columns:
            df = df[df['block_type'] == block_type]

        # Build groups: each group becomes one output paragraph.
        if group_by is not None and group_by in df.columns:
            groups = list(df.groupby(group_by, sort=False))
        else:
            # one group per row
            groups = [(int(row.get('para_id', i)), row.to_frame().T)
                      for i, (_, row) in enumerate(df.iterrows())]

        txt_lines = []
        meta_rows = []
        para_id_out = 0

        for source_key, gdf in groups:
            # Concatenate text from all rows in the group (sentences in a paragraph)
            parts = []
            sent_ids = []
            for _, row in gdf.iterrows():
                t = row.get(text_column, '')
                if isinstance(t, str) and t.strip():
                    parts.append(t)
                    sent_ids.append(int(row.get('sent_id', 0)) if 'sent_id' in row else None)
            if not parts:
                continue
            combined_text = ' '.join(parts)
            tokens = self._encode_line(combined_text, rng)
            if not tokens:
                continue

            para_id_out += 1
            cipher_text = ' '.join(tokens)
            txt_lines.append(cipher_text)
            meta_rows.append({
                'pseudo_para_id': para_id_out,
                'source_group_key': source_key,
                'n_source_sentences': len(parts),
                'n_tokens': len(tokens),
                'cipher_text': cipher_text,
            })

        out_txt.write_text('\n'.join(txt_lines) + '\n', encoding='utf-8')
        if out_csv is not None:
            out_csv = Path(out_csv)
            with open(out_csv, 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['pseudo_para_id',
                                                  'source_group_key',
                                                  'n_source_sentences',
                                                  'n_tokens',
                                                  'cipher_text'])
                w.writeheader()
                w.writerows(meta_rows)

        total_tokens = sum(r['n_tokens'] for r in meta_rows)
        return {
            'total_paragraphs': para_id_out,
            'total_tokens': total_tokens,
            'mean_tokens_per_paragraph': total_tokens / max(para_id_out, 1),
        }

    # ─── Inspection ──────────────────────────────────────────────────────

    def tokens_for(self, symbol: str) -> list[tuple[str, float]]:
        """Return the (token, weight) list for the given NL symbol."""
        return list(self._table.get(symbol, []))

    def decode(self, token: str) -> str:
        """Decode a cipher token to its NL symbol. Returns '?' if the
        token's value doesn't correspond to any alphabet symbol."""
        return self._token_to_symbol.get(token, '?')

    def decode_text(self, cipher_text: str) -> str:
        """Decode a stream of space-separated cipher tokens to NL symbols.
        Newlines preserved. Unknown tokens emit '?'."""
        out_lines = []
        for line in cipher_text.splitlines() or [cipher_text]:
            chars = [self.decode(t) for t in line.split() if t]
            out_lines.append(''.join(chars))
        return '\n'.join(out_lines)

    # ─── Tuning ───────────────────────────────────────────────────────────

    def tune_to_vms(
        self,
        target_doubling_rate: float = 0.0092,
        sample_text: Optional[str] = None,
        max_iterations: int = 30,
        tolerance: float = 0.0005,
    ) -> float:
        """Adjust self.doubling_strength so that encoding `sample_text`
        produces a cipher doubling rate matching `target_doubling_rate`.

        Real VMS doubling rate ≈ 0.92% (0.0092). The right doubling_strength
        is language-specific because it depends on the source's NL letter-
        doubling rate.

        If sample_text is None, uses a built-in calibration sample (a short
        passage approximating mixed letter frequencies; not language-specific,
        so prefer passing your own sample_text for best results).

        Returns the new doubling_strength value (and updates self in-place).
        """
        if sample_text is None:
            # Fallback: a short pangram-ish English sample
            sample_text = (
                "the quick brown fox jumps over the lazy dog "
                "she sells seashells by the seashore "
                "all things bright and beautiful all creatures great and small"
            ) * 100

        def measure_rate(p: float) -> float:
            old = self.doubling_strength
            self.doubling_strength = p
            try:
                cipher = self.encode(sample_text)
                tokens = cipher.split()
                if len(tokens) < 2:
                    return 0.0
                doubles = sum(1 for i in range(len(tokens) - 1)
                              if tokens[i] == tokens[i+1])
                return doubles / (len(tokens) - 1)
            finally:
                self.doubling_strength = old

        # Bracket and bisect: find p in [0, 1] where measure_rate(p) ≈ target
        lo, hi = 0.0, 1.0
        for _ in range(max_iterations):
            mid = (lo + hi) / 2
            r = measure_rate(mid)
            if abs(r - target_doubling_rate) < tolerance:
                self.doubling_strength = mid
                return mid
            if r < target_doubling_rate:
                lo = mid
            else:
                hi = mid

        self.doubling_strength = (lo + hi) / 2
        return self.doubling_strength

    # ─── Persistence ──────────────────────────────────────────────────────

    def save(self, path: Union[str, Path]) -> None:
        """Persist the cipher table to a CSV.

        The CSV captures the symbol→token mapping and weights, so loading
        it produces the exact same encoder behavior even if the code
        changes. Use this to share a frozen cipher with collaborators or
        to lock in a cipher for a long-running experiment.

        Note: doubling_strength, zipf_exponent, and other configuration
        parameters are NOT saved here — they're applied at encoding time
        and can be changed without rebuilding the table.
        """
        path = Path(path)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['symbol', 'value', 'rank', 'token', 'weight'])
            for symbol, entries in self._table.items():
                v = self.alphabet[symbol]
                for rank, (tok, weight) in enumerate(entries, start=1):
                    w.writerow([symbol, v, rank, tok, weight])

    def _load_table(self, path: Path) -> None:
        """Load a previously saved cipher table from CSV."""
        self._table = {}
        loaded_alphabet = {}
        with open(path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                symbol = row['symbol']
                value = int(row['value'])
                tok = row['token']
                weight = float(row['weight'])
                loaded_alphabet[symbol] = value
                self._table.setdefault(symbol, []).append((tok, weight))
        # Reconcile: if user passed alphabet that differs from saved,
        # prefer the saved one (it's authoritative for the loaded table).
        self.alphabet = loaded_alphabet

    @classmethod
    def load(cls, path: Union[str, Path], **kwargs) -> 'PseudoVmsEncoder':
        """Construct a PseudoVmsEncoder by loading its cipher table from
        a previously-saved CSV.

        Any keyword arguments override the loaded values (e.g., you can
        load a table but use a different doubling_strength).
        """
        kwargs.setdefault('table_path', path)
        return cls(**kwargs)

    # ─── Diagnostics ──────────────────────────────────────────────────────

    def compare_to_vms(
        self,
        vms_csv: Union[str, Path],
        pseudo_corpus_txt: Union[str, Path],
    ) -> dict:
        """Compute side-by-side stats vs real VMS for a generated corpus.

        Returns a dict with: total_tokens, unique_tokens, doubling_rate,
        top_N coverage, paragraph length stats, both for VMS and pseudo.
        """
        import pandas as pd

        # Real VMS
        df = pd.read_csv(vms_csv)
        token_cols = [c for c in df.columns if re.fullmatch(r't\d+', c)]
        vms_linear = []
        vms_paras: list[list[str]] = []
        last_par = None
        current = []
        for _, row in df.sort_values(['folio', 'par', 'line']).iterrows():
            par_key = (row['folio'], int(row['par']))
            if last_par is not None and par_key != last_par:
                vms_linear.append(None)
                vms_paras.append(current)
                current = []
            last_par = par_key
            for c in token_cols:
                v = row[c]
                if isinstance(v, str) and v != '$' and v.strip():
                    tok = v.strip()
                    vms_linear.append(tok)
                    current.append(tok)
        if current:
            vms_paras.append(current)

        # Pseudo-VMS
        pseudo_paras: list[list[str]] = []
        pseudo_linear: list[Optional[str]] = []
        for line in Path(pseudo_corpus_txt).read_text().splitlines():
            line = line.strip()
            if not line:
                if pseudo_linear and pseudo_linear[-1] is not None:
                    pseudo_linear.append(None)
                continue
            toks = line.split()
            if pseudo_linear and pseudo_linear[-1] is not None:
                pseudo_linear.append(None)
            pseudo_linear.extend(toks)
            pseudo_paras.append(toks)

        def stats(linear: list, paras: list[list[str]]) -> dict:
            toks = [t for t in linear if t is not None]
            counts = Counter(toks)
            doubles = sum(1 for i in range(len(linear) - 1)
                          if linear[i] is not None and linear[i+1] is not None
                          and linear[i] == linear[i+1])
            sorted_counts = sorted(counts.values(), reverse=True)
            n = len(toks)
            cov = {}
            for cp in [1, 5, 10, 25, 50, 100, 250, 500, 1000]:
                if cp > len(sorted_counts):
                    cov[cp] = None
                else:
                    cov[cp] = sum(sorted_counts[:cp]) / n
            para_lens = sorted([len(p) for p in paras])
            return {
                'n_tokens': n,
                'n_unique': len(counts),
                'n_paragraphs': len(paras),
                'doubling_rate': doubles / max(n, 1),
                'top_n_coverage': cov,
                'paragraph_lengths': {
                    'p10': para_lens[len(para_lens) // 10] if para_lens else 0,
                    'p50': para_lens[len(para_lens) // 2] if para_lens else 0,
                    'p90': para_lens[len(para_lens) * 9 // 10] if para_lens else 0,
                    'mean': sum(para_lens) / max(len(para_lens), 1),
                },
            }

        return {
            'vms': stats(vms_linear, vms_paras),
            'pseudo': stats(pseudo_linear, pseudo_paras),
        }

    # ─── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"PseudoVmsEncoder(alphabet_size={len(self.alphabet)}, "
            f"zipf_exponent={self.zipf_exponent}, "
            f"doubling_strength={self.doubling_strength}, "
            f"tokens_per_char={self.tokens_per_char})"
        )
