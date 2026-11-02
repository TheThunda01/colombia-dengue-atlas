# Data dictionary

`surveillance_weekly.csv`: one department × source epidemiological year/week ×
INS event. There are 13,794 cells; missing cases are blank in CSV and null in JSON.

|Field|Meaning / units|
|---|---|
|year, week|Source epidemiological labels; not inferred onset or notification dates|
|department_code|Two-character DANE code, retain leading zero|
|department_name|Display name for department-level unit including Bogotá|
|event_code, event_name|210 Dengue or220 Severe dengue, kept separate|
|cases|Recorded count summed from available municipal source rows; nullable nonnegative integer|
|observation_status|observed_positive, explicit_zero, or source_absent; explicit_zero is supported but not present in this release|
|source_rows|Number of contributing municipal aggregate rows;0 if source_absent|
|source_id|ins-socrata-4hyg-wa9d|

`population.csv`: department/year Total area population, persons, 2019–2022.
`population_scope` identifies total residents, not dengue population at risk.
`population_source` identifies the fixed DANE revision. No selected denominator
is missing or nonpositive.

`departments.geojson`: 33 display geometries with `department_code`,
`department_name`, `boundary_name`, `boundary_version`, and
`boundary_feature_update_year`; WGS84 longitude/latitude, EPSG:4326.

The filtered annual CSV adds:

|Field|Meaning / units|
|---|---|
|first_week, last_week|Requested week bounds from the controls|
|actual_first_week, actual_last_week|Bounds among structural week cells in that year; includes absent cells|
|population_total|Matched DANE total residents for that department/year|
|cases_per_100k|Available selected-week cases / population_total ×100,000; null if numerator/denominator unavailable|
|source_present_weeks, source_absent_weeks, expected_weeks|Grid cell availability, not submission completeness|
|explicit_zero_weeks|Cells explicitly reporting zero;0 for this snapshot|
|availability|all_week_cells_present, partial_week_cells, or no_source_rows|
|count_unit, rate_unit, time_basis, location_basis|Interpretation carried in the export|
|snapshot_date, source_data_updated_utc, source_url, population_version|Provenance carried in the export|

The map's multiyear rate is the arithmetic mean of each selected year's
`cases_per_100k`, requiring a nonnull value in every selected year. The annual
CSV preserves the components of that calculation. A weekly CSV adds snapshot
metadata to the selected cell-level rows. CSV text fields are quoted and guarded
against leading formula characters; null is represented by an empty cell.
