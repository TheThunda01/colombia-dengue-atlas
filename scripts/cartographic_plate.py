"""Build a comparable four-year map plate from the pinned, processed inputs.

The default verifies and reuses the committed publication bundle without a
desktop dependency. With no existing PNG/PDF exports, it can create SVG/CSV only.
Pass --inkscape PATH to refresh the whole bundle with the free application's
command-line exporter. Changed inputs or stale exports stop publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
YEARS = (2019, 2020, 2021, 2022)
EVENT_CODE = "210"
EXPECTED_WEEKS = {2019: 52, 2020: 53, 2021: 52, 2022: 52}
INK = "#173d49"
MUTED = "#52696e"
PAPER = "#fcfcf9"
INPUT_NAMES = ("surveillance_weekly.csv", "population.csv", "departments.geojson", "surveillance_audit.json")


def aggregate_annual(weekly: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    """Sum available rows, keeping an entirely absent department/year null.

    The processed surveillance input is a calendar grid, so ``size`` measures
    expected weeks and ``count`` measures non-null source-week observations.
    Neither quantity establishes reporting completeness or infection capture.
    """
    selected = weekly.loc[
        weekly.event_code.astype(str).eq(EVENT_CODE) & weekly.year.isin(YEARS)
    ].copy()
    selected["department_code"] = selected.department_code.astype(str).str.zfill(2)
    if selected.duplicated(["department_code", "year", "week"]).any():
        raise ValueError("Duplicate department/year/week cells would double-count cases.")
    if selected.cases.dropna().lt(0).any():
        raise ValueError("Recorded cases must be nonnegative.")
    for year, cells in selected.groupby("year"):
        if not cells.week.between(1, EXPECTED_WEEKS[year]).all():
            raise ValueError(f"Invalid source epidemiological week for {year}.")

    annual = selected.groupby(["department_code", "year"], as_index=False).agg(
        cases=("cases", lambda values: values.sum(min_count=1)),
        available_weeks=("cases", "count"),
        expected_weeks=("cases", "size"),
    )
    expected = annual.year.map(EXPECTED_WEEKS)
    if not annual.expected_weeks.eq(expected).all():
        raise ValueError("The processed surveillance calendar grid is incomplete.")

    denominators = population.loc[population.year.isin(YEARS)].copy()
    denominators["department_code"] = denominators.department_code.astype(str).str.zfill(2)
    if denominators.duplicated(["department_code", "year"]).any():
        raise ValueError("Population must have one denominator per department/year.")
    if denominators.population.isna().any() or denominators.population.le(0).any():
        raise ValueError("Population denominators must be present and positive.")
    result = annual.merge(
        denominators[["department_code", "department_name", "year", "population"]],
        on=["department_code", "year"], how="outer", validate="one_to_one", indicator=True,
    )
    if not result._merge.eq("both").all():
        raise ValueError("Every annual surveillance cell needs a matching population denominator.")
    result = result.drop(columns="_merge")
    result["event_code"] = EVENT_CODE
    result["cases"] = result.cases.astype("Int64")
    result["population"] = result.population.astype("int64")
    result["rate_per_100000"] = result.cases.astype(float) / result.population * 100_000
    result["missing_weeks"] = result.expected_weeks - result.available_weeks
    result["availability_fraction"] = result.available_weeks / result.expected_weeks
    result["availability_status"] = np.select(
        [result.available_weeks.eq(0), result.available_weeks.eq(result.expected_weeks)],
        ["no_source_rows", "all_source_weeks_present"], default="partial_source_weeks",
    )
    return result[[
        "department_code", "department_name", "year", "event_code", "cases", "population",
        "rate_per_100000", "available_weeks", "expected_weeks", "missing_weeks",
        "availability_fraction", "availability_status",
    ]].sort_values(["year", "department_code"]).reset_index(drop=True)


def shared_scale(table: pd.DataFrame) -> Normalize:
    """One linear domain for all panels; zero stays the same color in every year."""
    maximum = table.rate_per_100000.max()
    if pd.isna(maximum):
        raise ValueError("At least one observed rate is needed to draw the map plate.")
    upper = max(500.0, float(np.ceil(maximum / 500) * 500))
    return Normalize(vmin=0, vmax=upper, clip=False)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_fingerprint(root: Path) -> dict:
    """Ignore checkout line endings, but detect any input/code/lock-file edit.

    These are processed text files, not original downloads. Raw source integrity
    remains byte-exact in the source preparation pipeline. LF normalization here
    lets the same reviewed release work on Windows and on Linux CI.
    """
    names = [f"data/processed/{name}" for name in INPUT_NAMES]
    names.extend(["scripts/cartographic_plate.py", "uv.lock"])
    hashes = {name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
              for name in names}
    canonical = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"algorithm": "sha256-lf-text-v1", "files_sha256": hashes,
            "sha256": hashlib.sha256(canonical).hexdigest()}


def _verify_release(root: Path, previous: dict, fingerprint: dict, csv_bytes: bytes) -> list[str]:
    """Return actionable mismatches; never silently bless an old PNG/PDF pair."""
    problems = []
    if previous.get("build_fingerprint") != fingerprint:
        problems.append("processed inputs, renderer, or dependency lock changed")
    csv_hash = hashlib.sha256(csv_bytes).hexdigest()
    csv_path = root / "data/processed/map_comparison.csv"
    if (previous.get("csv_sha256") != csv_hash or not csv_path.exists()
            or _sha256(csv_path) != csv_hash):
        problems.append("annual CSV differs from the freshly calculated table")
    evidence = previous.get("inkscape_export", {})
    svg_path = root / "figures/map-comparison.svg"
    svg_hash = previous.get("svg_sha256")
    if (not svg_hash or not svg_path.exists() or _sha256(svg_path) != svg_hash
            or evidence.get("source_svg_sha256") != svg_hash):
        problems.append("editable SVG does not match the recorded Inkscape source")
    hashes = evidence.get("files_sha256", {})
    if set(hashes) != {"map-comparison.png", "map-comparison.pdf"}:
        problems.append("complete Inkscape export evidence is missing")
    else:
        for name, digest in hashes.items():
            path = root / "figures" / name
            if not path.exists() or _sha256(path) != digest:
                problems.append(f"{name} is missing or changed")
    return problems


def _publish_staged(pairs: list[tuple[Path, Path]], staging: Path) -> None:
    """Replace validated files individually, rolling back a partial replacement.

    The filesystem cannot atomically exchange several unrelated files at once.
    All expensive work therefore finishes first; replacements are atomic per
    file, and an ordinary replacement failure restores the previous bundle.
    """
    backups = {}
    for index, (_, destination) in enumerate(pairs):
        if destination.exists():
            backup = staging / f"backup-{index}"
            shutil.copy2(destination, backup)
            backups[destination] = backup
    published = []
    try:
        for source, destination in pairs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(source, destination)
            published.append(destination)
    except OSError:
        for destination in reversed(published):
            if destination in backups:
                os.replace(backups[destination], destination)
            else:
                destination.unlink(missing_ok=True)
        raise


def draw_plate(table: pd.DataFrame, geometry: gpd.GeoDataFrame, destination: Path,
               snapshot_date: str) -> dict:
    """Render the same geometry and the same color normalization in all panels."""
    projected = geometry.to_crs(9377)
    if projected.department_code.duplicated().any():
        raise ValueError("The map requires one geometry per department code.")
    if set(projected.department_code) != set(table.department_code):
        raise ValueError("Map geometry and annual table department codes do not match.")
    norm = shared_scale(table)
    cmap = LinearSegmentedColormap.from_list(
        "atlas_sequential", ["#eef5ed", "#a4d6bd", "#4fa99e", "#187879", "#12434f"]
    )
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10, "svg.fonttype": "none",
        "svg.hashsalt": "colombia-dengue-atlas-map-v1", "hatch.linewidth": 0.55,
    })
    fig = plt.figure(figsize=(13, 14.8), facecolor=PAPER)
    fig.text(.065, .963, "Dengue across Colombia", color=INK, fontsize=29, weight="bold")
    fig.text(.065, .936, "Four surveillance years, one shared color scale", color=INK, fontsize=16)
    fig.text(.065, .911, "INS event 210  ·  Annual recorded cases per 100,000 total residents  ·  2019–2022",
             color=MUTED, fontsize=11)
    xmin, ymin, xmax, ymax = projected.total_bounds
    dx, dy = xmax - xmin, ymax - ymin
    bounds = (xmin - dx * .035, xmax + dx * .035, ymin - dy * .025, ymax + dy * .025)
    panel_reports = []

    for index, year in enumerate(YEARS):
        left = .065 if index % 2 == 0 else .535
        bottom = .55 if index < 2 else .215
        title_y = .878 if index < 2 else .543
        values = table.loc[table.year.eq(year)]
        mapped = projected.merge(values, on="department_code", validate="one_to_one")
        ax = fig.add_axes([left, bottom, .40, .28], facecolor=PAPER)
        ax.set_xlim(bounds[:2]); ax.set_ylim(bounds[2:]); ax.set_aspect("equal"); ax.axis("off")
        observed = mapped.loc[mapped.rate_per_100000.notna()]
        absent = mapped.loc[mapped.rate_per_100000.isna()]
        observed.plot(ax=ax, column="rate_per_100000", cmap=cmap, norm=norm,
                      edgecolor="#ffffff", linewidth=.45, zorder=2)
        absent.plot(ax=ax, facecolor="#eee9df", edgecolor="#66777b", hatch="////",
                    linewidth=.55, zorder=3)
        projected.boundary.plot(ax=ax, color="#627b7d", linewidth=.23, zorder=4)
        # Names and leaders keep small units discoverable without moving or
        # enlarging their polygons. All maps share the original coordinates.
        for code, label, text_position, alignment in [
            ("88", "San Andrés &\nProvidencia", (.04, .88), "left"),
            ("11", "Bogotá\nNo source rows", (.17, .48), "right"),
        ]:
            point = projected.loc[projected.department_code.eq(code)].geometry.iloc[0].representative_point()
            ax.annotate(label, xy=(point.x, point.y), xytext=text_position,
                        textcoords="axes fraction", fontsize=8, color=MUTED,
                        ha=alignment, va="center", linespacing=1.35,
                        arrowprops={"arrowstyle": "-", "color": "#7c8d8e", "lw": .6,
                                    "connectionstyle": "angle,angleA=0,angleB=90,rad=0"}, zorder=5)
        count = int(values.cases.sum(min_count=1))
        available, expected = int(values.available_weeks.sum()), int(values.expected_weeks.sum())
        partial = int(values.availability_status.eq("partial_source_weeks").sum())
        fig.text(left, title_y, f"{chr(65 + index)}   {year}", fontsize=19, weight="bold", color=INK)
        fig.text(left, title_y - .020, f"{count:,} recorded cases", fontsize=11.5, color=INK)
        fig.text(left, title_y - .030,
                 f"Source rows: {available:,}/{expected:,} department-weeks\n"
                 f"{partial} units have partial weeks; {len(absent)} has no rows", fontsize=8.6,
                 color=MUTED, linespacing=1.45, va="top")
        panel_reports.append({"year": year, "mapped_units": len(mapped), "cases": count,
                              "available_department_weeks": available,
                              "expected_department_weeks": expected,
                              "units_with_partial_source_weeks": partial,
                              "units_with_no_source_rows": len(absent),
                              "color_vmin": norm.vmin, "color_vmax": norm.vmax})

    fig.text(.065, .188, "Recorded cases per 100,000 total residents", fontsize=11, color=INK, weight="bold")
    colorbar_axis = fig.add_axes([.065, .165, .50, .012])
    colorbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=colorbar_axis,
                           orientation="horizontal", ticks=np.arange(0, norm.vmax + 1, 500))
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(labelsize=9, length=2, colors=MUTED)
    fig.text(.615, .174, "Same linear scale in every panel", fontsize=10, color=INK)
    fig.text(.615, .156, "Lighter = lower recorded rate", fontsize=9, color=MUTED)
    fig.legend(handles=[Patch(facecolor="#eee9df", edgecolor="#66777b", hatch="////",
                              label="No source rows (Bogotá); not a zero")],
               loc="center left", bbox_to_anchor=(.058, .130), frameon=False, fontsize=9)
    fig.text(.065, .115,
             "Rates use the sum of available weeks ÷ that year's DANE population × 100,000. "
             "Partial source rows can lower the recorded totals.\n"
             "Row availability is not reporting completeness. These are descriptive normalized records, "
             "not official incidence in a population at risk.",
             fontsize=8.5, color=MUTED, linespacing=1.65, va="top")
    fig.text(.065, .074,
             "Sources: INS / Sivigila, datos.gov.co/4hyg-wa9d (CC BY-SA 4.0); "
             "DANE PPED 2025 population revision; DANE MGN2025 boundaries.\n"
             f"Snapshot: {snapshot_date}. Fixed 2025 reference geometry, simplified 500 m; "
             "EPSG:9377. Islands remain at their actual coordinates.\n"
             "33 units = 32 departments + Bogotá. Event 220 (severe dengue) is separate. "
             "Source week 53 exists only in 2020. Figure: Brandon Huynh.",
             fontsize=8, color=MUTED, linespacing=1.65, va="top")
    fig.savefig(destination, facecolor=PAPER, metadata={
        "Creator": "Brandon Huynh; Colombia Dengue Surveillance Atlas",
        "Date": snapshot_date,
        "Description": "Four annual maps; common linear rate scale; absent source cells remain missing.",
    })
    # Matplotlib can emit CRLF on Windows. Git stores this text artifact as LF,
    # so normalize before Inkscape reads it or any source/export hash is made.
    destination.write_text(destination.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    plt.close(fig)
    return {"projection": "EPSG:9377", "color_scale": {"type": "linear", "min": norm.vmin,
            "max": norm.vmax, "shared_across_panels": True}, "panels": panel_reports}


def build_plate(root: Path = ROOT, inkscape: Path | None = None) -> dict:
    """Verify a release bundle, or stage a new one through Inkscape's CLI."""
    root = Path(root).resolve()
    processed = root / "data/processed"
    weekly = pd.read_csv(processed / "surveillance_weekly.csv",
                         dtype={"department_code": str, "event_code": str})
    population = pd.read_csv(processed / "population.csv", dtype={"department_code": str})
    metadata = json.loads((processed / "surveillance_audit.json").read_text(encoding="utf-8"))
    table = aggregate_annual(weekly, population)
    if len(table) != 132 or table.department_code.nunique() != 33:
        raise ValueError("The pinned plate requires 132 department-years across 33 map units.")
    figures = root / "figures"
    csv = processed / "map_comparison.csv"
    csv_bytes = table.to_csv(index=False, float_format="%.12g", na_rep="", lineterminator="\n").encode("utf-8")
    svg = figures / "map-comparison.svg"
    report_path = root / "reports/cartographic_plate.json"
    previous = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    fingerprint = _build_fingerprint(root)
    has_exports = "inkscape_export" in previous or any(svg.with_suffix(f".{ext}").exists() for ext in ("png", "pdf"))
    if inkscape is None and has_exports:
        problems = _verify_release(root, previous, fingerprint, csv_bytes)
        if problems:
            raise ValueError("Publication map exports need regeneration: " + "; ".join(problems)
                             + ". Run uv run python scripts/cartographic_plate.py --inkscape PATH. "
                             "The existing bundle has not been changed.")
        # Keep the exact reviewed SVG/PNG/PDF bundle: platform-specific font or
        # rendering changes must not mix a fresh SVG with an older raster/PDF.
        return previous

    geometry = gpd.read_file(processed / "departments.geojson")
    with tempfile.TemporaryDirectory(prefix=".map-plate-", dir=root) as directory:
        staging = Path(directory)
        staged_csv, staged_svg = staging / csv.name, staging / svg.name
        staged_csv.write_bytes(csv_bytes)
        report = draw_plate(table, geometry, staged_svg, metadata["snapshot_date"])
        report.update({
            "event_code": EVENT_CODE, "years": list(YEARS), "table_rows": len(table),
            "null_case_and_rate_rows": int(table.cases.isna().sum()),
            "semantics": "Available source rows only; absent cells are not zeros; row presence is not reporting completeness.",
            "inputs_sha256": {name: _sha256(processed / name) for name in INPUT_NAMES},
            "build_fingerprint": fingerprint,
            "svg_sha256": _sha256(staged_svg), "csv_sha256": _sha256(staged_csv),
        })
        pairs = [(staged_csv, csv), (staged_svg, svg)]
        if inkscape is not None:
            version = subprocess.run([str(inkscape), "--version"], check=True, capture_output=True,
                                     text=True, encoding="utf-8").stdout.strip()
            exported = {}
            for extension in ("png", "pdf"):
                destination = staged_svg.with_suffix(f".{extension}")
                command = [str(inkscape), str(staged_svg), f"--export-type={extension}",
                           f"--export-filename={destination}", "--export-area-page"]
                if extension == "png":
                    command.append("--export-dpi=240")
                subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
                # Successful exit alone is insufficient if an export is absent
                # or empty. Do not publish a half-refreshed artifact bundle.
                if not destination.exists() or destination.stat().st_size == 0:
                    raise ValueError(f"Inkscape did not create a nonempty {extension.upper()} export.")
                exported[destination.name] = _sha256(destination)
                pairs.append((destination, figures / destination.name))
            report["inkscape_export"] = {"version": version, "source_svg_sha256": report["svg_sha256"],
                                          "png_dpi": 240, "files_sha256": exported}
        staged_report = staging / report_path.name
        staged_report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8", newline="\n")
        pairs.append((staged_report, report_path))
        _publish_staged(pairs, staging)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inkscape", type=Path, help="Path to the Inkscape executable; exports PNG/PDF")
    args = parser.parse_args()
    report = build_plate(inkscape=args.inkscape)
    if args.inkscape:
        print(f"Refreshed {report['table_rows']} annual rows, editable SVG and Inkscape PNG/PDF.")
    elif "inkscape_export" in report:
        print(f"Verified {report['table_rows']} annual rows; reused the complete publication bundle.")
    else:
        print(f"Built {report['table_rows']} annual rows and editable SVG; no publication PNG/PDF exports yet.")


if __name__ == "__main__":
    main()
