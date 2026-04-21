"""Reference-corpus build pipeline.

Target CSV schema is defined in `schema`. Source-specific helpers (e.g.
DTA) live in their own submodules and produce rows conforming to that
schema via the generic format parsers (e.g. `tei_p5`).
"""
