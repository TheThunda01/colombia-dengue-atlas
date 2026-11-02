# PAHO source assessment

Assessed 2 November 2026. PAHO is a contextual comparison source for this release; no PAHO observations are mixed into the atlas data.

## Official resources inspected

- Pan American Health Organization (PAHO), [Dengue indicators, PLISA](https://opendata.paho.org/en/dengue-indicators). The page describes weekly national reporting by 46 countries and territories. Its legacy subnational navigation does **not** list Colombia, but this is not evidence that newer PAHO resources lack Colombia subnational data.
- PAHO, [ARBO Portal](https://www.paho.org/en/arbo-portal). The portal explicitly describes the data as preliminary and subject to increases and decreases during national validation. It says information is supplied by national ministries and updated daily from official government sources.
- PAHO, [Colombia country profile](https://www.paho.org/en/arbo-portal/countries/colombia-country-profile). The public page embeds [the Colombia dashboard wrapper](https://ais.paho.org/ArboPortal/DENG/1030_DENG_COL_Indicadores.asp), which opens Tableau workbook `1030`, published view `Resumen`. The wrapper supplies a temporary public-view ticket; it is not a stable download URL.
- PAHO, [Dengue data and analysis](https://www.paho.org/en/arbo-portal/dengue-data-and-analysis), linking the regional dashboard.

## Representative data actually inspected

A read-only request to the Colombia wrapper and its public Tableau session returned visible aggregate tables. No person-level records were requested. The following are inspected fields and snapshot dimensions, not a claim that all possible filters or full underlying data have been validated:

| Visible worksheet | Extract inspected | Important limitations |
|---|---|---|
| `W Epi Curve` | 668 rows; epidemiological week, year, `SUM(New Suspected Cases)`; years 2014–2026 | National series. The snapshot includes 2026, an incomplete year. A week 53 value is present in 2014. The publisher's epidemiological-week convention must be preserved rather than inferred to be ISO weeks. |
| `W Resumen` | 104 rows in long indicator form; year, serotypes, measure name, measure value; years 2014–2026 | Multiple measures are not additive categories. National year summaries can differ from other snapshots because of revisions. |
| `W M Casos DEPT` | 32 visible rows; department name, total cases, generated coordinates, incidence per 100,000 | Current-year map values, not a verified historical department panel. Geographic denominators, district inclusion, and year selection were not established. These rates must not be treated as DANE total-population rates. |
| `SE_Actualizada` | One row: 2026, epidemiological week 41 | Latest reported week in that snapshot; not a field-completeness indicator or a guarantee every department reports through that week. |

A generic Tableau CSV URL exported only the dashboard's first worksheet (the latest-week indicator). It is therefore **not** a complete dataset download. Requests for nonpublished sheet URLs returned 404. Visible aggregate extraction used `tableauscraper` through the public session, with Windows system certificate trust enabled using `truststore`. This was an exploratory check, not a production dependency or a stable API contract.

## Definitions and comparability

The inspected weekly field is explicitly named **New Suspected Cases**. It must not be relabeled as laboratory-confirmed dengue. The public portal text does not by itself resolve symptom-onset versus notification date, residence versus reporting geography, department/district relationships, or denominator vintage for this workbook. Those unresolved details prevent adopting the departmental map or its rates without additional documentation.

This release uses the separately documented INS aggregate source and a single pinned source snapshot. Combining PAHO national summaries or current maps with that INS panel could mix classification, date convention, geographic aggregation, and revision vintages. No reconciliation has been claimed. PAHO remains useful for contextual national comparisons if an explicit definition and revision crosswalk is added in a future release.

## Access and terms

For a manual download, open the Colombia country profile, wait for its embedded dashboard, select the desired visible chart, and use Tableau's **Download → Data/Crosstab** option. Record the selected chart, year/week/territory filters, download date, and all source notes. Each view must be checked; a dashboard-level CSV can contain only the first worksheet.

The [PLISA page](https://opendata.paho.org/en/dengue-indicators) footer states **CC BY-NC 3.0 IGO**, except where otherwise indicated, and notes that individual resources may have other licenses. The [PAHO terms](https://www.paho.org/en/terms-and-conditions-use-site) also prohibit suggesting PAHO endorsement or affiliation. This assessment does not presume that every ARBO dashboard export has the same license as the legacy page. PAHO observation files and dashboard assets are not redistributed in this repository.

Raw exploratory HTML, aggregate CSV extracts, and extraction notes remain in the local workspace at `Workspace/colombia-atlas-source-research/paho`, outside the repository. They are not part of the atlas's reproducible production inputs. The published release source register identifies the actual included datasets.
