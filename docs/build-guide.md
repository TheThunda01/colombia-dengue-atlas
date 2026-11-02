# How this atlas was built

The easiest way to understand this project is to follow one number from its source to the screen. We start with a published count, keep its original meaning, join it to the right department and year, and only then decide how to draw it. The interesting work is often in those joins and definitions rather than in the charting command.

This guide explains that process and the reasons behind it. The code blocks marked **excerpt** come from the implementation, with comments or formatting added for teaching; they are not replacement scripts. Follow the linked files for their complete validation and error handling. The worked example is a separate, runnable calculation using the committed data.

For a first visit, read the [project overview](../README.md), work through this guide, then use the [methods](methods.md), [data dictionary](data-dictionary.md), and [glossary](glossary.md) when you want a precise definition.

## 1. Start with a question the data can answer

The atlas asks how recorded dengue counts vary across Colombian departments and source epidemiological weeks during 2019–2022. It supports descriptive comparisons, with a second view that divides available counts by annual total resident population.

That wording does real work. Recorded cases are not all infections. A source-present week is not evidence that every municipality reported completely. The extract does not settle whether the week reflects symptom onset or notification, so the interface says “source epidemiological week.” Its geographic fields describe occurrence/procedence; we do not quietly relabel them as residence.

The INS dataset supplies two event codes: 210 for dengue and 220 for severe dengue. They remain separate selections. The project does not assume they can be added into a deduplicated clinical total. Likewise, it uses closed years without claiming closed years guarantee complete surveillance capture. These choices are documented in the [INS source assessment](ins-source.md) and [assumptions](assumptions.md).

## 2. Separate the scientific model from the drawing

There are three layers: preserve inputs, prepare a well-defined dataset, and present it. Python handles the first two and creates publication figures. JavaScript applies interactive filters in the browser. Quarto gathers the pages and assets into a static website.

| Where to look | What it does | Why it is separate |
|---|---|---|
| `data/raw/` and source manifests | Preserve source bytes and fingerprints | A later portal revision must not silently change an old result. |
| `scripts/prepare_surveillance.py` | Validate, aggregate, and expand weekly records | Counting rules can be inspected without reading interface code. |
| `scripts/prepare_geography.py` | Prepare population and boundaries | Denominators and map geometry need different checks. |
| `data/processed/` | Hold reusable tables, geography, and audits | Analysis can be repeated without downloading everything again. |
| `scripts/build.py` | Create the browser bundle and publication figures | The site and figures begin from the same processed inputs. |
| `site/assets/model.mjs` | Filter, summarize, and serialize CSV | Charts and exports share calculations. |
| `site/assets/atlas.js` | Respond to controls and draw the interface | Presentation can change without rewriting case definitions. |
| `scripts/site.py` and `site/_quarto.yml` | Execute and render the site | The correct Python environment is explicit. |

A useful mental picture is `source bytes → checked tables → shared model → maps, charts, tables, downloads`. The arrows are transformations we can test. A more attractive map should leave the numeric meaning of every arrow intact.

## 3. Recreate the working environment

Clone the repository and run these commands from its root. You need Python 3.12, uv, Node.js, and Quarto available on your command path. The Python requirements are recorded in `pyproject.toml`; `uv.lock` fixes their resolved versions. Quarto and Node are separate installations, not packages supplied by `uv sync`.

~~~powershell
git clone https://github.com/TheThunda01/colombia-dengue-atlas.git
Set-Location colombia-dengue-atlas
uv sync --frozen --system-certs
uv run python scripts/build.py
uv run python scripts/site.py preview
~~~

Open `http://127.0.0.1:4200/`. The preview server matters because the explorer fetches its JSON through a relative URL. Double-clicking an HTML file gives a `file://` origin and can prevent that fetch. The published site itself needs no Python service: GitHub Pages serves the finished HTML, JavaScript, JSON, and figures.

`--frozen` asks uv to use the existing lockfile rather than resolving a different environment. `--system-certs` uses the operating system's trusted certificate store; it does not turn certificate verification off. The default build uses the committed processed snapshot. It does not request current surveillance data from the portal each time you render a page.

## 4. Download a snapshot, then prove which bytes you used

