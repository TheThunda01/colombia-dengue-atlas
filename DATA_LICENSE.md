# Source-data licenses and attribution

The project's MIT software license does not replace source-data terms. Preserve
the following attribution, source links, update dates, and transformation notes
when reusing data, exported tables, or figures from this atlas. The project is
independent of INS, DANE, and PAHO and does not imply their endorsement.

| Data component | Terms | Scope in this release |
|---|---|---|
| INS surveillance aggregates | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | Original selected aggregate responses, derived surveillance counts, and their adaptations |
| DANE population estimates | [DANE statistical portal terms](https://www.dane.gov.co/index.php/terrminos-y-condiciones-dane) | Department-year population values and their attributed transformations |
| DANE department geometry | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) under [DANE geographic terms](https://geoportal.dane.gov.co/acerca-del-geoportal/licencia-y-condiciones-de-uso/) | MGN2025 boundaries and simplified display geometry |

## INS surveillance data

**Source:** Instituto Nacional de Salud (INS), Bogotá D.C. *Datos de Vigilancia
en Salud Pública de Colombia*, National Open Data Portal dataset
[`4hyg-wa9d`](https://www.datos.gov.co/d/4hyg-wa9d).
[Dataset metadata](https://www.datos.gov.co/api/views/4hyg-wa9d.json) identifies
the license as `CC_40_BY_SA`. The recorded data update is 17 October 2024;
the release snapshot was retrieved 2 November 2026.

Attribution: **Fuente: Portal de Datos Abiertos www.datos.gov.co; Instituto
Nacional de Salud (INS), Bogotá D.C.**

Changes made by this atlas: selection of years 2019–2022 and events 210/220,
normalization of identifiers, municipal-to-department aggregation, explicit
representation of absent cells, exclusion of foreign/unknown geography from
the mapped comparison, and preparation of browser/download summaries.
INS-derived surveillance adaptations retain CC BY-SA 4.0. See the linked
license for attribution, indication-of-changes, and share-alike requirements.
The same conditions apply to the surveillance content of combined tables or
visualizations; associated DANE material retains its own required attribution.

Only aggregate municipality/week/event observations are included. Person-level
records were not used. Other INS site content or differently licensed downloads
are not covered by this dataset's license.

## DANE population values

**Source:** DANE. *Proyecciones de Población y Estudios Demográficos (PPED):
Serie departamental de población por área, 2018–2050*, CNPV 2018 basis,
2025 revision. [Official source page](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion).
The page dates the workbook 8 August 2025; the workbook records an update of
30 July 2025. Retrieved 2 November 2026.

Required attribution: **Fuente: Departamento Administrativo Nacional de
Estadística: www.dane.gov.co**.

DANE's terms authorize use, transformation, and analysis with this credit.
The atlas selects the Total population rows for 2019–2022 and renames fields;
it does not claim that the resulting rates are DANE or INS official incidence.
No Creative Commons license is inferred for the statistical workbook merely
because DANE's separate geographic portal uses one.

## DANE geography

**Source:** DANE. *MGN2025_DPTO_POLITICO*, official ArcGIS catalog item
[`7023d9d31e834840a9136ccaa6426432`](https://www.arcgis.com/home/item.html?id=7023d9d31e834840a9136ccaa6426432),
owner `adm_cdge_hub`. Item modified 28 May 2026; retrieved 2 November 2026.
Feature update years 2024 and 2025 are retained in the output metadata.

Attribution: **Departamento Administrativo Nacional de Estadística - DANE:
www.dane.gov.co**. Licensed under CC BY 4.0 according to the DANE geographic
portal's general conditions; the ArcGIS item has no separate populated license
field. These conditions were verified in the official page's search-index
content; direct page retrieval timed out, as recorded in the source assessment.

Changes: reprojection to EPSG:9377, per-feature topology-preserving simplification
at 500 metres, reprojection to EPSG:4326, and field selection/renaming. This is
display geometry, not a legal boundary product or annual historical reconstruction.

## Other materials

PAHO resources were assessed, but PAHO observation files and dashboard assets
are not redistributed. Third-party plotting and website libraries retain their
own licenses. The atlas's source manifests preserve exact download URLs and
fingerprints; source organizations may publish later revisions under the same
URL. Review the applicable terms when deliberately refreshing a snapshot.
