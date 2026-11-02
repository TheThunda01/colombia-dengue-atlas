# First-release validation — 2 November 2026

**Colombia Dengue Surveillance Atlas v1.0.0**, by Brandon Huynh.

Repository: https://github.com/TheThunda01/colombia-dengue-atlas

Website: https://thethunda01.github.io/colombia-dengue-atlas/

Publication verification is recorded below once the hosted run and live checks
finish. A local build is not evidence of a successful deployment.

## Completed local release checks

- Environment verified on Windows 11 x64, Python 3.12.10, uv 0.11.15, Quarto 1.9.37,
  Node 24.22.0. Project Python dependencies are frozen in `uv.lock`; Quarto is
  launched with `QUARTO_PYTHON` set to that interpreter. Missing GitHub CLI was
  unnecessary because authenticated Git and the GitHub API were available.
- INS source: 57,083 original aggregate rows; all 8,358 source department/week/event
  sums matched an independent API aggregation. Separate computational review
  recomputed all 13,794 public cells without discrepancies. No person-level
  records are included.
- **28 Python tests passed**; **14 JavaScript model tests passed**, no skips.
  These include district containment, excluded geography, week53, true zero
  versus missing fixtures, duplicate/hash/license rejection, annual population
  matching, rates, URL parsing, and CSV agreement.
- DANE: 132 positive matched denominators, 33 valid map units, zero unmatched
  identifiers. Raw geometry reduced from 1,079,179 to 14,492 coordinates for display.
- Quarto rendered all four pages, including a Python-executed source summary.
  **93 local links/assets checked**, all scripts self-hosted, no root-relative
  paths. All data and interactions fit a static GitHub Pages deployment.
- Actual Edge browser checks passed 11 scenario groups on the rendered site:
  default totals; summary/weekly CSVs; all filters and saved URL; keyboard map
  selection; Bogotá no-data; separate event categories and isolated points;
  single-week and inverted ranges; week53; 390px portrait/844px landscape;
  navigation/figure/source table; deliberate failed data fetch.
- Browser checks reported zero page errors and zero HTTP errors on the successful
  local run. Earlier local checks encountered a hidden collapsed week control
  in the test harness and intermittent server/request timing failures; these
  were corrected/retried, not counted as passes.
- Visually inspected the desktop explorer, mobile portrait explorer, mobile
  seasonal chart, overview and standalone publication figure. An independent
  screenshot review inspected the same five artifacts. Fixed duplicate title,
  mobile source-table overflow, explicit table denominator wording, and missing
  horizontal-scroll guidance. SVG, 300 dpi PNG and PDF figure exports succeeded.

Evidence: `reports/browser_local.json`, `reports/independent_scientific_review.md`,
`reports/geography_validation.json`, `reports/build_validation.json`, source
manifests, tests, and `docs/screenshots/`.

## Corrections made before release

Reversed adjacent years previously allowed NaN map rates; a guarded calculation
and regression test now return missing values. Isolated observed weeks could
vanish in line-only charts; small markers now retain them while gaps stay
unconnected. Browser checks verified both corrections. A Windows encoding edit
introduced mojibake in README/UI strings; explicit UTF-8 repair restored them.
Original observations were not changed to resolve interface defects.

## Scope and limits

The data cover 2019–2022, 32 departments plus Bogotá as unavailable. INS events 210
and 220 remain separate. Foreign/unknown geography is excluded and audited.
Data last updated 17 October 2024 were retrieved 2 November 2026. Sparse source absence
does not establish zero; source epiweek cannot be confidently labeled onset or
notification time. Rates use DANE total population and do not reproduce official
population-at-risk incidence. Fixed MGN2025 geometry is a display reference.

Software checks establish transformation and interface consistency, not complete
case ascertainment or scientific/clinical validation. Human epidemiological
review, screen-reader testing, physical touch-device testing, and cross-browser
testing beyond Edge/Chromium were not performed. The official geographic license
page was inspected through its search-index content after direct access timed out.
PAHO was investigated but its observations were not combined with INS.

## Reproduce

`uv sync --frozen`; `uv run python scripts/build.py`; then
`uv run python scripts/site.py preview` (http://127.0.0.1:4200/).

For raw-data reconstruction use `uv run python scripts/build.py --prepare`;
missing DANE originals are fetched only if their pinned hashes match. For a
deliberate new snapshot follow `docs/sources.md`, retain previous bytes/manifests,
inspect numerical and definition changes, and repeat release checks.

## Hosted publication

Pending initial repository publication and hosted verification.
