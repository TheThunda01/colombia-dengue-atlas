# Interface design brief

The atlas should make one defensible descriptive comparison at a time. The selected department, years, epidemiological weeks, and metric must be visible without hovering. All controls, captions, tables, and downloads should share the same filtered summary calculation.

## Overview and coordinated exploration

- Lead with the actual source, complete study years, unit of geography, and the fact that these are reported surveillance observations. Explain that source-row availability is not reporting completeness.
- Use a native labeled department selector, year range, week range, metric selector, and reset button. Keep an all-departments option to restore geographical context. Changing a filter should update the map, summary, time series, seasonal comparison, availability table, and download filename/metadata together.
- Show counts as proportional circles on a neutral department map. If a rate is available, use a sequential choropleth with an explicit scale and denominator label. For a selected multiyear interval, counts sum the available weekly records, while the map rate is the arithmetic mean of year-specific selected-week cases divided by each year's total population. A usable rate is required in every selected year; a partial-week selection is not annualized. This is not official population-at-risk incidence.
- Represent source absence as a distinct no-data style with a text explanation. A reported zero is a valid numeric value and retains the zero color/size treatment. A missing denominator disables only the rate, not a valid count.
- Keep the map context at the same administrative level. District totals must be rolled into their parent department once before map or denominator joins. A territorial rollup is not a spatial inference about where infections occurred.

## Temporal views

- The time series uses source epidemiological year and week with discontinuities for missing source rows. Label date semantics according to the verified dataset, including where they remain unresolved. Do not join missing weeks with a line or convert absent rows to zeros.
- The seasonal panel overlays the same selected department's year traces by epidemiological week. Use consistent y-axis units and a shared scale, a colorblind-friendly palette, explicit year legends, and a separate week-53 position where supported. A selected week range applies equally across years.
- If an all-departments aggregate is shown, label its geographical coverage and flag incomplete geographic input coverage. A sum of observed departments must not imply that absent departments reported zero.

## Provenance and download

- Provide an availability table with expected source cells, observed rows, explicitly reported zeros, absent rows, and denominator availability, but only where the source contract supports each statistic. Avoid calling these values reporting completeness.
- Make source name, retrieval date, snapshot fingerprint, selected case classifications, district rollup, and rate denominator reachable from the current view.
- Export the actual displayed summary rows, including identifiers, years/weeks, counts, rates, units, denominator, coverage status, and source snapshot information. Include a visible table so essential values can be read without chart hover.
- An impossible filter or empty selection needs a plain-language empty state and a working reset. Keyboard focus must remain visible; charts should have adjacent textual summaries.

## Release inspection

Inspect desktop and narrow layouts using the actual rendered static site. Exercise every filter, keyboard selection, reset, download, zero/missing handling, and empty state. Test project-relative links and data fetches at the deployed GitHub Pages URL as well as locally. Do not describe unperformed visual checks as passed.

## Visual refinement in v1.1

The explorer now uses a fixed event-specific color domain across all four years.
Count symbols retain an adaptive size domain with direct numeric labels and an
explicit rescaling note. Hatching has its own legend swatch; Bogotá's unavailable
status is named even when its small polygon is hard to see. A persistent detail
panel pairs the selected unit's value with its present/expected week cells.
Keyboard selection restores focus to the replaced map or ranking control.
Narrow-screen timeline ticks show years, with exact weeks still in tooltips and CSV.

The publication map plate uses four equal-size maps with identical extents and a
shared linear 0–2,500 scale. Map and color scale remain two-dimensional. Inkscape
converts the generated vector artwork to PNG/PDF; no case values, geometry, or
rates are edited by hand. The separate [software guide](visualization-tools.md)
explains free-tool choices and the reasons to reserve Blender for a future scene
with meaningful three-dimensional information.

The site reading path is Overview → Explore/Figures → Methods/Data → Learn.
The Learn menu brings together reasoning, glossary, annotated code, and tool
choices. The README follows the same seven-section portfolio outline as the
other projects and adds a guide/purpose table for deeper reading.
