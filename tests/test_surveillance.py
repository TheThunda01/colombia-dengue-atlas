"""Source reconciliation and failure tests for the pinned surveillance release.

Small synthetic inputs exist only in pytest temporary directories. They are never
written to data/raw, data/processed, or the published site.
"""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from scripts.prepare_surveillance import build


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


@pytest.fixture(scope="module")
def source_db():
    """Use SQL, independently of the production Counter/pandas aggregation."""
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE source(year INT, week INT, event INT, dept INT, municipality INT, cases INT)"
    )
    for year in range(2019, 2023):
        records = json.loads((RAW / f"ins_dengue_{year}.json").read_bytes())
        connection.executemany(
            "INSERT INTO source VALUES(?,?,?,?,?,?)",
            ((int(r["ano"]), int(r["semana"]), int(r["cod_eve"]),
              int(r["cod_dpto_o"]), int(r["cod_mun_o"]), int(r["conteo"])) for r in records),
        )
    yield connection
    connection.close()


@pytest.fixture(scope="module")
def published():
    return json.loads((PROCESSED / "surveillance_weekly.json").read_bytes())


def test_every_published_cell_reconciles_with_raw_sql(source_db, published):
    expected = {
        (year, week, dept, event): (cases, rows)
        for year, week, dept, event, cases, rows in source_db.execute(
            "SELECT year,week,dept,event,SUM(cases),COUNT(*) FROM source "
            "WHERE dept NOT IN(0,1) GROUP BY year,week,dept,event"
        )
    }
    seen = set()
    for record in published:
        key = (record["year"], record["week"], int(record["department_code"]), int(record["event_code"]))
        assert key not in seen, f"Duplicate output key: {key}"
        seen.add(key)
        cases, rows = expected.get(key, (None, 0))
        assert record["cases"] == cases, key
        assert record["source_rows"] == rows, key
        assert record["observation_status"] == (
            "source_absent" if cases is None else "explicit_zero" if cases == 0 else "observed_positive"
        ), key
    assert len(seen) == 13794
    assert set(expected).issubset(seen)
    assert len(expected) == 8130


@pytest.mark.parametrize("year,event,total,foreign,unknown", [
    (2019, 210, 122992, 643, 6), (2019, 220, 1339, 9, 0),
    (2020, 210, 76220, 199, 0), (2020, 220, 860, 2, 0),
    (2021, 210, 49174, 151, 0), (2021, 220, 932, 8, 0),
    (2022, 210, 65428, 263, 0), (2022, 220, 1330, 10, 0),
])
def test_pinned_year_event_totals_and_exclusions(source_db, published, year, event, total, foreign, unknown):
    source_totals = dict(source_db.execute(
        "SELECT dept,SUM(cases) FROM source WHERE year=? AND event=? GROUP BY dept", (year, event)
    ))
    assert sum(value for dept, value in source_totals.items() if dept not in (0, 1)) == total
    assert source_totals.get(1, 0) == foreign
    assert source_totals.get(0, 0) == unknown
    assert sum(r["cases"] for r in published
               if r["year"] == year and int(r["event_code"]) == event and r["cases"] is not None) == total


@pytest.mark.parametrize("municipality,parent", [(8001, 8), (13001, 13), (47001, 47), (76001, 76), (76109, 76)])
def test_district_is_in_parent_total_exactly_once(source_db, published, municipality, parent):
    assert source_db.execute(
        "SELECT DISTINCT dept FROM source WHERE municipality=?", (municipality,)
    ).fetchall() == [(parent,)]
    for year in range(2019, 2023):
        for event in (210, 220):
            district, rest = source_db.execute(
                "SELECT SUM(CASE WHEN municipality=? THEN cases ELSE 0 END),"
                "SUM(CASE WHEN municipality<>? THEN cases ELSE 0 END) "
                "FROM source WHERE year=? AND event=? AND dept=?",
                (municipality, municipality, year, event, parent),
            ).fetchone()
            assert district > 0  # Each audited district has actual observations in every selected year/event.
            published_parent = sum(
                r["cases"] for r in published if r["year"] == year and int(r["event_code"]) == event
                and int(r["department_code"]) == parent and r["cases"] is not None
            )
            assert published_parent == district + rest
            assert published_parent != 2 * district + rest


