// One pure data model drives the on-screen summaries and both CSV exports.
export const defaults = {
  department: "all",
  event: "210",
  start: 2019,
  end: 2022,
  first: 1,
  last: 53,
  metric: "cases",
};
export function readState(search, departments) {
  const p = new URLSearchParams(search),
    s = { ...defaults };
  for (const k of Object.keys(s))
    if (p.has(k)) s[k] = typeof s[k] === "number" ? Number(p.get(k)) : p.get(k);
  for (const k of ["start", "end"])
    if (!Number.isInteger(s[k]) || s[k] < 2019 || s[k] > 2022)
      s[k] = defaults[k];
  for (const k of ["first", "last"])
    if (!Number.isInteger(s[k]) || s[k] < 1 || s[k] > 53) s[k] = defaults[k];
  if (!departments.includes(s.department)) s.department = "all";
  if (!["210", "220"].includes(s.event)) s.event = "210";
  if (!["cases", "rate"].includes(s.metric)) s.metric = "cases";
  return s;
}
export function sumPresent(values) {
  const present = values.filter((v) => v !== null && Number.isFinite(v));
  return present.length ? present.reduce((a, b) => a + b, 0) : null;
}
export function selectedRows(data, s, context = false) {
  return data.rows.filter(
    (r) =>
      r.event_code === s.event &&
      r.year >= s.start &&
      r.year <= s.end &&
      r.week >= s.first &&
      r.week <= s.last &&
      (context || s.department === "all" || r.department_code === s.department),
  );
}
export function summaries(data, s, context = false) {
  const groups = new Map();
  for (const r of selectedRows(data, s, context)) {
    const key = `${r.department_code}-${r.year}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(r);
  }
  return [...groups.values()]
    .map((rows) => {
      const r = rows[0],
        cases = sumPresent(rows.map((x) => x.cases));
      const population =
        data.population[`${r.department_code}-${r.year}`] ?? null;
      const observed = rows.filter((x) => x.cases !== null).length;
      return {
        department_code: r.department_code,
        department_name: r.department_name,
        year: r.year,
        event_code: r.event_code,
        event_name: r.event_name,
        first_week: s.first,
        last_week: s.last,
        actual_first_week: Math.min(...rows.map((x) => x.week)),
        actual_last_week: Math.max(...rows.map((x) => x.week)),
        cases,
        population_total: population,
        cases_per_100k:
          cases === null || !population ? null : (cases / population) * 1e5,
        source_present_weeks: observed,
        source_absent_weeks: rows.length - observed,
        expected_weeks: rows.length,
        explicit_zero_weeks: rows.filter((x) => x.cases === 0).length,
        availability:
          observed === 0
            ? "no_source_rows"
            : observed === rows.length
              ? "all_week_cells_present"
              : "partial_week_cells",
        count_unit: "recorded cases in available source rows",
        rate_unit: "selected-week recorded cases per 100000 total residents",
        time_basis:
          "source epidemiological year and week; onset/notification basis unresolved",
        location_basis: "source occurrence/procedence department",
        source_id: data.meta.source_id,
        snapshot_date: data.meta.snapshot_date,
        source_data_updated_utc: data.meta.source_data_updated_utc,
        population_version: "DANE 2025 revision",
        source_url: data.meta.source_url,
      };
    })
    .sort(
      (a, b) =>
        a.department_name.localeCompare(b.department_name, "es") ||
        a.year - b.year,
    );
}
export function mapSummaries(data, s) {
  const annual = summaries(data, s, true),
    years = s.end - s.start + 1;
  return data.departments.map((d) => {
    const rows = annual.filter((r) => r.department_code === d.code);
    const valid = rows.map((r) => r.cases_per_100k).filter((v) => v !== null);
    return {
      ...d,
      cases: sumPresent(rows.map((r) => r.cases)),
      rate:
        years > 0 && valid.length === years
          ? valid.reduce((a, b) => a + b, 0) / years
          : null,
      present: rows.reduce((a, r) => a + r.source_present_weeks, 0),
      expected: rows.reduce((a, r) => a + r.expected_weeks, 0),
    };
  });
}
export function timeSeries(data, s) {
  const groups = new Map();
  for (const r of selectedRows(data, s)) {
    const key = `${r.year}-W${String(r.week).padStart(2, "0")}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(r);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([label, rows]) => ({
      label,
      year: rows[0].year,
      week: rows[0].week,
      cases: sumPresent(rows.map((r) => r.cases)),
      present: rows.filter((r) => r.cases !== null).length,
      expected: rows.length,
    }));
}
export function csv(rows) {
  if (!rows.length) return "";
  const fields = Object.keys(rows[0]);
  const cell = (v) => {
    let t = v === null || v === undefined ? "" : String(v);
    if (/^[=+@\t\r]/.test(t)) t = "'" + t;
    return '"' + t.replaceAll('"', '""') + '"';
  };
  return (
    [
      fields.map(cell).join(","),
      ...rows.map((r) => fields.map((k) => cell(r[k])).join(",")),
    ].join("\r\n") + "\r\n"
  );
}