The official aggregate dataset is [INS dataset 4hyg-wa9d](https://www.datos.gov.co/d/4hyg-wa9d). Each annual request limits the years and events and uses an explicit ordering. That makes the request inspectable and helps prevent an apparently successful download from hiding a truncated result.

**Excerpt — annual query parameters in [prepare_surveillance.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/prepare_surveillance.py):**

~~~python
{
    "$where": f"ano={year} AND cod_eve in(210,220)",
    "$order": "cod_eve,semana,cod_dpto_o,cod_mun_o",
    "$limit": "50000",
}
~~~

The full fetch routine saves the response bytes before transformation, records the request URL and UTC retrieval time, and computes SHA-256. It checks whether the response reaches the request limit, which could indicate truncation, and verifies the expected data license. Another request independently asks the portal for grouped sums and row counts; preparation compares those results with local aggregation.

A hash answers “Are these exactly the same bytes?” It does not answer “Are these observations correct?” Keep those questions separate. The snapshot retrieved on 2 November 2026 has a source update date of 17 October 2024; retrieval date is not a claim of new 2026 surveillance.

The DANE inputs follow the same principle. Their URLs and expected hashes are in `data/dane_sources.json`. A download that differs from the pinned fingerprint fails instead of quietly replacing the expected input. Code licensing and source-data licensing are documented separately in [sources](sources.md).

## 5. Read the source fields before aggregating

The preparation script expects the source's actual fields, including `ano`, `semana`, `cod_eve`, `cod_dpto_o`, `cod_mun_o`, and `conteo`. It validates years, weeks, event categories, nonnegative integer counts, geographic codes, and duplicate municipality/week/event keys before producing department totals.

Department codes stay as strings. `"05"` is an identifier for Antioquia, not the number five in a calculation. Converting it to an integer and forgetting to restore the leading zero can break a perfectly plausible-looking join. The script normalizes department codes to two characters and municipality codes to five.

The frozen source contains 57,083 municipality/week/event rows. These are aggregate counts, not person-level records. Grouping uses year, week, department, and event. The 8,358 independently obtained portal groups also include excluded geographic categories; they are a reconciliation target, not the final number of mapped cells.

The release has 52 weeks in 2019, 53 in 2020, and 52 each in 2021 and 2022. Those 209 source week positions, multiplied by 33 department-level units and two events, produce 13,794 cells. We do not manufacture a week 53 in every year or turn these labels into ISO calendar dates.

## 6. Preserve absence, zero, and partial information

This is the most important rule in the data model. If the source publishes no row for a department/week/event combination, the atlas records `null`. It does not invent a zero.

**Excerpt — expanding the full panel in [prepare_surveillance.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/prepare_surveillance.py):**

~~~python
key = (year, week, dept, event)

# Membership matters: an absent key differs from a published zero.
value = aggregates[key] if key in aggregates else None
status = (
    "source_absent" if value is None
    else "explicit_zero" if value == 0
    else "observed_positive"
)
~~~

The first snapshot has 8,130 positive cells and 5,664 source-absent cells, with no explicit zeros. The software still preserves zero as a valid future input. In JSON, absence becomes `null`; in CSV, it becomes an empty cell. A blank export is therefore meaningful rather than an accidentally omitted value.

**Excerpt — [model.mjs](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/site/assets/model.mjs):**

~~~javascript
export function sumPresent(values) {
  const present = values.filter((v) => v !== null && Number.isFinite(v));
  // An empty observed set stays unavailable; [0] remains a numeric zero.
  return present.length ? present.reduce((a, b) => a + b, 0) : null;
}
~~~

Notice the remaining nuance: `[12, null]` sums to 12, but that is a sum of available observations. The surrounding model also counts source-present and source-absent cells, so the interface can flag partial input. Neither 12 nor “one of two cells present” tells us the true completeness of surveillance. The Python figure uses `sum(min_count=1)` for the same all-missing versus zero distinction.

## 7. Resolve geography before joining a population

The map contains Colombia's 32 departments plus separately coded Bogotá D.C. Bogotá has a population denominator and geometry, but no records in this selected source snapshot. Its count and rate remain unavailable.

District handling deserves a careful look. Barranquilla's municipality code begins with `08`, Cartagena's with `13`, and Santa Marta's with `47`; Cali and Buenaventura belong to `76` in these source records. Aggregating municipality records by their existing parent department includes each once. Adding a separate district total afterwards would double-count those records.

Foreign code `01` and unknown code `00` are retained in the audit but excluded from the Colombian department map. A successful geographic join requires the same 33 domestic identifiers in the surveillance panel, population table, and geometry. It does not require matching names with accents or guessing from coordinate locations.

See the [DANE source assessment](dane-source.md) for boundary provenance and the [data dictionary](data-dictionary.md) for the resulting identifiers.

## 8. Match each count with the correct denominator

The denominator is DANE's annual total resident population from its 2025 revision of the CNPV 2018 projections. Select the total row once for each department and year; do not add it to the urban and rural component rows.

**Excerpt — population selection in [prepare_geography.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/prepare_geography.py):**

~~~python
table = pd.read_excel(
    path,
    sheet_name="PobDepartamentalxÁrea",
    header=7,                    # Excel row 8 contains the column headings.
    dtype={"DP": str},          # Preserve geographic identifiers.
)
table = table.loc[
    (table["ÁREA GEOGRÁFICA"] == "Total") & table["AÑO"].isin(YEARS)
].copy()
~~~

The complete function renames fields, rejects duplicate department/year keys, and checks for 132 positive denominators: 33 units across four years. A year-specific summary calculates available selected-week cases divided by that year's population, multiplied by 100,000.

For several selected years, the map shows the arithmetic mean of those yearly normalized values. It requires a usable value for every selected year. It does not divide a multiyear case sum by one year's population, and it does not annualize a short week selection. This is total-population normalization, not the official dengue incidence denominator for the population at risk.

## 9. Follow one real example all the way through

Run this PowerShell block from the repository root after building. It imports the actual browser model, so the calculation follows the same rules as the explorer rather than a second interpretation of them.

**Runnable worked example — Antioquia, event 210, 2019, weeks 1–52:**

~~~powershell
@'
import fs from "node:fs";
import { defaults, summaries } from "./site/assets/model.mjs";

const data = JSON.parse(fs.readFileSync("site/data/atlas.json", "utf8"));
const selection = {
  ...defaults,
  department: "05", // Antioquia: keep the leading zero.
  event: "210",     // Dengue, separately from severe dengue.
  start: 2019,
  end: 2019,
  first: 1,
  last: 52,
};
const [row] = summaries(data, selection);
console.log(JSON.stringify({
  department: row.department_name,
  cases: row.cases,
  population: row.population_total,
  per100k: row.cases_per_100k,
  presentWeeks: row.source_present_weeks,
  expectedWeeks: row.expected_weeks,
}, null, 2));
'@ | node --input-type=module -
~~~

For the frozen release, this gives 4,980 recorded cases, 6,518,070 residents, approximately 76.403 cases per 100,000 total residents, and 52 of 52 source-present week cells. The arithmetic is `4,980 / 6,518,070 × 100,000`. The availability result means each department/week cell has source input; it does not prove every infection was captured or every municipality reported.

## 10. Make the map lighter without changing the joins

Detailed administrative boundaries are useful for reference but expensive to deliver to every browser. The preparation script simplifies DANE's fixed MGN 2025 reference geometry in a projected coordinate system, where the tolerance is expressed in metres.

**Excerpt — [prepare_geography.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/prepare_geography.py):**

~~~python
boundaries = boundaries.to_crs(9377)
boundaries.geometry = boundaries.geometry.simplify(
    500, preserve_topology=True
)
boundaries = boundaries.to_crs(4326)
~~~

This reduces roughly 1.08 million coordinates to 14,492. Per-feature topology preservation helps maintain valid shapes; it is not a claim of survey accuracy or perfectly shared adjacent boundaries. These are display boundaries, with source feature years 2024/2025, not reconstructed historical boundaries for each surveillance year.

The build projects them again to EPSG:9377 and fits the coordinates into the SVG drawing area. Its `geometry_paths()` function flips the vertical axis because screen coordinates increase downward. A representative point anchors each count symbol inside its geometry. That position is a display anchor, not a case location.

Counts and populations join by codes throughout. No point-in-polygon operation assigns cases, so display simplification cannot move a case into a different department. Proportional circles communicate counts; their radius grows with the square root of the value so area, rather than radius, represents magnitude. Rates use a sequential fill, with a separate unavailable-data treatment.

## 11. Let one selection drive every interactive output

The browser stores department, event, year bounds, week bounds, and metric in a state object. `readState()` reads those values from the URL and validates the allowed values. A saved URL can therefore reopen a particular comparison. An inverted range stays an empty selection with a visible explanation instead of being silently reinterpreted.

**Excerpt — the shared filter in [model.mjs](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/site/assets/model.mjs):**

~~~javascript
export function selectedRows(data, s, context = false) {
  return data.rows.filter((r) =>
    r.event_code === s.event &&
    r.year >= s.start && r.year <= s.end &&
    r.week >= s.first && r.week <= s.last &&
    (context || s.department === "all" || r.department_code === s.department)
  );
}
~~~

The `context` argument allows the map to retain surrounding departments while the selected department drives its focused temporal views. Event and time filters still apply. The same model then produces annual summaries, map summaries, and a year/week series.

The drawing code uses Plotly for the timeline and seasonal comparison. `connectgaps: false` keeps missing observations from becoming an invented continuous line. Partial geographic sums receive a distinct marker treatment. Empty results remove old traces and show an explanation, so a previous valid chart cannot masquerade as the new selection.

The visible summary table and its CSV download use the same summary rows. Weekly export uses the same selected source cells. Export fields carry the event, time bounds, denominator, availability, units, source URL, and snapshot date; this makes a downloaded number interpretable outside the website. CSV serialization preserves null as blank, quotes embedded delimiters, and guards specific formula-like text prefixes. See [atlas.js](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/site/assets/atlas.js) for control handlers, history navigation, plotting, and download wiring.

## 12. Build figures and render a static publication

The publication figures start from the same processed weekly records as the browser bundle. Matplotlib creates the yearly temporal comparison with shared axes and a zero baseline, then writes SVG, PNG, and PDF. SVG is useful for vector editing, PNG for convenient previews, and PDF for print workflows. Fixed source metadata and SVG hashing reduce incidental differences between repeated exports.

The companion geographic comparison is generated by [cartographic_plate.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/cartographic_plate.py), with its plotted values available in `data/processed/map_comparison.csv` and the figure in `figures/map-comparison.svg`, `.png`, and `.pdf`. This keeps the visual composition and the numbers behind it reviewable together.

Its four annual panels use the same linear color scale, 0–2,500 recorded cases per 100,000 total residents in this snapshot. Bogotá remains hatched as unavailable. Each panel reports source-cell availability, and the islands remain at their original coordinates. A dark area therefore means the same numeric value in each year, while the labels explain the limits of the available input.

**Excerpt — annual aggregation in [cartographic_plate.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/cartographic_plate.py):**

~~~python
annual = selected.groupby(["department_code", "year"], as_index=False).agg(
    # min_count=1 preserves an entirely absent department/year as missing.
    cases=("cases", lambda values: values.sum(min_count=1)),
    available_weeks=("cases", "count"),  # Non-null cells only.
    expected_weeks=("cases", "size"),    # All structurally expected cells.
)
~~~

For an ordinary clone, verify the committed plate bundle with:

~~~powershell
uv run python scripts/cartographic_plate.py
~~~

This command recomputes the 132-row annual table in memory, then verifies the committed CSV, SVG, PNG, and PDF against their recorded hashes. It also checks fingerprints for the plate's text inputs, renderer script, and `uv.lock`, normalizing text line endings to LF so a Windows/Linux checkout difference does not count as a scientific change. If everything matches, it reuses the complete release bundle without redrawing it. The ordinary site build therefore does not require Inkscape on a fresh clone.

The PNG and PDF supplied with this revision were exported through Inkscape 1.4.4. When the plate's data, renderer, or exports change, verification fails with a refresh instruction. With Inkscape installed and on your command path, refresh the artwork with:

~~~powershell
uv run python scripts/cartographic_plate.py --inkscape inkscape
~~~

For a portable installation, replace the last argument with its quoted full executable path. The refresh stages the new outputs and publishes the replacement bundle only after the Inkscape exports succeed. It records the application version and file fingerprints in `reports/cartographic_plate.json`, so the report distinguishes an actual desktop-software export from a normal verification run.

For an initial development run with no previous PNG/PDF bundle, the standalone script can create just the SVG and CSV without Inkscape. That is not enough for publication: the root site build requires a complete, verified export bundle. Inkscape is optional for ordinary rebuilds of this release and required to refresh its cartographic artwork.

External graphics software can help with layout or final composition, but the scripts remain the source of numeric values, scales, labels, and missing-data rules. If you edit an exported vector figure, keep its editable source and a documented regeneration route. The [visualization software guide](visualization-tools.md) explains where free tools, including Inkscape, QGIS, and Blender, fit into this workflow.

Quarto renders the explanatory pages and executes their Python code. On Windows, simply launching Quarto from an activated environment can still select an unexpected kernel. The wrapper explicitly gives it the Python interpreter running the build.

**Excerpt — environment setup in [site.py](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/scripts/site.py):**

~~~python
env = os.environ.copy()
env["QUARTO_PYTHON"] = sys.executable
env["JUPYTER_PATH"] = (
    str(Path(sys.prefix) / "share/jupyter")
    + os.pathsep + env.get("JUPYTER_PATH", "")
)
subprocess.run(args, cwd=ROOT, env=env, check=True)
~~~

The finished website lands in `site/_site/`. Project-relative asset and data URLs allow it to work beneath the repository path on GitHub Pages. Plotly is bundled locally, so the explorer does not depend on a chart-library CDN request at viewing time.

## 13. Check calculations, behavior, and the published artifact

Different checks answer different questions. Python tests cover preparation and source consistency; Node tests exercise the shared model; rendered-site checks inspect links and assets; browser checks exercise real controls and downloads.

~~~powershell
uv run pytest -q
node --test tests/model.test.mjs
uv run python scripts/check_site.py
~~~

With the preview server running in another terminal:

~~~powershell
uv run python scripts/browser_checks.py --url http://127.0.0.1:4200/
~~~

The browser script uses Microsoft Edge by default. Where Edge is unavailable, install the project Playwright Chromium browser with `uv run playwright install chromium`, then add `--channel chromium` to the check command.

The first-release evidence records 28 Python tests, 14 Node tests, and 11 browser scenarios. Those are dated results, not a promise about later versions; inspect [RELEASE_REPORT.md](../RELEASE_REPORT.md) and `reports/` for the exact release evidence. Independent reconciliation also checked all 13,794 panel cells without finding a computational discrepancy.

The [Pages workflow](https://github.com/TheThunda01/colombia-dengue-atlas/blob/main/.github/workflows/pages.yml) installs pinned tool versions, prepares the frozen surveillance snapshot, builds, tests, and checks that committed processed surveillance outputs reproduce. Pull requests run checks; a successful main-branch build can upload and deploy the static artifact. Hosted CI proves those specified software checks passed. It cannot establish surveillance sensitivity, denominator suitability for a new scientific question, or causal interpretation.

## 14. Refresh deliberately and keep the old evidence

A normal rebuild needs no new source snapshot. To reconstruct processed geography from the pinned originals, use:

~~~powershell
uv run python scripts/prepare_geography.py --download
uv run python scripts/build.py --prepare
~~~

To investigate a newer surveillance extract, choose a new, nonexistent candidate directory. Replace the date label below before running:

~~~powershell
uv run python scripts/prepare_surveillance.py --fetch-to data/candidates/ins-YYYY-MM-DD
~~~

The fetch operation refuses to reuse an existing destination. Review its metadata, license, schema, year/week coverage, hashes, and changed totals before adopting anything. A new snapshot may revise old years as well as add information. Preserve the original snapshot, record the change, rerun preparation and checks, and update the narrative and release evidence together. Passing a hash check only establishes consistency with the expected input; it does not approve a changed source definition.

## 15. Troubleshoot from the failed boundary

| Symptom | What to inspect first |
|---|---|
| Quarto is not found | Install the required standalone tool, reopen the terminal, and check its command path. |
| Python imports fail during page execution | Use `uv run python scripts/site.py render` so the wrapper selects the project interpreter. |
| The explorer cannot load data locally | Use the preview server and inspect the relative `data/atlas.json` request. |
| A source hash differs | Preserve both versions and investigate the source revision; do not remove verification to make the build pass. |
| A department fails to join | Check string identifiers and leading zeros before considering name matching. |
| A rate is blank while a count exists | Inspect the matching annual denominator and the selected-year rate requirements. |
| A selected range shows no observations | Check reversed bounds, event selection, source absence, and whether week 53 exists in those years. |
| Local rendering works but Pages does not | Inspect project-relative links, deployed artifact paths, and the exact hosted workflow result. |

## 16. Explain the project in a conversation

If you are presenting this work, begin with a concrete result such as the Antioquia example, then explain how the result remains traceable. The main engineering contribution is a shared, testable data model that keeps source meaning visible across maps, charts, tables, and downloads.

Be ready to explain five decisions: why missing values remain distinct from zero; why district records enter a department total once; why a denominator must match geography and year; why a multiyear mean of annual rates differs from a pooled rate; and why a static site is sufficient for a frozen aggregate dataset. These are useful concepts well beyond dengue surveillance.

For terminology, return to the [glossary](glossary.md). For scientific interpretation, use [practical use and limitations](practical-use.md) and the [methods](methods.md). For the source trail, use the [source register](sources.md), [literature review](literature-review.md), and [reference audit](reference-audit.md). Together, those documents let a reader move from a visible comparison to its calculation, its provenance, and the limits of what it can support.
