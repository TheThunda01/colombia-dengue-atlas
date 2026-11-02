# INS surveillance source and extraction

The release uses the Instituto Nacional de Salud (INS) dataset [Datos de Vigilancia
en Salud Pública de Colombia](https://www.datos.gov.co/d/4hyg-wa9d), dataset ID
`4hyg-wa9d`, hosted by Colombia's National Open Data Portal. Its
[machine-readable metadata](https://www.datos.gov.co/api/views/4hyg-wa9d.json)
identifies INS as producer, an annual update frequency, and **CC BY-SA 4.0**
(`CC_40_BY_SA`). The recorded data update is **17 October 2024, 23:35:37 UTC**;
the atlas retrieved its snapshot on **2 November 2026**. These are distinct dates.
The source has no separate numbered release; dataset ID, data-update timestamp,
exact queries, and SHA-256 fingerprints identify this version.

Suggested citation: Instituto Nacional de Salud (INS), Bogotá D.C. *Datos de
Vigilancia en Salud Pública de Colombia*. National Open Data Portal, dataset
4hyg-wa9d. Data updated 17 October 2024; retrieved 2 November 2026.
https://www.datos.gov.co/d/4hyg-wa9d. CC BY-SA 4.0.

Source attribution for reuse: **Fuente: Portal de Datos Abiertos www.datos.gov.co;
Instituto Nacional de Salud (INS), Bogotá D.C.** This atlas filters and aggregates
the source; it is an independent work and is not endorsed by INS. Adapted surveillance
data retain [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Original project code has its separate repository license. The open-data portal
[terms](https://herramientas.datos.gov.co/terminos) permit reuse and transformation,
require source credit, and require preserving update/usage metadata.

## Selected observations and definitions

The source covers 2007–2022. This release selects 2019–2022 and event codes **210
(DENGUE)** and **220 (DENGUE GRAVE)**. A downloaded row is a municipality × source
epidemiological week × year × event aggregate, not a person record. The source
contains `conteo`, a count for that row's week. The atlas sums these weekly counts;
it does not take differences of cumulative bulletins.

The INS [routine-surveillance notes](https://portalsivigila.ins.gov.co/Paginas/Vigilancia-Rutinaria.aspx)
describe cases reported as confirmed and geographic assignment by occurrence or
procedence. That statement does **not** establish laboratory confirmation for each
record. The aggregate API does not contain confirmation type, clinical warning-sign
classification, onset date, notification date, or person identifiers. The atlas
therefore labels the categories with their INS event codes, keeps them separate,
and does not claim that their sum has undergone person-level de-duplication.
Mortality event 580 is excluded; adding it to a case total would risk overlap.

The same notes warn that surveillance data are revised and must be interpreted
with their reporting context. Occurrence/procedence is not the reporting office
and is not necessarily residence. No residence-based disease risk is estimated.

The API explicitly describes epidemiological week and year but does not document
whether its `semana` values were derived from notification or symptom-onset dates.
The atlas preserves source week labels and states this unresolved date basis.
It does not relabel the series as symptom-onset incidence or silently convert
epidemiological weeks to ISO weeks or calendar months. The source contains 52
weeks in 2019, 2021, and 2022, and 53 in 2020. Week 53 is retained only for 2020;
other years have no artificial week-53 zero. The four years have elapsed completely,
which does not imply complete case ascertainment or reporting.

## Geography and missing values

Source department identifiers are normalized to two-character DANE codes; the
source municipality identifier is the full five-character DANE code after padding.
For example, numeric `8001` becomes `08001`, not `008001`. All mapped municipality
prefixes agree with the corresponding department code.

| Municipality | District | Parent department in the source |
|---|---|---|
| 08001 | Barranquilla | 08 Atlántico |
| 13001 | Cartagena | 13 Bolívar |
| 47001 | Santa Marta (source spelling: SANTA MARTHA) | 47 Magdalena |
| 76001 | Cali | 76 Valle del Cauca |
| 76109 | Buenaventura | 76 Valle del Cauca |

These municipalities are already ordinary rows under their parent departments.
They are counted once during the municipal-to-department sum; no district total
is added afterward. The atlas includes 32 department polygons and Bogotá D.C.
(code 11). Bogotá has no selected-event observations in this snapshot and remains
an explicit no-data unit. Code 00 (unknown procedence) and 01 (foreign origin) are
not mapped to Colombia's departments. Their excluded counts remain in the audit.

The selected raw data contain 57,083 rows, all with positive integer counts and
no duplicate municipality/week/year/event keys. There are **no explicit zero
rows**. A department-week-event without a source row is kept as JSON `null` and
an empty CSV field with `observation_status=source_absent`. This is an absence in
a sparse published extract; it is not proof of zero cases, a missed report, or an
unreported outbreak. A positive department-week sum likewise does not establish
that every municipality reported. Counts of available cells describe **data
availability**, never reporting completeness.

## Verified totals and excluded geography

These are sums of the published observations, without imputing absent cells.

| Year | Mapped event 210 | Mapped event 220 | Foreign 210 / 220 | Unknown 210 / 220 |
|---|---:|---:|---:|---:|
| 2019 | 122,992 | 1,339 | 643 / 9 | 6 / 0 |
| 2020 | 76,220 | 860 | 199 / 2 | 0 / 0 |
| 2021 | 49,174 | 932 | 151 / 8 | 0 / 0 |
| 2022 | 65,428 | 1,330 | 263 / 10 | 0 / 0 |

The generated grid contains 33 geographic units × 209 epidemiological weeks ×
2 events = **13,794 cells**: 8,130 observed positive sums and 5,664 absent cells.
Every one of the **8,358** present source department/week/event sums (including
foreign and unknown geography) agrees with a separately requested, server-side
Socrata group-by query, as do the constituent row counts. This validates the
aggregation against the downloaded source snapshot, not the accuracy or
completeness of surveillance itself.

The initial source investigation also inspected INS routine XLSX files locally.
Those files were **not published or used to fill gaps**: the general INS site
terms differ from the explicit open-data dataset license, and snapshots differ.
For example, the 2021 routine workbook's event-210 department total is 52,228,
whereas the selected licensed API has 49,174 mapped cases. The reason for the
difference is not documented in the sources examined. Mixing versions would
conceal that uncertainty. The release consistently uses the licensed API snapshot.

## Files and reproducible commands

The original HTTP response bytes are in `data/raw/ins_dengue_2019.json` through
`ins_dengue_2022.json`, with API metadata and the independent aggregate response.
`data/raw/ins_manifest.json` records every query, retrieval time, byte count, and
SHA-256. They are public aggregate data, contain no person-level fields, and are
redistributed under the source license. All source queries are capped at 50,000
rows; each response is below that limit, and the pipeline fails at the limit so a
future larger result cannot be silently truncated.

From the repository root:

```powershell
uv run python scripts/prepare_surveillance.py
```

This offline command verifies fingerprints and identifiers, independently checks
source sums, and writes `data/processed/surveillance_weekly.csv`, the matching
JSON array, and `surveillance_audit.json`. It fails on mismatches rather than
silently adjusting observations.

To retrieve a **candidate** refresh into a new directory:

```powershell
uv run python scripts/prepare_surveillance.py --fetch-to data/candidates/ins-2026-11-03
uv run python scripts/prepare_surveillance.py --raw-dir data/candidates/ins-2026-11-03 --output-dir data/candidates/ins-2026-11-03/processed
```

Choose a new date/name. The destination must not exist. Review the new license,
metadata, annual/event/district totals, omissions, and API validation before adopting
it. Preserve the prior snapshot and audit in version history; deliberately replace
the pinned inputs only after that review, rebuild the whole project, and rerun
release checks. Refreshing the dataset does not automatically expand the fixed
2019–2022 analysis window.

## Output data dictionary

| Field | Meaning |
|---|---|
| `year` | Source epidemiological year, 2019–2022 |
| `week` | Source epidemiological week, 1–52 or 1–53 in 2020 |
| `department_code` | Two-character DANE department/Bogotá code |
| `department_name` | Readable standardized label; raw names are preserved in inputs |
| `event_code` | INS category 210 or 220; retain as text |
| `event_name` | Dengue or Severe dengue; categories are displayed separately |
| `cases` | Sum of source `conteo` in this cell, integer or missing |
| `observation_status` | `observed_positive`, `explicit_zero`, or `source_absent`; no explicit zeros occur in the release source |
| `source_rows` | Number of municipal source rows summed, not expected-report denominator |
| `source_id` | `ins-socrata-4hyg-wa9d` |

The surveillance preparation step supplies no denominator. Population matching
and any normalization are separate documented transformations downstream.
