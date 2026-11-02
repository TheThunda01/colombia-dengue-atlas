"""Build pinned department populations and display geometry; never overwrite raw inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
YEARS = (2019, 2020, 2021, 2022)
EXPECTED_CODES = {
    "05", "08", "11", "13", "15", "17", "18", "19", "20", "23", "25",
    "27", "41", "44", "47", "50", "52", "54", "63", "66", "68", "70",
    "73", "76", "81", "85", "86", "88", "91", "94", "95", "97", "99",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_sources(download: bool = False) -> dict:
    manifest = json.loads((ROOT / "data/dane_sources.json").read_text(encoding="utf-8"))
    for item in manifest["inputs"]:
        path = ROOT / item["path"]
        if not path.exists():
            if not download:
                raise FileNotFoundError(f"Missing {path}; use --download to retrieve pinned inputs.")
            request = Request(item["url"], headers={"User-Agent": "colombia-dengue-atlas/1.0"})
            with urlopen(request, timeout=120) as response:
                content = response.read()
            if hashlib.sha256(content).hexdigest() != item["sha256"]:
                raise ValueError(f"Source changed: {item['path']}. Review a new version; pinned data were not replaced.")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        if sha256(path) != item["sha256"]:
            raise ValueError(f"Input fingerprint mismatch: {item['path']}")
    return manifest


def population_frame(path: Path) -> pd.DataFrame:
    """Select one total per department/year, excluding both constituent area rows."""
    table = pd.read_excel(path, sheet_name="PobDepartamentalxÁrea", header=7, dtype={"DP": str})
    table = table.loc[(table["ÁREA GEOGRÁFICA"] == "Total") & table["AÑO"].isin(YEARS)].copy()
    table = table.rename(columns={"DP": "department_code", "DPNOM": "department_name",
                                  "AÑO": "year", "TOTAL": "population"})
    table = table[["department_code", "department_name", "year", "population"]]
    table["year"] = table["year"].astype(int)
    table["population"] = table["population"].astype(int)
    if len(table) != 132 or table.duplicated(["department_code", "year"]).any():
        raise ValueError("Expected exactly 33 department-level units in each of four years")
    if not table.groupby("year").department_code.apply(lambda x: set(x) == EXPECTED_CODES).all():
        raise ValueError("Unexpected DANE codes")
    if (table.population <= 0).any() or table.isna().any().any():
        raise ValueError("Missing or invalid population denominator")
    table["population_unit"] = "persons"
    table["population_scope"] = "total resident population; not dengue population at risk"
    table["population_source"] = "DANE PPED 2025 revision, 2018-2050 department series"
    return table.sort_values(["year", "department_code"]).reset_index(drop=True)


def prepare(download: bool = False) -> dict:
    manifest = ensure_sources(download)
    raw = ROOT / "data/raw/dane"
    output = ROOT / "data/processed"
    output.mkdir(parents=True, exist_ok=True)
    population = population_frame(raw / "population.xlsx")
    population.to_csv(output / "population.csv", index=False)

    boundaries = gpd.read_file(raw / "departments.geojson")
    if len(boundaries) != 33 or set(boundaries.dpto_ccdgo) != EXPECTED_CODES:
        raise ValueError("Expected all 33 DANE department units, including Bogotá D.C.")
    if boundaries.dpto_ccdgo.duplicated().any() or set(boundaries.dpto_nano) != {2024, 2025}:
        raise ValueError("Duplicate code or unexpected map version")
    if boundaries.geometry.isna().any() or boundaries.geometry.is_empty.any():
        raise ValueError("Missing boundary geometry")
    if not boundaries.is_valid.all():
        raise ValueError("Source contains invalid geometry; review explicitly before repair")
    original_count = int(boundaries.geometry.count_coordinates().sum())
    # No geographic overlay is used to assign cases: codes control every join.
    # Simplification only reduces the download size for the display map.
    boundaries = boundaries.to_crs(9377)  # MAGNA-SIRGAS 2018 / Origen-Nacional, metres
    boundaries.geometry = boundaries.geometry.simplify(500, preserve_topology=True)
    boundaries = boundaries.to_crs(4326)
    boundaries = boundaries.rename(columns={"dpto_ccdgo": "department_code", "dpto_cnmbr": "boundary_name", "dpto_nano": "boundary_feature_update_year"})
    names = population.drop_duplicates("department_code").set_index("department_code").department_name
    boundaries["department_name"] = boundaries.department_code.map(names)
    boundaries["boundary_version"] = "DANE MGN2025; display geometry simplified 500 m"
    boundaries = boundaries[["department_code", "department_name", "boundary_name", "boundary_version", "boundary_feature_update_year", "geometry"]]
    boundaries = boundaries.sort_values("department_code").reset_index(drop=True)
    if not boundaries.is_valid.all() or boundaries.geometry.is_empty.any() or boundaries.department_name.isna().any():
        raise ValueError("Invalid simplified geometry or failed population join")
    geojson = json.loads(boundaries.to_json(drop_id=True))
    for feature in geojson["features"]:
        feature["id"] = feature["properties"]["department_code"]
    (output / "departments.geojson").write_text(json.dumps(geojson, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    report = {
        "population_rows": len(population), "department_units": 33, "years": list(YEARS),
        "unmatched_population_codes": [], "unmatched_boundary_codes": [],
        "population_missing_values": 0, "population_nonpositive_values": 0,
        "national_population_sums": {str(k): int(v) for k, v in population.groupby("year").population.sum().items()},
        "boundary_source_version": "MGN2025", "boundary_feature_update_years": [2024, 2025], "boundary_source_valid": True,
        "boundary_output_valid": True, "geometry_vertices_original": original_count,
        "geometry_vertices_simplified": int(boundaries.geometry.count_coordinates().sum()),
        "simplification_tolerance_m": 500, "simplification_crs": "EPSG:9377",
        "output_crs": "EPSG:4326", "source_retrieved_date": manifest["retrieved_date"],
        "limits": "Display boundaries are fixed MGN2025, not reconstructed annual historical boundaries. No polygon overlay assigns cases. Total-population rates are not INS population-at-risk incidence.",
    }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/geography_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download missing pinned inputs only; changed bytes fail closed")
    print(json.dumps(prepare(parser.parse_args().download), indent=2))
