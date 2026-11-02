"""Meaningful map invariants: common scale, honest missingness and source totals."""
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from scripts.cartographic_plate import aggregate_annual, shared_scale
from scripts import cartographic_plate as plate

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def inputs():
    processed = ROOT / "data/processed"
    return (
        pd.read_csv(processed / "surveillance_weekly.csv", dtype={"department_code": str, "event_code": str}),
        pd.read_csv(processed / "population.csv", dtype={"department_code": str}),
    )


def test_annual_table_preserves_all_units_and_audited_source_totals(inputs):
    table = aggregate_annual(*inputs)
    assert len(table) == 132
    assert table.groupby("year").department_code.nunique().eq(33).all()
    assert table.groupby("year").cases.sum().to_dict() == {
        2019: 122992, 2020: 76220, 2021: 49174, 2022: 65428,
    }
    assert table.groupby("year").available_weeks.sum().to_dict() == {
        2019: 1593, 2020: 1552, 2021: 1502, 2022: 1531,
    }
    assert table.groupby("year").expected_weeks.sum().to_dict() == {
        2019: 1716, 2020: 1749, 2021: 1716, 2022: 1716,
    }


def test_absent_bogota_stays_null_and_observed_zero_is_distinct(inputs):
    weekly, population = inputs
    original = aggregate_annual(weekly, population)
    absent = original.loc[original.department_code.eq("11")]
    assert absent.cases.isna().all() and absent.rate_per_100000.isna().all()
    assert absent.available_weeks.eq(0).all()
    assert absent.availability_status.eq("no_source_rows").all()
    # A real zero would count as an available observation, unlike an absent row.
    weekly.loc[(weekly.department_code == "11") & (weekly.year == 2019)
               & (weekly.week == 1) & (weekly.event_code == "210"), "cases"] = 0
    changed = aggregate_annual(weekly, population)
    zero = changed.loc[(changed.department_code == "11") & (changed.year == 2019)].iloc[0]
    assert zero.cases == 0 and zero.rate_per_100000 == 0
    assert zero.available_weeks == 1 and zero.missing_weeks == 51
    assert zero.availability_status == "partial_source_weeks"


def test_rate_uses_matching_year_population_and_shared_domain(inputs):
    table = aggregate_annual(*inputs)
    observed = table.loc[table.cases.notna()]
    np.testing.assert_allclose(observed.rate_per_100000,
                               observed.cases.astype(float) / observed.population * 100000)
    norm = shared_scale(table)
    assert norm.vmin == 0 and norm.vmax == 2500
    assert table.rate_per_100000.max() < norm.vmax
    # The domain is insensitive to row/year ordering; equal rates get the same
    # color coordinate, without rescaling each year's lower maximum to 1.0.
    reordered = shared_scale(table.iloc[::-1])
    assert norm(1000) == reordered(1000) == 0.4
    assert norm(table.loc[table.year == 2021, "rate_per_100000"].max()) < 1


def test_rejects_duplicate_cells_and_missing_denominators(inputs):
    weekly, population = inputs
    with pytest.raises(ValueError, match="Duplicate"):
        aggregate_annual(pd.concat([weekly, weekly.iloc[[0]]]), population)
    with pytest.raises(ValueError, match="matching population"):
        aggregate_annual(weekly, population.iloc[1:])


def test_rejects_broken_calendar_instead_of_shrinking_expected_weeks(inputs):
    weekly, population = inputs
    with pytest.raises(ValueError, match="calendar grid"):
        aggregate_annual(weekly.iloc[1:], population)


@pytest.fixture
def release_copy(tmp_path):
    """Use the real publication bundle, isolated from authoring artifacts."""
    names = [f"data/processed/{name}" for name in plate.INPUT_NAMES]
    names += ["scripts/cartographic_plate.py", "uv.lock", "data/processed/map_comparison.csv",
              "reports/cartographic_plate.json"]
    names += [f"figures/map-comparison.{ext}" for ext in ("svg", "png", "pdf")]
    for name in names:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    return tmp_path


def bundle_bytes(root):
    names = ["data/processed/map_comparison.csv", "reports/cartographic_plate.json"]
    names += [f"figures/map-comparison.{ext}" for ext in ("svg", "png", "pdf")]
    return {name: (root / name).read_bytes() for name in names}


