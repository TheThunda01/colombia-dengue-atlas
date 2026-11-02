# Colombia Dengue Surveillance Atlas

**Brandon Huynh** · A reproducible atlas of reported dengue surveillance observations
in Colombia, 2019–2022.

Repository: [TheThunda01/colombia-dengue-atlas](https://github.com/TheThunda01/colombia-dengue-atlas)
· Live website:
[Colombia Dengue Surveillance Atlas](https://thethunda01.github.io/colombia-dengue-atlas/).
Published and checked on 2 November 2026. See the [release report](RELEASE_REPORT.md)
for hosted build, data, and browser verification evidence.

## Why this project

Reported case counts describe a surveillance system as well as a disease. This
atlas helps researchers, students, and public health readers compare Colombian
departments while seeing the source, geographic definitions, missing observations,
and population denominator behind each view.

Within [From biological measurements to better experiments](https://github.com/TheThunda01/TheThunda01/blob/main/PROJECT_GUIDE.md),
this project demonstrates spatial data preparation and evidence-aware scientific
visualization. It is a separate surveillance workflow, not an integrated pipeline
with the portfolio's molecular or experimental projects.

## What it does

- Coordinates geographic, year, epidemiological-week, event, and metric selections
  across a department map, weekly series, seasonal comparison, and summary table.
- Keeps INS event **210 (dengue)** and **220 (severe dengue)** separate, with an
  explicit reset and visible selection summary.
- Shows source-row availability and distinguishes missing cells from reported
  zeros; Bogotá remains selectable even though it has no selected-event records.
- Downloads the current summary with identifiers, units, source metadata, and
  denominator information. Available normalization is **reported cases per
  100,000 total population**, not official incidence per population at risk.
- Runs entirely as a static Quarto website. Python prepares aggregates and an
  exported figure; browser JavaScript supplies linked interactions without a
  running Python service or paid map provider.

The source is INS's licensed aggregate dataset `4hyg-wa9d`, using 2019–2022;
DANE supplies 132 department-year population values and 33 reference map units
(32 departments plus Bogotá D.C.). PAHO was investigated and documented but its
observations are not mixed into this release.

## Quick start

Install **Python 3.12**, **uv 0.11.15**, **Quarto 1.9.37**, and **Node.js 24**. The Python dependency
versions are locked in `uv.lock`; use the project environment for every command.
From the repository root:

```powershell
uv sync --frozen --system-certs
uv run python scripts/build.py
uv run python scripts/site.py preview
```

The build writes `site/_site/index.html`, the website's supporting assets, and
`figures/weekly-comparison.svg` plus `figures/weekly-comparison.png`. The preview
command serves http://127.0.0.1:4200/. Use that server for browser interactions;
opening the HTML directly with a `file:` URL can prevent data loading.

To recalculate processed data from pinned original inputs:

```powershell
uv run python scripts/prepare_geography.py --download
uv run python scripts/build.py --prepare
```

The first command downloads missing DANE inputs and rejects changed source
fingerprints; it never silently replaces an existing snapshot. See
[source retrieval and refresh](docs/sources.md) before adopting newer data.

## Example results

The licensed INS snapshot contains **57,083 municipal week/event aggregate rows**.
After excluding foreign and unknown origin from the department map, the sums of
published dengue event-210 observations are **122,992 (2019), 76,220 (2020),
49,174 (2021), and 65,428 (2022)**. These are snapshot-specific sums, not estimates
of all infections or proof that every municipality reported.

![Desktop atlas](docs/screenshots/desktop.png)

<details>
<summary>Narrow-screen view</summary>

![Narrow-screen atlas](docs/screenshots/mobile.png)

</details>

Inspect the reproducible [vector figure](figures/weekly-comparison.svg) or its
[PNG export](figures/weekly-comparison.png), the
[weekly surveillance table](data/processed/surveillance_weekly.csv), and the
[DANE population table](data/processed/population.csv). Figure exports and browser
views describe the same pinned input release.

## Practical use and limitations

Choose an event, department, and comparable set of source weeks; inspect the
availability counts before comparing years. Download the table to preserve the
selection and its interpretation. Occurrence/procedence geography is not
necessarily residence, and the API does not establish whether weeks derive from
notification or symptom onset. The atlas preserves the source week labels,
including week 53 in 2020, rather than relabeling them as calendar dates.

All four years have elapsed, but surveillance capture is not established as complete and is subject
to revisions. Absent rows remain missing. The mapped department sums exclude
foreign and unknown procedence, which remain in the audit. Fixed MGN2025 display
boundaries are not a reconstruction of historical boundaries. The atlas supports
descriptive comparison and source inspection; it does not estimate causal
effects, forecast outbreaks, or determine individual clinical risk.

Three decisions worth being able to explain:

1. **Absence is not zero.** The sparse source has no explicit zero rows. Filling
   its absent cells with zeros would manufacture observations and conceal the
   distinction between an observed count and unavailable data.
2. **The denominator changes the question.** Dividing by DANE total population
   permits a population-normalized descriptive comparison. It does not reproduce
   INS incidence based on the population at risk, and occurrence-based counts
   do not establish resident infection risk. Districts must be included exactly
   once in their parent department before that division.
3. **A static release can remain interactive and reproducible.** Pinned original
   responses and checked Python transformations produce small browser assets.
   Shared JavaScript calculations make charts and CSV downloads agree, while
   avoiding a live server and uncontrolled source changes during viewing.

## Documentation

- [Methods and interpretation](docs/methods.md)
- [Source register, retrieval, and deliberate refresh](docs/sources.md)
- [INS definitions, district rollups, validation, and data dictionary](docs/ins-source.md)
- [DANE denominators, map processing, and terms](docs/dane-source.md)
- [PAHO source assessment and remaining comparability questions](docs/paho-source-assessment.md)
- [Interface design and inspection criteria](docs/design.md)
- [Practical use and worked example](docs/practical-use.md)
- [Data dictionary](docs/data-dictionary.md), [glossary](docs/glossary.md), and [assumption register](docs/assumptions.md)
- [Focused source review](docs/literature-review.md), [search log](docs/search-log.json), and [reference audit](docs/reference-audit.md)
- [Dated corrections](docs/corrections-2026-11-02.md) and [release validation](RELEASE_REPORT.md)
- [Geography validation evidence](reports/geography_validation.json)
- [Data reuse terms](DATA_LICENSE.md) and [software citation](CITATION.cff)

## Development and reuse

```powershell
uv run pytest
node --test tests/model.test.mjs
uv run python scripts/browser_checks.py --url https://thethunda01.github.io/colombia-dengue-atlas/
```

For local browser checks, replace the URL with the address printed by the preview
command. Install the browser-check runtime if needed with
`uv run playwright install chromium`, then pass `--channel chromium`. On Windows,
the default uses an installed Microsoft Edge browser (`--channel msedge`). The checks address data invariants,
filter/download agreement, and rendered interactions. Their success does not
establish complete case ascertainment or validate epidemiological interpretation.

Original code is [MIT licensed](LICENSE). INS-derived surveillance data retain
**CC BY-SA 4.0**; DANE population values and geometry have separate attribution
requirements described in [DATA_LICENSE.md](DATA_LICENSE.md). Do not apply the
code license to third-party data. Cite the software using [CITATION.cff](CITATION.cff)
and retain the underlying dataset citations. See [CONTRIBUTING.md](CONTRIBUTING.md)
for source-refresh and review expectations.
