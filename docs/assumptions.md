# Assumptions and interpretation boundaries

The atlas makes the following explicit choices; each is a limit on interpretation.

- **One surveillance snapshot:** 2019–2022 comes from licensed INS dataset `4hyg-wa9d`. Differently revised bulletins and PAHO totals are not used to fill gaps.
- **Separate categories:** events 210 and 220 remain distinct because aggregate data cannot verify person-level overlap or deduplication. Mortality event 580 is excluded.
- **Published time labels:** source year/week is retained, including week 53 only in 2020. Underlying onset-versus-notification semantics remain unresolved. Fully elapsed years do not prove complete capture.
- **Occurrence geography:** municipality rows are summed under their published department codes. Districts already carry parent codes and are included once. Foreign and unknown locations are excluded from maps and retained in the audit. Bogotá is a no-data unit.
- **No imputation:** an absent row remains null. Partial-period totals sum available observations and show availability counts. An observed department-week does not establish that every municipality reported.
- **Descriptive denominator:** DANE total resident population is matched by department and year, using one 2025 revision. It includes populations outside dengue transmission areas and does not turn occurrence-based counts into resident infection risk.
- **Fixed display geometry:** MGN2025 boundaries are simplified for display. Codes determine joins; polygons do not allocate cases or reconstruct annual historical boundaries.

No uncertainty interval, forecast, causal effect, or reporting-completeness measure is inferred. Review the [methods](methods.md), [source register](sources.md), and [independent review](../reports/independent_scientific_review.md) before extending these choices.
