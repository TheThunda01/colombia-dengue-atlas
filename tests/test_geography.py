"""Checks against inspected DANE cells and the published geometry contract."""
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

from scripts.prepare_geography import EXPECTED_CODES

ROOT = Path(__file__).resolve().parents[1]


def test_population_has_exact_department_year_keys():
    data = pd.read_csv(ROOT / "data/processed/population.csv", dtype={"department_code": str})
    assert len(data) == 132
    assert not data.duplicated(["department_code", "year"]).any()
    assert not data.isna().any().any()
    assert (data.population > 0).all()
    assert set(data.year) == {2019, 2020, 2021, 2022}
    for _, group in data.groupby("year"):
        assert set(group.department_code) == EXPECTED_CODES


def test_population_matches_representative_original_total_cells():
    data = pd.read_csv(ROOT / "data/processed/population.csv", dtype={"department_code": str})
    indexed = data.set_index(["department_code", "year"]).population
    # Directly inspected Total rows: full departments include their districts.
    assert indexed.loc[("08", 2019)] == 2_608_908
    assert indexed.loc[("13", 2020)] == 2_151_461
    assert indexed.loc[("47", 2021)] == 1_463_123
    assert indexed.loc[("76", 2022)] == 4_658_811
    assert indexed.loc[("11", 2022)] == 7_849_206


def test_map_preserves_identifiers_and_small_island_geometry():
    path = ROOT / "data/processed/departments.geojson"
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    assert len(features) == 33
    assert {f["id"] for f in features} == EXPECTED_CODES
    assert all(f["id"] == f["properties"]["department_code"] for f in features)
    frame = gpd.read_file(path)
    assert frame.is_valid.all()
    assert not frame.geometry.is_empty.any()
    assert (frame.to_crs(9377).area > 0).all()
    assert len(frame.loc[frame.department_code == "88"]) == 1
    assert len(frame.loc[frame.department_code == "11"]) == 1
