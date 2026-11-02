# Reference audit

Audit date: **2 November 2026**. This audit checks whether project claims have appropriate source evidence; it is not a systematic literature review or independent validation of the surveillance system.

| Claim or resource | Evidence and status |
|---|---|
| INS source, fields, years, license, revisions | The API metadata, original aggregate responses, and exact queries are recorded in [INS source assessment](ins-source.md) and `data/raw/ins_manifest.json`. Metadata identifies CC BY-SA 4.0. |
| Counts and missingness | All 13,794 published cells were independently recomputed from the 57,083 original rows. No raw explicit zeros occur. Evidence: [independent review](../reports/independent_scientific_review.md). |
| District containment | Raw municipality/department codes establish the five documented district-parent relationships. No separately published district total is added to the municipality sum. |
| DANE population and geometry | Workbook, technical note, service metadata, fingerprints, versions, and transformations are documented in [DANE source assessment](dane-source.md). National population totals shown there are sums of department rows, not a separate national-series validation. |
| DANE reuse terms | Statistical terms were retrieved directly. Geographic license text was verified through the official-page search index; direct geoportal access timed out. This distinction is preserved. |
| PAHO feasibility | Official pages and representative public dashboard aggregates were inspected. [PAHO assessment](paho-source-assessment.md) records unresolved denominator/date/district semantics and excludes these observations from the atlas. |
| Underlying date basis and clinical confirmation | **Unresolved at record level.** Neither onset-date assignment nor universal laboratory confirmation is asserted. |

Dataset citations remain separate from the software citation and MIT code license. No institutional logo or claim of endorsement is used. The limited [search log](search-log.json) records actual PAHO/source-feasibility searches; it is not an exhaustive project retrieval log.

## Visualization and teaching update

The [free software guide](visualization-tools.md) records official licensing and
capability sources checked on 2 November 2026. Inkscape 1.4.4 and Blender 5.2.3 LTS
were queried locally for their version; only Inkscape was used to export the new
figure. QGIS and ParaView are evaluated options, not claimed production steps.
The build guide's Antioquia 2019 example was run against the committed model:
4,980 recorded cases / 6,518,070 residents × 100,000 = 76.4029843, with 52/52 source
week cells present. This is a calculation check, not evidence of complete capture.
