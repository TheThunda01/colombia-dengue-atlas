# Methods and interpretation

This release describes **recorded dengue surveillance counts in Colombia during
2019–2022**. It uses one pinned INS historical aggregate dataset, rather than
mixing weekly bulletin snapshots or treating current dashboard values as a
historical revision series. It is a descriptive research demonstration by Brandon
Huynh, not a clinical tool, outbreak alert, or estimate of all infections.

## Cases, location, and time

The INS dataset contains municipality × epidemiological week × year × event
counts. `conteo` is the count in that cell, not a running cumulative total.
The atlas sums those counts directly; it never differences cumulative reports.
Event **210 (Dengue)** and **220 (Severe dengue)** remain separate selections.
No mortality event is added, and no record-level overlap or deduplication claim
is made. The extract has no person-level case classification fields.

INS's routine-data notes describe confirmed notifications. This is not proof
of laboratory confirmation for each case; this release displays the recorded
event classification supplied by INS. See the [INS source assessment](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/ins-source.md).

The geographic fields refer to **occurrence/procedence**, not the reporting
facility or a verified resident-only numerator. The time fields are the source's
**epidemiological year and week**. Available metadata does not establish whether
week assignment is based on symptom onset or notification. Therefore the atlas
does not relabel it as either, and does not invent calendar dates.

The closed source periods contain 52 weeks in 2019, 53 in 2020, and 52 in each
of 2021 and 2022. Week 53 is retained only in 2020. A closed year does not prove
complete surveillance capture. The chosen data were last updated on 17 October
2024 and retrieved on 2 November 2026; they are not a live feed. Retrospective
revision can alter totals and comparability across downloads.

## One consistent geographic level

The panel has the 32 departments plus separately coded Bogotá D.C. (`11`),
which has no event 210 or 220 rows in the selected snapshot and remains missing.
The municipality codes already place Barranquilla within Atlántico, Cartagena
within Bolívar, Santa Marta within Magdalena, and Cali and Buenaventura within
Valle del Cauca. Their counts are included once by summing source rows with the
same department code. No separate district total is added. Bogotá is not folded
into Cundinamarca.

Foreign (`01`) and unknown (`00`) source geography are excluded from the mapped
panel and reported separately in the audit. The public panel is not the source's
entire national total. All joins use verified, zero-padded DANE department codes.
No spatial overlay allocates cases to polygons.

The map uses fixed DANE MGN2025 reference boundaries, with feature update years
2024–2025. Geometry is simplified at 500 metres in EPSG:9377, then stored as
EPSG:4326 GeoJSON. The SVG map projects it back to EPSG:9377. Simplification is
for display only and may introduce tiny shared-edge gaps. These are not annual
historical boundary reconstructions or legal boundary products.

## Missingness and source-row availability

The 57,083 original municipal aggregates contain **no explicit zero counts**.
The release builds a full 33-unit × 209-week × 2-event grid. It contains 8,130
positive department-week-event cells and **5,664 null cells with no source row**.
We cannot infer whether an absent row means zero, missing submission, omitted
classification, or another source convention.

Present counts are summed. A department/year with some absent weeks therefore
shows the **sum of available records**, alongside the number of present and
expected week cells. If every selected cell is absent, its count and rate are
null, not zero. Partial combined-department weekly sums receive orange open
markers in the timeline. Gaps in a single department are not connected by lines.

Availability is a check on this extract, **not reporting completeness**. There
is no denominator of expected reporting facilities or submissions in this source.
The all-departments view includes 33 units in the availability denominator;
Bogotá contributes no cases. A source-present department-week cell also does
not prove that every municipality reported.

## Population normalization

DANE's CNPV2018-based **2025 revision** supplies each department's total resident
population for each selected year. Only the workbook's `Total` area rows are
used; municipal-seat and rural rows are not added again. All 132 department-year
denominators are positive and present.

For department d, year y, and selected weeks W:

`normalized_count(d,y,W) = sum(available cases(d,y,W)) / total_population(d,y) × 100,000`

The annual summary table shows this value for each department-year. The
multiyear map uses the **arithmetic mean of the available yearly normalized
counts**, and returns no rate if any selected year lacks a usable numerator or
denominator. This gives each selected year equal weight. It is not a sum of
annual rates. If weeks are restricted, the same weeks are used in every year;
the result is **not annualized**. Week 53 is structurally available only in 2020,
so a week-53-only multiyear rate is unavailable unless the selected year is 2020.

These are **recorded cases per 100,000 total residents**, not official incidence
per population at risk, age-standardized rates, or infection probabilities.
Total population includes residents outside transmission areas, and an
occurrence-based numerator need not represent resident-only events. Missing
weekly records remain a limitation of the numerator. No uncertainty interval
is invented for counts or population estimates.

## Reading the coordinated views

The map and ranking show all department-level units for the chosen event,
years, and weeks. The geographic selection highlights one unit and focuses
the timeline, seasonal comparison, availability summary, and downloads. This
retains geographic context while inspecting one department. The map measure
selector affects only the map and ranking; temporal charts retain case-count
units. Filters are encoded in the URL and support browser back/forward.

Counts use proportional circles with area proportional to value. Population
normalization uses a sequential choropleth. No-data polygons are hatched.
The color scale recalculates with the selected period; compare values using
the visible legend and table rather than color alone. The seasonal traces
share a linear zero-based y-axis and distinct year labels.

Both CSV buttons use the same filtered model as the views. Summary CSV rows
include population, rate, source-row availability, requested and actual week
bounds, definitions, and snapshot metadata. Weekly CSV preserves every selected
cell and its observation status. Blank values mean unavailable. No rows are
silently changed to zero for export. Inverted filters produce an empty state.

## What the validation establishes

Independent API aggregation checked all 8,358 original department-week-event
sums, including excluded geography. A separate implementation reconciled all
13,794 published cells to the original records. Tests check geographic joins,
district handling, period lengths, missingness, denominator matches, and
representative rates. Browser checks exercise filtering, URLs, exports, empty
states, and responsive layouts. See the dated release report for checks actually
run; the existence of a test file is not evidence that it passed.

These checks establish consistency of this transformation and interface. They
do not establish surveillance sensitivity, complete population coverage,
causality, absence of underreporting, or comparability with differently defined
PAHO and INS bulletin series. See [source choices](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/docs/sources.md).

## AI assistance

Implementation, source inspection, and software review used AI assistance.
Independent checks here mean separate computational implementations/reviews,
not independent human epidemiological validation. A domain expert should review
definitions and fitness for use before extending this demonstration to research
claims or operational decisions.
