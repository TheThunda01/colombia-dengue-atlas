# Source register and deliberate refresh

Retrieval date for this release: **2 November 2026**. Source dates and retrieval
dates are separate. All observations are public aggregate counts; no person-level
surveillance records were downloaded or published for this atlas.

|Source|Selected release and contents|Units and coverage|Terms and provenance|
|---|---|---|---|
|Instituto Nacional de Salud, *Datos de Vigilancia en Salud Pública de Colombia*, dataset 4hyg-wa9d|Data last updated 17 October 2024; selected 2019–2022, events 210 and 220|Municipality/event/epidemiological-week counts; original dataset 2007–2022; department rollups use source DANE identifiers|CC BY-SA 4.0. Original filtered API bytes, metadata, independent query, URLs and hashes in `data/raw/ins_manifest.json`; [detailed assessment](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/ins-source.md)|
|DANE, *PPED: Serie departamental de población por área, 2018–2050*, CNPV2018, 2025 revision|Page release 8 August 2025; workbook update 30 July 2025; selected 2019–2022 Total rows|Persons, department/year; 132 selected denominators incl Bogotá|Attribution required. Exact workbook URL and SHA-256 in `data/dane_sources.json`; [detailed assessment](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/dane-source.md)|
|DANE, *MGN2025_DPTO_POLITICO*, item 7023d9d31e834840a9136ccaa6426432|Item modified 28 May 2026; features updated 2024–2025|33 department-level polygons; fixed display reference; simplified500m|CC BY4.0 geographic terms. Original raw local file; public derived GeoJSON and catalog metadata, manifest SHA-256; [detailed assessment](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/dane-source.md)|
|PAHO, *Colombia Country Profile*, ARBO Portal|Public Tableau exports inspected 2 November 2026|National weekly and annual indicators plus current subnational map|Investigated, not used as atlas observations. Definitions/revisions cannot safely be combined with INS; [assessment and access steps](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/paho-source-assessment.md)|

Official access points: [INS dataset and metadata](https://www.datos.gov.co/d/4hyg-wa9d),
[INS routine-data definitions](https://portalsivigila.ins.gov.co/Paginas/Vigilancia-Rutinaria.aspx),
[DANE projections](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion),
[DANE geographic catalog](https://www.arcgis.com/home/item.html?id=7023d9d31e834840a9136ccaa6426432),
[PAHO country profile](https://www.paho.org/en/arbo-portal/countries/colombia-country-profile).

## Exact reproduction

The repository commits the licensed, filtered INS source responses and all
processed data. DANE originals are preserved locally but excluded from Git to
keep the repository small. Their URLs and checksums are committed. The default
site build uses processed snapshots and makes no external data request.

```powershell
uv sync --frozen
uv run python scripts/prepare_geography.py --download
uv run python scripts/build.py --prepare
uv run pytest
node --test tests/model.test.mjs
```

`--download` fetches only missing pinned DANE inputs. A changed hash stops the
build. It does not bless current upstream bytes as equivalent. This preserves
scientific provenance if official URLs are updated in place.

## Refresh surveillance deliberately

```powershell
uv run python scripts/prepare_surveillance.py --fetch-to data/candidates/ins-YYYY-MM-DD
```

The destination must not exist. This creates a candidate snapshot and manifest,
leaving release inputs intact. Inspect changes to license, columns, event and
geographic codes, periods, missing-value behavior, excluded counts, annual totals,
and district assignments. Compare against the previous snapshot before replacing
the pinned source files on a new Git branch. Update retrieval metadata, tests of
pinned totals, citations, and release notes together. Never use a changed source
solely because its download succeeded. A script's hard-coded supported years and
weeks must be reviewed when extending the period.

For DANE, retrieve a new official workbook/layer into a dated candidate directory,
preserve the old manifest and originals, review geographic and population changes,
then explicitly update `data/dane_sources.json` and any transformation assumptions.
Rebuild and rerun data, browser, figure, and deployed-site checks. Do not substitute
an unofficial boundary mirror or bypass a failed fingerprint check.

## Citations and reuse

Credit INS for the underlying surveillance records and retain CC BY-SA 4.0 for
the derived surveillance data and data-bearing exports. Credit DANE as
**Fuente: Departamento Administrativo Nacional de Estadística: www.dane.gov.co**.
Geographic modifications comprise field selection, projection and simplification.
The original code is MIT licensed; that license does not relicense source data.
See `DATA_LICENSE.md`, `CITATION.cff`, and source-specific assessments.

The source investigation is a focused official-data feasibility review, not a
systematic literature review. The geographic terms page timed out on direct
access; its official indexed contents were inspected and this limitation is
recorded in the DANE assessment.