def test_sparse_source_and_geographic_grid(source_db, published):
    assert source_db.execute("SELECT COUNT(*),MIN(cases) FROM source").fetchone() == (57083, 1)
    assert source_db.execute(
        "SELECT COUNT(*) FROM (SELECT year,week,event,dept,municipality FROM source "
        "GROUP BY year,week,event,dept,municipality HAVING COUNT(*)>1)"
    ).fetchone()[0] == 0
    assert len({r["department_code"] for r in published}) == 33
    assert not {"00", "01"}.intersection(r["department_code"] for r in published)
    assert {r["event_code"] for r in published} == {"210", "220"}
    absent = [r for r in published if r["cases"] is None]
    assert len(absent) == 5664
    assert all(r["cases"] is None for r in published if r["department_code"] == "11")


def test_epidemiological_week_53_is_only_2020(source_db, published):
    assert source_db.execute(
        "SELECT year,MIN(week),MAX(week),COUNT(DISTINCT week) FROM source GROUP BY year"
    ).fetchall() == [(2019, 1, 52, 52), (2020, 1, 53, 53), (2021, 1, 52, 52), (2022, 1, 52, 52)]
    assert {r["year"] for r in published if r["week"] == 53} == {2020}
    assert len([r for r in published if r["week"] == 53]) == 66
    assert all(1 <= r["week"] <= (53 if r["year"] == 2020 else 52) for r in published)


def test_offline_rebuild_preserves_source_and_reproduces_outputs(tmp_path, monkeypatch):
    from scripts import prepare_surveillance

    def unexpected_network(*args, **kwargs):
        raise AssertionError("The pinned rebuild must not require network access")

    monkeypatch.setattr(prepare_surveillance.urllib.request, "urlopen", unexpected_network)
    paths = sorted(RAW.glob("ins_*.json"))
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    build(RAW, tmp_path / "rebuilt")
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert before == after
    for filename in ("surveillance_weekly.json", "surveillance_weekly.csv", "surveillance_audit.json"):
        assert (tmp_path / "rebuilt" / filename).read_bytes() == (PROCESSED / filename).read_bytes(), filename