def test_verified_release_reuse_needs_neither_renderer_nor_desktop_app(release_copy, monkeypatch):
    before = bundle_bytes(release_copy)
    assert b"\r\n" not in before["figures/map-comparison.svg"]
    assert b"\r\n" not in before["data/processed/map_comparison.csv"]
    def forbidden(*args, **kwargs):
        pytest.fail("Verified release reuse must not redraw or invoke Inkscape.")
    monkeypatch.setattr(plate, "draw_plate", forbidden)
    monkeypatch.setattr(plate.subprocess, "run", forbidden)
    report = plate.build_plate(release_copy)
    assert report["inkscape_export"]["version"].startswith("Inkscape 1.4.4")
    assert bundle_bytes(release_copy) == before


def test_checkout_line_endings_do_not_invalidate_verified_release(release_copy, monkeypatch):
    original = plate._build_fingerprint(release_copy)
    # Windows CRLF and Linux LF checkouts have the same processed text content.
    for name in original["files_sha256"]:
        path = release_copy / name
        text = path.read_text(encoding="utf-8")
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    assert plate._build_fingerprint(release_copy) == original
    monkeypatch.setattr(plate, "draw_plate", lambda *a, **k: pytest.fail("Unexpected redraw"))
    assert "inkscape_export" in plate.build_plate(release_copy)


@pytest.mark.parametrize("changed", ["data", "renderer", "lock", "png", "csv", "missing_pdf"])
def test_stale_or_tampered_bundle_blocks_publication(release_copy, changed):
    if changed == "data":
        path = release_copy / "data/processed/surveillance_weekly.csv"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(",114,observed_positive,", ",115,observed_positive,", 1), encoding="utf-8")
    elif changed in ("renderer", "lock"):
        path = release_copy / ("scripts/cartographic_plate.py" if changed == "renderer" else "uv.lock")
        path.write_bytes(path.read_bytes() + b"\n# Changed configuration\n")
    elif changed == "missing_pdf":
        (release_copy / "figures/map-comparison.pdf").unlink()
    else:
        path = release_copy / ("figures/map-comparison.png" if changed == "png"
                               else "data/processed/map_comparison.csv")
        path.write_bytes(path.read_bytes() + b"changed")
    before = {str(path.relative_to(release_copy)): path.read_bytes()
              for path in release_copy.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="--inkscape PATH"):
        plate.build_plate(release_copy)
    after = {str(path.relative_to(release_copy)): path.read_bytes()
             for path in release_copy.rglob("*") if path.is_file()}
    assert after == before


def test_failed_pdf_export_preserves_previous_complete_bundle(release_copy, monkeypatch):
    before = bundle_bytes(release_copy)
    def fake_run(command, **kwargs):
        if "--version" in command:
            return SimpleNamespace(stdout="Inkscape test version")
        if "--export-type=png" in command:
            destination = next(value.split("=", 1)[1] for value in command
                               if value.startswith("--export-filename="))
            Path(destination).write_bytes(b"staged export, not yet published")
            return SimpleNamespace(stdout="")
        raise subprocess.CalledProcessError(1, command, stderr="Simulated failed PDF export")
    monkeypatch.setattr(plate.subprocess, "run", fake_run)
    with pytest.raises(subprocess.CalledProcessError):
        plate.build_plate(release_copy, inkscape=Path("inkscape"))
    assert bundle_bytes(release_copy) == before
    assert not list(release_copy.glob(".map-plate-*"))


def test_first_svg_only_build_is_allowed_without_native_software(release_copy, monkeypatch):
    for name in bundle_bytes(release_copy):
        (release_copy / name).unlink()
    monkeypatch.setattr(plate.subprocess, "run", lambda *a, **k: pytest.fail("Unexpected native software"))
    report = plate.build_plate(release_copy)
    assert report["table_rows"] == 132 and "inkscape_export" not in report
    assert (release_copy / "figures/map-comparison.svg").exists()
    assert b"\r\n" not in (release_copy / "figures/map-comparison.svg").read_bytes()
    assert (release_copy / "data/processed/map_comparison.csv").exists()
    assert not (release_copy / "figures/map-comparison.png").exists()
    assert not (release_copy / "figures/map-comparison.pdf").exists()


def test_partial_filesystem_replacement_rolls_back_previous_files(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    staging.mkdir()
    pairs = []
    for index in range(2):
        source, destination = staging / f"new-{index}", tmp_path / f"published-{index}"
        source.write_text("new", encoding="utf-8")
        destination.write_text("previous", encoding="utf-8")
        pairs.append((source, destination))
    replace = plate.os.replace
    def fail_second(source, destination):
        if Path(source).name == "new-1":
            raise OSError("Simulated replacement failure")
        return replace(source, destination)
    monkeypatch.setattr(plate.os, "replace", fail_second)
    with pytest.raises(OSError, match="replacement failure"):
        plate._publish_staged(pairs, staging)
    assert all(destination.read_text(encoding="utf-8") == "previous" for _, destination in pairs)
