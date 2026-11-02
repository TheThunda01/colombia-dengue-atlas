# Practical use

## Input and output contract

The release accepts the pinned INS municipality/week/year/event aggregates, DANE annual department populations, and DANE reference boundaries described in the [source register](sources.md). Preparation verifies fingerprints and geographic keys. The public panel has 33 department-level units, 2019–2022, and separate events 210 and 220. Outputs are the static atlas, filtered summary and weekly CSVs, processed tables, and SVG/PNG figure exports. No person-level input is required.

## Worked comparison

Select **Antioquia → Dengue (210) → 2019–2019 → weeks 1–52**. The built release summary contains **4,980 recorded cases**, **6,518,070 total residents**, and **76.403 cases per 100,000 total residents**. All 52 department-week cells are present. This verifies a particular source-based calculation; it does not establish that every municipality reported or every infection was detected. Download the summary CSV to retain the denominator, filters, and snapshot metadata.

Run `uv run pytest` and `node --test tests/model.test.mjs` after rebuilding. Follow the README for browser checks; inspect the active selection, missingness, rate units, and download agreement before interpreting a comparison.

## Limits and prioritized improvements

1. **Resolve date semantics:** obtain an official field definition identifying onset versus notification assignment; acceptance requires an attributable document and updated labels without retrospectively inventing dates.
2. **Extend comparable years:** inspect a newer licensed aggregate release; acceptance requires the same event/geography contract, preserved snapshots, complete elapsed periods, and rerun reconciliation.
3. **Improve denominator alignment:** evaluate documented population-at-risk data; acceptance requires matching geographic/year definitions and an explicit comparison with total-population normalization.

This tool supports descriptive surveillance exploration. It does not establish causal effects, individual risk, or reporting completeness. See [methods](methods.md) and [assumptions](assumptions.md).
