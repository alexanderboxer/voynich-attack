# Voy2Vec Experiment Notes

## Goal
Use word2vec to identify distributionally equivalent "patches" (BPE-derived subword units) in the Voynich Manuscript. The hypothesis is that some patches encode the same underlying value — analogous to how tokens '41'/'52' both encoded 'r' and '43'/'54'/'ψ' all encoded 's' in the Wallis cipher.

## Approach
1. **BPE on VMS glyphs** — byte-pair encoding starting from 66 base glyphs, merging the most frequent adjacent pairs. 50 merges → 116 patches with healthy frequency distribution (only 10.3% hapax vs 70% at the raw token level).
2. **Word2Vec on patch sequences** — train skip-gram on 801 paragraph-level sentences of patches. Use baseline settings validated on wallis1 cipher (embed_dim=24, window=5, epochs=200, sg=1).
3. **Cosine similarity** to find distributionally equivalent patch pairs.

## Wallis1 Validation (working/clustering/)
Tested the approach on the Wallis cipher (a known 17th-century French diplomatic cipher with a key). Key findings:
- **Baseline settings** (embed_dim=24, window=5, epochs=200, skip-gram) gave the best overall clustering across 30 experiments.
- The model successfully clustered equivalent tokens close together (r-s scatter metric) and grouped numerals, function words, and proper nouns into meaningful clusters.
- Metrics used: **r-s scatter** (mean distance of duplicate-plaintext tokens from their centroid, lower=better) and **n-gram silhouette** (separation of tokens by plaintext length, higher=better).
- Sweeping parameters showed: fewer epochs and smaller dims improve r-s scatter but produce diffuse, undertrained global structure. The baseline is the sweet spot.
- PPMI+SVD was also tested but did not beat word2vec (cluster balance was worse).

## VMS Results So Far (50-merge BPE)

### Top distributional equivalences (cosine similarity):
- `cc,c,8,9` ↔ `c^c,c,8,9` (0.909) — bench prefix `cc` vs `c^c` interchangeable
- `P1` ↔ `P2` (0.881) — platform glyphs nearly interchangeable  
- `cc,o,Z` ↔ `cc,o,x` (0.861) — final `Z` vs `x` interchangeable
- `a,Z` ↔ `a,x` (0.850), `a,Z` ↔ `a,m` (0.849) — common word-final patterns equivalent
- `c,8,9` ↔ `c,c,8,9` (0.881) — extra `c` makes no distributional difference
- `4,o,N` ↔ `o,N` (0.812) — the `4` prefix is optional
- `c^c,c` ↔ `cc,c` (0.714) — bench prefix equivalence again

### Clustering structure:
- Uncertain readings (`?`-marked glyphs) cluster together by type
- Rare special characters (`<`, `>`, `â`, `ô`) form their own cluster
- Platform glyphs (`P1`, `P2`) cluster together
- The bulk of common patches split into two main groups

## Files
- `bpe.py` — BPE implementation. Usage: `python bpe.py [n_merges]` (default 50)
- `bpe_50.json` — BPE output: merges, vocab, patch_sentences
- `bpe_50_patches.csv` — patch frequency table (116 patches)
- `patch2vec.py` — word2vec on BPE patches. Usage: `python patch2vec.py [bpe_file]`
- `patch2vec_50.png` — t-SNE visualization
- `voy2vec.py` — word2vec on raw VMS tokens (not useful due to 70% hapax)
- `voy2vec_0.png/csv` — raw token experiment (for reference)

## Next Steps
- Experiment with different BPE merge counts (e.g., 30, 75, 100) to find optimal granularity
- Deeper analysis of the equivalence pairs — do they hold across manuscript sections (herbal vs astronomical)?
- Use the equivalences to reduce the effective vocabulary and re-examine token-level patterns
- Compare against existing Voynich research on glyph equivalences
