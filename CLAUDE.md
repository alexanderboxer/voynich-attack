# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voynich-attack is a Python cryptanalysis research project for analyzing the Voynich Manuscript. It provides tools for transcription management, n-gram statistical analysis, and comparative corpus analysis across multiple languages (Latin, German, English, French, Spanish, Hebrew, Enochian) and historical ciphers.

## Setup

```bash
pip install -e .           # Install voynpy package in development mode
pip install -r requirements.txt  # Install dependencies (pandas, numpy, matplotlib, IPython)
```

Requires Python 3.12+.

## Running Scripts

Scripts must be run from their own directory due to relative path dependencies:

```bash
cd sequences && python voypars.py        # Generate paragraph-level CSV
cd transcription && python vms_cleanup.py # Validate/clean transcription
cd transcription && python vms_to_markdown.py
```

Statistical report scripts in `topics/` subdirectories follow the same pattern. There is no Makefile, test suite, or linter configured.

## Architecture

### voynpy Package (core library)

- **`reftext.py`** — `RefText` class: holds a reference text as token list (`tklist`), character list (`charlist`), and optional DataFrame (`df`). Key methods: `tkdf(order)` and `chardf(order)` produce n-gram frequency DataFrames. Multiple factory functions (`from_string`, `from_txt`, `from_csv`, `from_dataframe`, `from_textstring_csv` and variants) handle different source formats.

- **`corpora.py`** — Instantiates all reference text objects as module-level variables at import time (no lazy loading). Imports like `from voynpy.corpora import vms` give direct access. Manages path resolution by changing to the module directory during load, then restoring the original cwd.

### Key Voynich Segmentations (from corpora.py)

`vms` (full text), `vms1`/`vms2` (herbal/astronomical halves), `plants1`/`plants2`/`plants`, `fems`, `stars`, `r7`/`w7` (specific folios).

### Data Formats

- **vms.csv**: Columns are folio, par, line, t1–t26. Tokens are comma-separated character sequences (e.g., "c,N,c,a,Z"). `$` = null/empty cell.
- **voypars.csv**: Index is "folio.side.paragraph", content is semicolon-separated tokens.
- **Reference corpora**: Text files or CSVs with varying column layouts; encoding variants handled by `from_textstring_csv_var1` (allows `&`) and `from_textstring_csv_lat0` (Latin-0).

### Path Conventions

Scripts use `sys.path.insert(0, '<relative-path-to-voynpy>')` to locate the package. Nesting depth varies (e.g., `'../voynpy'` in sequences/, `'../../../voynpy'` in deep topic directories).
