# The question and the reasoning

The starting question is straightforward: **where and when were dengue cases
recorded in Colombia during 2019–2022, and what do we need to know before
comparing those records?** A useful answer needs more than a colored map. It
needs the source definition, the population denominator, and an honest account
of what is absent from the extract.

This atlas is a portfolio demonstration for readers learning spatial surveillance
analysis. It connects data preparation, scientific communication, and software
verification. Its intended result is an inspectable descriptive comparison, not
an estimate of all infections or an operational outbreak warning.

## Why these sources and this period?

The INS public aggregate dataset provides municipality, event, year, week, and
count fields in one downloadable historical snapshot. The selected years have
elapsed, which avoids presenting an unfinished calendar year as a full-year
comparison. That choice does **not** establish complete reporting. DANE provides
the department codes, reference geography, and annual total-population values.

We investigated PAHO as well, but did not combine its observations with INS.
The unresolved differences in definitions, denominators, and timing would make
a combined series harder to interpret. The
[source assessment](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/paho-source-assessment.md)
records that decision and the evidence available at the time.

## Decisions you should be able to explain

| Decision | Reasoning | What the reader sees |
| --- | --- | --- |
| Keep events 210 and 220 separate | The source supplies distinct categories; the extract does not establish person-level overlap. | An explicit event selector, with no claimed deduplicated combined total. |
| Retain absent cells as null | No published row is not evidence of a reported zero. | Hatched polygons, gaps, blank CSV values, and source-row availability counts. |
| Use code-based department joins | Names vary, and districts can be counted twice if separate totals are added. | One row per department/year, with districts included once through their source parent code. |
| Show counts with circle area | The quantity is a count; a large land area should not itself imply a larger count. | A map paired with numerical ranking and directly labeled example circles. |
| Use a fixed color scale for normalized values | Changing the scale at each selection can make the same color mean different quantities. | One scale per event across 2019–2022 and a shared scale across all four static maps. |
| Publish a static website | The pinned data fit in browser assets, and the core interactions need no live computation service. | Shareable selections, local CSV downloads, and a reproducible GitHub Pages build. |
| Add Inkscape to figure export | Editable vector artwork and high-resolution exports make figures easier to reuse. | SVG, PNG, and PDF files tied to the same generated values. |

The count-symbol scale still adapts to the selected period so small counts remain
visible. Its legend says so. Use the numerical values when comparing count maps
from separate selections. The fixed rate scale answers a different need: a color
has the same numerical meaning within the selected event throughout this release.

## What this project can and cannot establish

The atlas can show differences in the **available recorded observations** and
expose the transformations behind them. It cannot separate changes in disease
occurrence from changes in detection, reporting, classification, or revisions.
The source does not resolve onset versus notification week assignment. Its
occurrence/procedence geography is not a verified resident-only numerator.

Dividing by total residents makes a descriptive normalized count. It does not
produce official population-at-risk incidence or an individual infection
probability. Software checks establish that the views and exports agree with
the pinned inputs; they do not validate surveillance sensitivity or causal claims.

## A sensible reading order

Start with the
[surveillance concepts](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/biology-and-concepts.md)
and [glossary](https://thethunda01.github.io/colombia-dengue-atlas/glossary.html).
Then try the
[worked example](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/practical-use.md)
in the explorer. Read the methods when you want the calculation details, and
the [annotated build guide](https://thethunda01.github.io/colombia-dengue-atlas/build-guide.html)
when you want to follow the code from source files to the published site.

The [software guide](https://thethunda01.github.io/colombia-dengue-atlas/tools.html)
explains the free tools, including where Blender or QGIS could help a future
extension. The reasoning here describes project choices; the methods and source
assessments hold the underlying data definitions and evidence.
