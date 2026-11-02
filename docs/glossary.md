# Glossary

| Term | Meaning in this atlas |
|---|---|
| Recorded cases | Counts published in the selected INS aggregate snapshot; not an estimate of all infections. |
| Event 210 / 220 | INS dengue / severe-dengue categories, displayed separately. Their sum is not presented as a deduplicated clinical total. |
| Epidemiological week | The source's week label. The extract does not resolve onset versus notification assignment; these labels are not converted to ISO weeks. |
| Occurrence / procedence | The source's geographic assignment, which is not necessarily residence or the reporting facility. |
| Department-level unit | One of Colombia's 32 departments or separately coded Bogotá D.C. |
| District rollup | Inclusion of municipality records such as Barranquilla within their source parent department, exactly once. |
| Source-present cell | A department/week/event combination with at least one published source row. Presence does not prove complete municipal reporting. |
| Source-absent cell | A combination with no published row, stored as null and exported as blank. It is not an explicit zero. |
| Explicit zero | A published numeric count of zero. None occurs in this release's original INS rows; software preserves the distinction. |
| Total-population normalization | Available cases divided by the matching annual DANE total resident population, multiplied by 100,000. It is not official population-at-risk incidence. |
| Mean yearly rate | The arithmetic mean of selected-week normalized counts across selected years, requiring a usable value for each year. Restricted weeks are not annualized. |
| Snapshot | Source bytes tied to retrieval metadata and SHA-256 fingerprints. Retrieval date and source update date are distinct. |
| Choropleth | A map that fills each geographic unit with a color representing its value. This atlas uses one for population-normalized counts. |
| Proportional circles | Symbols whose **area**, not radius, represents a count; the radius therefore scales with the square root of the value. |
| Shared or fixed scale | A numeric range that keeps the same visual meaning across specified panels or selections. Here the interactive rate domain is fixed per event; the four-year plate has a shared domain across its panels. |
| Sequential palette | Colors that progress from lighter to darker as a nonnegative value increases. Hatching is separate from the numeric palette. |
| Projection / CRS | The coordinate system used to place geographic features on a flat map. The atlas draws in EPSG:9377 and distributes GeoJSON in EPSG:4326. |
| SVG / vector artwork | A graphic made from paths, text, and shapes that can be edited and enlarged without pixelating its geometry. |
| PNG / raster image | A fixed pixel grid. Its exported resolution matters when printing or enlarging it. |
| Static website | Prebuilt files served to a browser; JavaScript can still provide interactive filtering without a running Python service. |

See the [data dictionary](data-dictionary.md) for field-level definitions.
