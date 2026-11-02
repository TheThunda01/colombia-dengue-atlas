# Dengue records and surveillance concepts

Before reading the charts, it helps to separate the disease from the observations
we have about it. This project contains public aggregate surveillance counts.
It does not contain individual clinical records, diagnostic results, or a sample
from which the total number of infections can be estimated.

## What counts as a case here?

The INS source labels event **210 as dengue** and **220 as severe dengue**.
The atlas preserves those labels and displays each event separately. It does
not reclassify patients, infer laboratory confirmation, or add the two categories
and claim a deduplicated clinical total. The source's routine-data notes and
unresolved classification details are recorded in the [INS assessment](ins-source.md).

## Why a recorded count is not the whole disease burden

A published aggregate describes the cases represented in that extract. A
department-week with a source row is observable; it does not establish that every
municipality reported or that every infection was detected. A department-week
without a source row is unavailable. We cannot decide from this extract alone
whether it reflects zero cases, an omitted submission, or another source convention.

That distinction explains the atlas's gaps and hatching. Bogotá D.C. remains
on the map with no usable value because neither selected event has source rows
there in this snapshot. Painting it as zero would add a claim the data do not support.

## Why population and place matter

A department with more residents can have more recorded cases even if its
population-normalized count is lower. The atlas therefore offers both counts
and available counts per 100,000 total residents, using each year's DANE
population. This denominator includes all residents. It is different from the
population at risk used in official dengue incidence measures.

The numerator also has a geographic definition: occurrence/procedence in the
source, not verified residence. Matching department codes makes the calculation
consistent; it does not erase that interpretive difference. See the
[methods](methods.md) and [DANE assessment](dane-source.md) for the exact joins.

## How to interpret a pattern responsibly

Imagine that a line falls between two years. First check whether you selected
the same event and weeks. Next inspect source-row availability and the annual
denominator. Then describe what is directly visible: the available recorded
count was lower in the selected period. An explanation involving transmission,
interventions, weather, or reporting would require evidence beyond these charts.

The [worked example](practical-use.md) walks through that reading process. The
[glossary](glossary.md) defines the technical terms, and the
[assumption register](assumptions.md) keeps unresolved issues visible.
