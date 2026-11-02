# DANE population and geographic sources

Retrieval date: **2 November 2026**. Original bytes are retained locally under
`data/raw/dane/`; the public repository includes the derived aggregates, small
catalog metadata snapshots, and the exact URLs, sizes and SHA-256 fingerprints
in `data/dane_sources.json`.

## Population denominator

**Citation:** Departamento Administrativo Nacional de Estadística (DANE).
*Proyecciones de Población y Estudios Demográficos (PPED): Serie departamental
de población por área, 2018–2050*. CNPV 2018 basis; 2025 revision.
[Official source page](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion),
[original Excel workbook](https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Departamental/PPED-AreaDep-2018-2050_VP.xlsx),
[July 2025 technical note](https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Nacional/NotaTecnica-PPED-jul2025.pdf).

The source page dates this workbook **8 August 2025**; the workbook itself says
**updated 30 July 2025**. These are recorded separately. The 2025 revision uses
an adapted multiregional cohort-component approach and updated demographic
assumptions. Historical estimates can change when DANE revises its series;
this atlas holds one revision fixed across every displayed year.

The inspected workbook has sheets `Índice`, `PPED`, and `PobDepartamentalxÁrea`.
The data sheet's header is Excel row 8. Its fields are `DP` (two-character DANE
department code), `DPNOM` (department name), `AÑO` (year), `ÁREA GEOGRÁFICA`
(area category), and `TOTAL` (persons). Available years are 2018–2050. Each
unit/year has separate municipal-seat and rural-area rows plus a **Total** row.
The pipeline selects **only Total**, avoiding a doubled denominator.

For this release, 2019–2022 yield **132 positive, nonmissing denominators**:
32 departments plus Bogotá D.C., independently coded `11`. Units are the
total resident population in persons, including separately administered
districts within the corresponding departments. Bogotá is excluded from
Cundinamarca. Barranquilla belongs to Atlántico (`08`), Cartagena to Bolívar
(`13`), Santa Marta to Magdalena (`47`), and Cali and Buenaventura to Valle del
Cauca (`76`). The surveillance preparation must verify district coding and
make these rollups exactly once before joining denominators.

The national sums of the selected department rows are 49,266,526 (2019),
50,390,790 (2020), 51,115,637 (2021), and 51,643,565 (2022). These are sums of
the department workbook, not a separate independently verified national series.

The rate is **reported cases per 100,000 total population**:
`reported_cases / population * 100000`. It is descriptive normalization, not
INS incidence per population at risk, an estimate of infection probability,
or an age-standardized rate. Total population includes people outside dengue
transmission areas. An occurrence-based numerator also need not describe
resident-only risk. No uncertainty interval is invented for these denominators.

Source blank introductory/footer cells are not data. All selected Total rows
are numeric; the pipeline rejects missing or nonpositive denominators rather
than imputing them. No special missing-value sentinel was encountered in the
selected cells.

## Map geometry

**Citation:** DANE. *Marco Geoestadístico Nacional 2025: MGN2025_DPTO_POLITICO*.
Official DANE ArcGIS Hub item
[`7023d9d31e834840a9136ccaa6426432`](https://www.arcgis.com/home/item.html?id=7023d9d31e834840a9136ccaa6426432),
owned by `adm_cdge_hub`; hosted
[FeatureServer layer 0](https://services.arcgis.com/ioNRSZMYYlx0PUaB/arcgis/rest/services/MGN2025_DPTO_POLITICO/FeatureServer/0).
The item's last-modified timestamp was **28 May 2026, 01:25:28 UTC**. The
catalog describes it as the MGN2025 department layer for the address locator.
Its feature-level `dpto_nano` values are **2024 and 2025**; the layer's release
name and those feature update years are distinct and both are preserved.

The ArcGIS query requests all fields and all features with `where=1=1`,
`returnGeometry=true`, `outSR=4326`, and `f=geojson`. The original response has
**33 features**, **1,079,179 coordinates**, and no invalid or empty geometries.
`dpto_ccdgo` supplies the verified two-character joining identifier.
Bogotá is a separate feature. The downloadable geometry preserves all
33 units, including the archipelago; the small island polygons may be difficult
to see at a national scale, so the named selector and table remain essential.

For a usable static website, the pipeline reprojects to **EPSG:9377**
(MAGNA-SIRGAS 2018 / Origen-Nacional), simplifies each geometry at a
**500-metre** tolerance with `preserve_topology=True`, and returns it to
**EPSG:4326**. The output retains 14,492 coordinates and all 33 valid, nonempty
features. Per-feature topology preservation does not guarantee that adjacent
polygons remain a perfectly gap-free coverage; the geometry is for display
only. No area calculation, geographic overlay, or case allocation uses the
simplified boundaries.

These are **fixed 2025 reference boundaries**, not reconstructed boundaries
for each surveillance year. Joining uses geographic codes. The map should not
be interpreted as a legal boundary product or as evidence that historical
municipal limits never changed. Original DANE geoportal/portalgis endpoints
were investigated but returned TLS EOF/timeouts in this environment; the
official DANE ArcGIS-hosted service above supplied the inspected data.

## Reuse terms

The code's MIT license does not relicense these source datasets.

- DANE's [statistical portal terms](https://www.dane.gov.co/index.php/terrminos-y-condiciones-dane)
  authorize use, transformation and analysis with the required attribution:
  **“Fuente: Departamento Administrativo Nacional de Estadística: www.dane.gov.co”.**
  This release publishes derived aggregate values with that attribution.
- The DANE Geoportal's
  [geographic license and conditions](https://geoportal.dane.gov.co/acerca-del-geoportal/licencia-y-condiciones-de-uso/)
  identify **Creative Commons Attribution 4.0 (CC BY 4.0)** and permit technical
  modifications. The ArcGIS item has no separate populated license field.
  Attribution: **Departamento Administrativo Nacional de Estadística - DANE:
  www.dane.gov.co**. This project changed projection, simplified geometry, and
  selected/renamed fields; DANE does not endorse the atlas.

The statistical terms were retrieved directly. The official geographic terms
were verified in the web search index; direct access to that geoportal page
timed out. This access limitation is recorded rather than presented as a
successful direct page download.

## Reproduce and refresh

From the repository root:

```powershell
uv sync --frozen
uv run python scripts/prepare_geography.py --download
```

`--download` downloads **missing** pinned inputs, checks their fingerprints,
and never overwrites an existing source file. A source changed upstream fails
with an explicit error. The script writes `data/processed/population.csv`,
`data/processed/departments.geojson`, and `reports/geography_validation.json`.
Without `--download`, it rebuilds from the original local bytes.

To refresh deliberately, preserve the old raw directory and manifest in a dated
archive, retrieve and inspect the new official release in a different directory,
compare the years/codes/definitions/terms, and only then update the pinned
manifest and processing assumptions. Rerun data validation, review the numerical
diff, and rebuild the site and publication figure. A file's retrieval date is
not its release date.