def write_fixture_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def update_fixture_manifest(directory):
    """This helper hashes synthetic fixtures only, never release data."""
    files = [{"filename": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
             for path in sorted(directory.glob("ins_*.json")) if path.name != "ins_manifest.json"]
    write_fixture_json(directory / "ins_manifest.json", {
        "source_id": "SYNTHETIC-TEST-ONLY", "snapshot_date": "2000-01-01", "files": files,
    })


@pytest.fixture
def synthetic_source(tmp_path):
    """A deliberately tiny test-only source with explicit zero and absent weeks."""
    directory = tmp_path / "synthetic-not-surveillance"
    directory.mkdir()
    for year in range(2019, 2023):
        write_fixture_json(directory / f"ins_dengue_{year}.json", [])
    example = {"ano": "2019", "semana": "1", "cod_eve": "210", "cod_dpto_o": "5",
               "cod_mun_o": "5001", "nombre_evento": "SYNTHETIC TEST DENGUE",
               "departamento_ocurrencia": "SYNTHETIC TEST", "municipio_ocurrencia": "SYNTHETIC TEST",
               "conteo": "0"}
    write_fixture_json(directory / "ins_dengue_2019.json", [
        example, {**example, "semana": "2", "conteo": "7"},
        {**example, "cod_eve": "220", "nombre_evento": "SYNTHETIC TEST SEVERE", "conteo": "2"},
    ])
    # Hand-specified expectations, independent of the production aggregation.
    write_fixture_json(directory / "ins_independent_weekly_totals.json", [
        {"ano": "2019", "semana": "1", "cod_dpto_o": "5", "cod_eve": "210", "cases": "0", "source_rows": "1"},
        {"ano": "2019", "semana": "2", "cod_dpto_o": "5", "cod_eve": "210", "cases": "7", "source_rows": "1"},
        {"ano": "2019", "semana": "1", "cod_dpto_o": "5", "cod_eve": "220", "cases": "2", "source_rows": "1"},
    ])
    write_fixture_json(directory / "ins_metadata.json", {
        "name": "SYNTHETIC TEST ONLY", "attribution": "pytest temporary fixture",
        "rowsUpdatedAt": 0, "licenseId": "CC_40_BY_SA",
    })
    update_fixture_manifest(directory)
    return directory


def test_explicit_zero_remains_distinct_from_absence_in_json_and_csv(synthetic_source, tmp_path):
    output = tmp_path / "synthetic-output"
    build(synthetic_source, output)
    records = json.loads((output / "surveillance_weekly.json").read_bytes())
    sample = {r["week"]: r for r in records
              if r["year"] == 2019 and r["department_code"] == "05" and r["event_code"] == "210"}
    assert (sample[1]["cases"], sample[1]["observation_status"], sample[1]["source_rows"]) == (0, "explicit_zero", 1)
    assert (sample[2]["cases"], sample[2]["observation_status"]) == (7, "observed_positive")
    assert (sample[3]["cases"], sample[3]["observation_status"], sample[3]["source_rows"]) == (None, "source_absent", 0)
    with (output / "surveillance_weekly.csv").open(encoding="utf-8", newline="") as handle:
        csv_sample = {int(r["week"]): r for r in csv.DictReader(handle)
                      if r["year"] == "2019" and r["department_code"] == "05" and r["event_code"] == "210"}
    assert csv_sample[1]["cases"] == "0"
    assert csv_sample[3]["cases"] == ""
    assert sum(r["cases"] for r in records if r["event_code"] == "210" and r["cases"] is not None) == 7
    assert sum(r["cases"] for r in records if r["event_code"] == "220" and r["cases"] is not None) == 2


@pytest.mark.parametrize("mutation,message", [
    ("duplicate", "Duplicate municipality-week-event"),
    ("wrong_department", "Municipal identifier does not match department"),
    ("invalid_week", "Unexpected year, event, or epidemiological week"),
    ("negative_count", "Count is not a nonnegative integer"),
    ("wrong_remote_sum", "Local sums disagree"),
    ("changed_bytes", "Source fingerprint mismatch"),
    ("changed_license", "Expected CC BY-SA 4.0"),
])
def test_source_risks_fail_closed(synthetic_source, tmp_path, mutation, message):
    path = synthetic_source / "ins_dengue_2019.json"
    records = json.loads(path.read_bytes())
    if mutation == "duplicate":
        records.append(records[0].copy())
    elif mutation == "wrong_department":
        records[0]["cod_dpto_o"] = "8"
    elif mutation == "invalid_week":
        records[0]["semana"] = "53"  # 2019 does not have week 53 in the selected source.
    elif mutation == "negative_count":
        records[0]["conteo"] = "-1"
    elif mutation in {"wrong_remote_sum", "changed_bytes"}:
        records[0]["conteo"] = "99"
    elif mutation == "changed_license":
        metadata_path = synthetic_source / "ins_metadata.json"
        metadata = json.loads(metadata_path.read_bytes())
        metadata["licenseId"] = "ALL-RIGHTS-RESERVED"
        write_fixture_json(metadata_path, metadata)
    write_fixture_json(path, records)
    if mutation != "changed_bytes":
        update_fixture_manifest(synthetic_source)
    with pytest.raises(ValueError, match=message):
        build(synthetic_source, tmp_path / "should-not-be-published")
