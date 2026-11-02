# Original inputs

The committed `ins_*.json` files are original response bytes from the licensed
INS public aggregate API. `ins_manifest.json` records exact queries, retrieval
timestamps, sizes and SHA-256 fingerprints. No person-level data are included.

The locally preserved `dane/` originals are excluded from Git. Reproduce them
with `uv run python scripts/prepare_geography.py --download`; every response must
match the committed `data/dane_sources.json` fingerprint. See `docs/sources.md`.
