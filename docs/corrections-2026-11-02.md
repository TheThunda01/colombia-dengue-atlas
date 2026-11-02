# Corrections recorded on 2 November 2026

These issues were found during first-release review, before claiming deployment verification. They concern the interface implementation, not corrections to the original surveillance observations.

## Reversed adjacent year range

**Trigger:** a selection such as 2020–2019 with the rate map active.

**Before:** the model computed zero selected years, then divided an empty rate sum by zero. The map could receive NaN while the summary table correctly remained empty.

**Correction:** the mean-rate calculation now requires a positive year count and a usable yearly value for every selected year. Reversed ranges return null map values and empty summaries.

**Evidence:** `tests/model.test.mjs` includes reversed-year and reversed-week regression cases. The executed model suite passed 14 tests with no failures or skips at review time.

## Isolated observations in temporal charts

**Trigger:** a single selected week, or an observed count surrounded by absent-source weeks.

**Before:** line-only Plotly traces could hide an isolated observation because no line segment could be drawn. The underlying count and CSV were present.

**Correction:** timeline and seasonal traces now use restrained markers with lines. `connectgaps:false` remains in place so missing weeks are not bridged. Source inspection confirmed this code change.

**Verification boundary:** marker presence was verified in source code; this correction record does not claim browser-level visual verification. Actual desktop, narrow-layout, filter, download, and deployment checks belong in the release report. No synthetic observation was added to the published data to demonstrate either fix.

Release follow-up: the local Edge browser checks verified single-week point visibility, sparse observations, no-data states and both actual CSV downloads. See `reports/browser_local.json` and `RELEASE_REPORT.md` for executed scope.
