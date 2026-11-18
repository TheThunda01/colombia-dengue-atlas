import {
  defaults,
  readState,
  selectedRows,
  summaries,
  annualAvailability,
  mapSummaries,
  rateScaleMaximum,
  timeSeries,
  sumPresent,
  csv,
} from "./model.mjs";
const $ = (id) => document.getElementById(id),
  fmt = (n) =>
    n === null ? "No data" : new Intl.NumberFormat("en-US").format(n),
  dec = (n) =>
    n === null
      ? "No data"
      : new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(n);
const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const colors = {
  2019: "#166b70",
  2020: "#bd632b",
  2021: "#69509b",
  2022: "#3b677f",
};
const bindings = {
  department: "department",
  event: "event",
  start: "year-start",
  end: "year-end",
  first: "week-start",
  last: "week-end",
  metric: "metric",
};
let data,
  state,
  rateMaxima,
  latestSummary = [],
  latestWeekly = [],
  renderToken = 0;
function setControls() {
  for (const [k, id] of Object.entries(bindings)) $(id).value = state[k];
}
function stateUrl() {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(state)) p.set(k, v);
  return "?" + p;
}
function selectDepartment(code) {
  const active = document.activeElement;
  const fromMap = active?.matches("path[data-code]");
  const fromRanking = active?.matches("#rank-table button");
  state.department = code;
  setControls();
  history.pushState(null, "", stateUrl());
  render();
  if (fromMap || fromRanking) {
    const container = fromMap ? $("map-container") : $("rank-table");
    container
      .querySelector(`[data-code="${code}"]`)
      ?.focus({ preventScroll: true });
  }
}
function download(rows, kind) {
  const blob = new Blob(["\uFEFF" + csv(rows)], {
      type: "text/csv;charset=utf-8;",
    }),
    a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `colombia-${state.event}-${state.department}-${state.start}-${state.end}-w${state.first}-${state.last}-${kind}.csv`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
function renderMap() {
  const map = mapSummaries(data, state),
    val = (d) => (state.metric === "rate" ? d.rate : d.cases),
    rate = state.metric === "rate",
    max = rate
      ? rateMaxima[state.event]
      : Math.max(1, ...map.map((d) => d.cases ?? 0));
  const rateDefinition = state.start === state.end
    ? `Cases in the selected weeks per 100,000 total residents in ${state.start}. The denominator comes from DANE.`
    : "Mean of yearly selected-week cases per 100,000 total residents. Each year uses its own DANE population.";
  $("map-subtitle").textContent = rate ? rateDefinition
    : "Circle area shows the number of recorded cases summed over the selected weeks.";
  const fill = (d) => {
    if (val(d) === null) return "url(#missing)";
    if (!rate) return "#e4ece9";
    const f = val(d) / max;
    return `rgb(${Math.round(229 - 207 * f)},${Math.round(241 - 134 * f)},${Math.round(237 - 125 * f)})`;
  };
  const paths = map
    .map(
      (d) =>
        `<path class="department-shape${d.code === state.department ? " selected" : ""}" data-code="${d.code}" d="${d.path}" fill="${fill(d)}" tabindex="0" role="button" aria-label="${escape(d.name)}, ${rate ? dec(val(d)) : fmt(val(d))}${rate ? " per 100,000 (mean)" : " recorded cases"}" aria-pressed="${d.code === state.department}"><title>${escape(d.name)}: ${rate ? dec(val(d)) : fmt(val(d))}; ${d.present}/${d.expected} week cells present</title></path>`,
    )
    .join("");
  const dots = rate
    ? ""
    : map
        .filter((d) => d.cases !== null)
        .sort((a, b) => b.cases - a.cases)
        .map(
          (d) =>
            `<circle class="map-dot${d.code === state.department ? " selected" : ""}" cx="${d.x}" cy="${d.y}" r="${Math.sqrt(d.cases / max) * 24}"/>`,
        )
        .join("");
  $("map-container").innerHTML =
    `<svg viewBox="0 0 560 600" aria-label="Colombia departmental map" role="group"><defs><pattern id="missing" patternUnits="userSpaceOnUse" width="5" height="5"><rect width="5" height="5" fill="#e5e6e4"/><path d="M0,5 L5,0" stroke="#919b98" stroke-width="1"/></pattern></defs>${paths}${dots}<text x="16" y="575" font-size="10" fill="#52666d">San Andrés / Providencia shown at true geographic position</text></svg>`;
  $("map-container")
    .querySelectorAll("path[data-code]")
    .forEach((p) => {
      p.addEventListener("click", () => selectDepartment(p.dataset.code));
      p.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectDepartment(p.dataset.code);
        }
      });
    });
  const missingKey =
    '<span class="legend-key"><span class="legend-swatch missing-swatch"></span>No usable value</span>';
  $("map-legend").innerHTML = rate
    ? `<div class="rate-legend"><div class="rate-gradient"></div><div class="legend-endpoints"><span>0</span><span>${dec(max)}</span></div><span>Recorded cases per 100,000 residents</span></div>${missingKey}<p class="legend-note">Fixed color scale for event ${state.event}, 2019–2022. Colors stay comparable when you change the period.</p>`
    : `${map.some((d) => d.cases !== null) ? `<span class="legend-key"><svg width="50" height="50" aria-hidden="true"><circle cx="25" cy="25" r="24" fill="#166b70" fill-opacity=".58"/></svg>${fmt(max)} cases</span><span class="legend-key"><svg width="26" height="50" aria-hidden="true"><circle cx="13" cy="25" r="12" fill="#166b70" fill-opacity=".58"/></svg>${dec(max / 4)} cases</span>` : "<span>No recorded values in this period.</span>"}${missingKey}<p class="legend-note">Circle area represents count. Symbol sizes rescale for the current period.</p>`;
  const focused = map.find((d) => d.code === state.department);
  let focusedValue = "No data for this selection";
  if (focused && val(focused) !== null) {
    const rateLabel = state.start === state.end ? "per 100,000 residents" : "per 100,000 residents (mean across years)";
    focusedValue = rate ? `${dec(focused.rate)} ${rateLabel}` : `${fmt(focused.cases)} recorded cases`;
  }
  $("map-detail").innerHTML = focused
    ? `<strong>${escape(focused.name)}</strong><span>${focusedValue}</span><span>${fmt(focused.present)} of ${fmt(focused.expected)} department-week cells have source rows. ${focused.present < focused.expected ? "Absent cells remain missing." : "Row availability does not establish complete case capture."}</span>`
    : "<strong>Select a department</strong><span>Use the map or ranking to see its value and source-row availability here.</span>";
  const ranked = [...map].sort((a, b) => (val(b) ?? -1) - (val(a) ?? -1));
  $("rank-description").textContent = rate
    ? "The bars use the map’s rate scale, based on total resident population. Select a department to inspect its weeks."
    : "The bars rank all 33 department-level units by recorded cases. Select a department to inspect its weeks.";
  $("rank-table").innerHTML = ranked
    .map(
      (d) =>
        `<div class="rank-row"><button type="button" data-code="${d.code}" aria-pressed="${d.code === state.department}">${escape(d.name)}</button><div aria-hidden="true" class="rank-bar${val(d) === null ? " no-value" : ""}"><span style="width:${val(d) === null ? 0 : (100 * val(d)) / max}%"></span></div><span class="rank-number">${rate ? dec(val(d)) : fmt(val(d))}</span></div>`,
    )
    .join("");
  $("rank-table")
    .querySelectorAll("button")
    .forEach((b) =>
      b.addEventListener("click", () => selectDepartment(b.dataset.code)),
    );
}
const layout = () => ({
  font: { family: "system-ui, sans-serif", size: 12, color: "#14333d" },
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  margin: { l: 60, r: 20, t: 20, b: 65 },
  xaxis: { showgrid: false, zeroline: false },
  yaxis: {
    title: { text: "Recorded cases" },
    rangemode: "tozero",
    gridcolor: "#e0e7e5",
    zerolinecolor: "#a6b8b6",
  },
  showlegend: false,
  hovermode: "closest",
  dragmode: false,
});
const config = { responsive: true, displayModeBar: false, scrollZoom: false };
async function renderPlots() {
  const series = timeSeries(data, state),
    any = series.some((r) => r.cases !== null),
    name =
      state.department === "all"
        ? "Available department records"
        : data.departments.find((d) => d.code === state.department).name;
  const event = state.event === "210" ? "Dengue (210)" : "Severe dengue (220)";
  const years = state.start === state.end ? state.start : `${state.start}–${state.end}`;
  const context = `${name} · ${event} · ${years} · Weeks ${state.first}–${state.last}.`;
  const peak = series.reduce((best, row) =>
    row.cases !== null && (best === null || row.cases > best.cases) ? row : best, null);
  const peakNote = peak
    ? ` The highest available weekly total was ${fmt(peak.cases)} (${peak.label}).`
    : "";
  $("time-description").textContent = context + peakNote;
  $("season-description").textContent = context;
  if (!any) {
    const empty = series.length
      ? "No source rows for this selection. Its weekly case count is unknown."
      : "No epidemiological weeks match these dates. Adjust the year or week range.";
    for (const id of ["timeline", "seasonal"]) {
      Plotly.purge($(id));
      $(id).removeAttribute("role");
      $(id).innerHTML = `<div class="empty-state">${empty}</div>`;
    }
    return;
  }
  const token = renderToken;
  for (const id of ["timeline", "seasonal"]) {
    $(id).setAttribute("role", "img");
    if (!$(id).classList.contains("js-plotly-plot")) $(id).innerHTML = "";
  }
  const narrow = window.matchMedia("(max-width: 650px)").matches;
  const tick = series.filter((r, i) =>
      narrow
        ? i === 0 || r.year !== series[i - 1].year
        : i === 0 || r.week === 1 || r.week === 26,
    ),
    l = layout();
  l.xaxis = {
    ...l.xaxis,
    tickvals: tick.map((r) => r.label),
    ticktext: tick.map((r) =>
      narrow ? String(r.year) : `${r.year} W${r.week}`,
    ),
    tickangle: 0,
    title: { text: "Source epidemiological year / week" },
  };
  await Plotly.react(
    $("timeline"),
    [
      {
        x: series.map((r) => r.label),
        y: series.map((r) => r.cases),
        type: "scatter",
        mode: "lines+markers",
        marker: { size: 3, color: "#166b70" },
        connectgaps: false,
        line: { color: "#166b70", width: 2 },
        customdata: series.map(
          (r) => `${r.present}/${r.expected} department cells present`,
        ),
        hovertemplate:
          "%{x}<br>%{y:,} recorded cases<br>%{customdata}<extra></extra>",
      },
      {
        x: series
          .filter((r) => r.present < r.expected && r.cases !== null)
          .map((r) => r.label),
        y: series
          .filter((r) => r.present < r.expected && r.cases !== null)
          .map((r) => r.cases),
        type: "scatter",
        mode: "markers",
        marker: { color: "#934819", size: 7, symbol: "circle-open" },
        hoverinfo: "skip",
      },
    ],
    l,
    config,
  );
  if (token !== renderToken) return;
  const sl = layout();
  sl.showlegend = true;
  sl.legend = { orientation: "h", x: 0, y: 1.17 };
  sl.margin.t = 45;
  sl.xaxis = {
    ...sl.xaxis,
    title: { text: "Source epidemiological week" },
    range: [Math.max(0.5, state.first - 0.5), Math.min(53.5, state.last + 0.5)],
    dtick: state.last - state.first > 20 ? 8 : 2,
  };
  const traces = [];
  for (let year = state.start; year <= state.end; year++) {
    const rows = series.filter((r) => r.year === year);
    if (rows.length)
      traces.push({
        name: String(year),
        x: rows.map((r) => r.week),
        y: rows.map((r) => r.cases),
        type: "scatter",
        mode: "lines+markers",
        marker: { size: 3, color: colors[year] },
        connectgaps: false,
        line: {
          color: colors[year],
          width: 2,
          dash: { 2019: "solid", 2020: "dot", 2021: "dash", 2022: "dashdot" }[year],
        },
        hovertemplate: `${year} W%{x}<br>%{y:,} recorded cases<extra></extra>`,
      });
  }
  await Plotly.react($("seasonal"), traces, sl, config);
}
function renderTable() {
  latestSummary = summaries(data, state);
  const availability = annualAvailability(latestSummary);
  $("annual-availability").innerHTML = availability.length
    ? availability.map(({ year, present, expected }) => `
        <li><strong>${year}</strong><span class="availability-track" aria-hidden="true"><span style="width:${100 * present / expected}%"></span></span><span>${fmt(present)} of ${fmt(expected)} cells</span></li>`
      ).join("")
    : '<li class="empty-period">No weeks in this selection.</li>';
  latestWeekly = selectedRows(data, state).map((r) => ({
    ...r,
    snapshot_date: data.meta.snapshot_date,
    source_url: data.meta.source_url,
    time_basis: "source epidemiological week; onset/notification unresolved",
    location_basis: "occurrence/procedence",
    count_unit: "recorded cases",
  }));
  $("download").disabled = !latestSummary.length;
  $("download-weekly").disabled = !latestWeekly.length;
  const rowCount = latestSummary.length;
  $("table-description").textContent =
    `${fmt(rowCount)} department-year ${rowCount === 1 ? "summary" : "summaries"} for the selected weeks. The downloads include source identifiers and dates.`;
  const tableRows = latestSummary.map((r) => {
    const missing = r.cases === null;
    return `<tr${missing ? ' class="row-missing"' : ""}>
      <th scope="row">${escape(r.department_name)}</th><td>${r.year}</td>
      <td class="numeric${missing ? " value-missing" : ""}">${fmt(r.cases)}</td>
      <td class="numeric">${fmt(r.population_total)}</td>
      <td class="numeric${r.cases_per_100k === null ? " value-missing" : ""}">${dec(r.cases_per_100k)}</td>
      <td class="numeric">${r.source_present_weeks} / ${r.expected_weeks}</td>
    </tr>`;
  });
  $("summary-table").innerHTML = rowCount
    ? `<table><caption class="visually-hidden">Department-year summaries for event ${state.event}, ${state.start}–${state.end}, weeks ${state.first}–${state.last}.</caption>
       <thead><tr><th scope="col">Department</th><th scope="col">Year</th>
       <th scope="col" class="numeric">Recorded cases</th><th scope="col" class="numeric">Total residents</th>
       <th scope="col" class="numeric">Cases per 100,000 residents</th><th scope="col" class="numeric">Weeks with records / expected</th>
       </tr></thead><tbody>${tableRows.join("")}</tbody></table>`
    : '<div class="empty-state">No periods match this selection. Set the first year/week before the last, or use Reset.</div>';
  const total = sumPresent(latestSummary.map((r) => r.cases)),
    present = latestSummary.reduce((a, r) => a + r.source_present_weeks, 0),
    expected = latestSummary.reduce((a, r) => a + r.expected_weeks, 0);
  $("kpi-cases").textContent = fmt(total);
  $("kpi-availability").textContent = `${fmt(present)} / ${fmt(expected)}`;
  const singleYear = state.department !== "all" && state.start === state.end && rowCount === 1;
  $("selected-rate").hidden = !singleYear;
  $("kpi-rate").textContent = singleYear ? dec(latestSummary[0].cases_per_100k) : "";
  let interpretation;
  if (!expected) {
    interpretation = "The selected years and weeks contain no valid observation period.";
  } else if (total === null) {
    interpretation = "The source contains no records for these weeks. The number of cases is unknown.";
  } else if (present === expected) {
    interpretation = "Every selected department-week has a source record. The surveillance system may still have missed cases.";
  } else {
    interpretation = `The case count sums available records. ${fmt(expected - present)} of ${fmt(expected)} department-week cells have no source row.`;
  }
  $("scope-note").textContent = interpretation;
  $("provenance-content").innerHTML =
    `<ul><li>Surveillance: <a href="${data.meta.source_url}">INS / Sivigila historical aggregates</a>, CC BY-SA 4.0. Retrieved ${data.meta.snapshot_date}; dataset last updated ${data.meta.source_data_updated_utc.slice(0, 10)}.</li><li>Geography: 32 departments plus Bogotá D.C. District municipality records are included once in their parent department; foreign and unknown geography are excluded.</li><li>Time: source epidemiological year/week, 52 weeks in 2019/2021/2022 and 53 in 2020. The metadata does not settle symptom onset versus notification date.</li><li>Population: DANE’s 2025 revision, matched by department and year. Annual table rate = available cases ÷ annual total population × 100,000. A multiyear map shows the arithmetic mean of these yearly rates, and requires a usable numerator and denominator for every selected year. Restricting weeks does not annualize the result.</li><li>Case status: INS describes the routine series as confirmed notifications; this extract has no individual classification fields. Events 210 and 220 are shown separately.</li></ul>`;
}
async function render() {
  const current = ++renderToken;
  $("atlas").setAttribute("aria-busy", "true");
  const name =
    state.department === "all"
      ? "All department-level units"
      : data.departments.find((d) => d.code === state.department).name;
  $("selection-heading").textContent = name;
  const years = state.start === state.end ? state.start : `${state.start}–${state.end}`;
  const event = state.event === "210" ? "Dengue (210)" : "Severe dengue (220)";
  $("selection").textContent =
    `${event} · ${years} · Weeks ${state.first}–${state.last} · Map in ${state.metric === "rate" ? "cases per 100,000 residents" : "recorded cases"}`;
  for (const link of document.querySelectorAll(".example-links a")) {
    const current = [...new URLSearchParams(link.search)]
      .every(([key, value]) => String(state[key]) === value);
    if (current) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  renderMap();
  renderTable();
  await renderPlots();
  if (current === renderToken) {
    $("atlas").setAttribute("aria-busy", "false");
    window.atlasReady = true;
  }
}
async function boot() {
  const response = await fetch("data/atlas.json");
  if (!response.ok) throw Error(`Data request returned ${response.status}`);
  data = await response.json();
  rateMaxima = Object.fromEntries(
    ["210", "220"].map((event) => [event, rateScaleMaximum(data, event)]),
  );
  $("department").innerHTML =
    '<option value="all">All departments + Bogotá</option>' +
    data.departments
      .map((d) => `<option value="${d.code}">${escape(d.name)}</option>`)
      .join("");
  for (const id of ["year-start", "year-end"])
    $(id).innerHTML = [2019, 2020, 2021, 2022]
      .map((y) => `<option>${y}</option>`)
      .join("");
  state = readState(
    location.search,
    data.departments.map((d) => d.code),
  );
  setControls();
  $("filters").addEventListener("submit", (e) => e.preventDefault());
  for (const [k, id] of Object.entries(bindings))
    $(id).addEventListener("change", () => {
      state[k] =
        typeof defaults[k] === "number" ? Number($(id).value) : $(id).value;
      state = readState(
        new URLSearchParams(state),
        data.departments.map((d) => d.code),
      );
      setControls();
      history.pushState(null, "", stateUrl());
      render();
    });
  $("reset").addEventListener("click", () => {
    state = { ...defaults };
    setControls();
    history.pushState(null, "", location.pathname);
    render();
  });
  window.addEventListener("popstate", () => {
    state = readState(
      location.search,
      data.departments.map((d) => d.code),
    );
    setControls();
    render();
  });
  window
    .matchMedia("(max-width: 650px)")
    .addEventListener("change", () => renderPlots());
  $("download").addEventListener("click", () =>
    download(latestSummary, "summary"),
  );
  $("download-weekly").addEventListener("click", () =>
    download(latestWeekly, "weekly"),
  );
  await render();
}
boot().catch((e) => {
  $("app-error").hidden = false;
  $("app-error").textContent =
    `The atlas could not load. Reload the page or use the CSV files on Data & sources. Details: ${e.message}`;
  $("atlas").setAttribute("aria-busy", "false");
  console.error(e);
});
