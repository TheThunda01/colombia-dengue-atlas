# Independent scientific/data review

Review date: 2 November 2026. This is an AI-assisted source and processing review, not an epidemiological validation of surveillance capture.

## Executed independent checks

A separate standard-library Python calculation loaded the four original `ins_dengue_2019.json` through `ins_dengue_2022.json` files, aggregated by published department/year/week/event identifiers, and compared every cell with `data/processed/surveillance_weekly.json`.

- Original municipal/week/event aggregate rows: **57,083**.
- Duplicate event/year/week/department/municipality keys: **0**.
- Explicit zero counts in the original snapshots: **0**.
- Published department/week/event grid: **13,794 cells**.
- Value disagreements against independently recomputed source sums: **0**.
- Positive observed cells: **8,130**; absent-source cells preserved as JSON null: **5,664**.
- All Bogotá cells remain null; none is interpreted as reported zero.
- Foreign (`01`) and unknown (`00`) source geography are excluded from the mapped panel, with counts retained in the pipeline audit.
- Weeks present in source: 1–52 (2019), 1–53 (2020), 1–52 (2021), 1–52 (2022).

| Year | Mapped event 210 count | Mapped event 220 count |
|---|---:|---:|
| 2019 | 122,992 | 1,339 |
| 2020 | 76,220 | 860 |
| 2021 | 49,174 | 932 |
| 2022 | 65,428 | 1,330 |

These are sums of published positive rows, with sparse-source absences preserved separately. The table does not establish that every absent municipality/week reported zero cases.

District municipality codes were directly inspected in the raw snapshots: Barranquilla (`08001`) belongs to department `08`; Cartagena (`13001`) to `13`; Santa Marta (`47001`) to `47`; Cali (`76001`) and Buenaventura (`76109`) to `76`. Their source rows already carry the parent department codes. Aggregating municipality rows once includes them without adding a second district-level total.

## Code and source review

Read-only review of `scripts/prepare_surveillance.py` found no confirmed defects in source fingerprint verification, key validation, source/API reconciliation, category separation, or absent-versus-zero handling. Events 210 and 220 remain separate, avoiding an unsupported assumption that person-level overlap can be resolved from aggregates.

Read-only review of `scripts/prepare_geography.py` confirmed explicit department/year population selection (`Total` rows only), checks for 132 unique annual denominators, all 33 department-level units, and positive denominators. Geometry uses a fixed DANE 2025 display vintage; codes, not polygon overlays, join counts. The 500 m simplification is documented as a display transformation.

The INS metadata describes epidemiological week/year of occurrence and municipality/department of occurrence. It does not establish the underlying symptom-onset versus notification date implementation or an individual clinical/laboratory confirmation field. These limits need to remain explicit in published documentation.

PAHO representative data and its different classification/revision risks are documented in `docs/paho-source-assessment.md`. No PAHO observations are combined with INS.

## Scope of this review

This record covers source fields, raw-to-processed counts, absence states, district containment, and source-processing code. It does not certify case ascertainment, source clinical classification, person-level deduplication, or completeness of surveillance capture. UI calculations, rates, exports, rendered layouts, and deployment require the release checks recorded elsewhere; they were not established by this processing review.

## Shared browser data model review

After the site payload was built, `node --test tests/model.test.mjs` ran **14 tests: 14 passed, 0 failed, 0 skipped** against the actual `site/data/atlas.json` and pinned raw INS inputs. Assertions cover both separate event categories, partial seasons, geographic filters, raw-source reconciliation, annual denominator matching, the arithmetic mean of yearly rates, a missing-denominator fixture, Bogotá nulls, absent source weeks, an explicitly separated zero fixture, week 53, reversed temporal ranges, map context, CSV filter metadata and numeric agreement, URL validation, and CSV quoting.

The tests independently reconcile default mapped totals of **313,814 event-210 records** and **4,461 event-220 records** across the four selected years. These categories are tested separately and are not combined into a clinical total.

A confirmed edge case was corrected during review: an adjacent reversed year range produced a zero year count and `0/0` (NaN) in the map rate. The model now requires a positive year count before computing the mean. The regression test verifies that reversed year/week ranges produce empty summaries and null map values.

Read-only review of `site/assets/atlas.js` confirms the visible summary table and summary download use the same `summaries()` output; weekly downloads use the same `selectedRows()` filter function. The map intentionally retains all department context while the table and time series follow the selected department. Model/CSV agreement is tested; actual click-triggered downloads and rendered chart behavior still require browser verification.

A chart presentation issue was flagged to the release author: line-only Plotly traces can hide an isolated observed point surrounded by null weeks or a single selected week. Visible markers are needed to preserve those observations without connecting across missing data. This is a rendering concern, separate from the passing data-model tests, and should be checked in browser inspection.

Release follow-up: the local Edge browser checks verified single-week point visibility, sparse observations, no-data states and both actual CSV downloads. See `reports/browser_local.json` and `RELEASE_REPORT.md` for executed scope.
