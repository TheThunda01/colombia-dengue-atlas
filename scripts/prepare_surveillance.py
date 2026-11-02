"""Build department/week aggregates from pinned, licensed INS public aggregates.

Default execution is offline. --fetch-to DIR downloads a candidate snapshot into a
new directory; review it before deliberately replacing the release snapshot.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "ins-socrata-4hyg-wa9d"
API = "https://www.datos.gov.co/resource/4hyg-wa9d.json"
YEARS = (2019, 2020, 2021, 2022)
WEEKS = {2019: 52, 2020: 53, 2021: 52, 2022: 52}
EVENTS = {"210": "Dengue", "220": "Severe dengue"}
DEPARTMENTS = {
    "05": "Antioquia", "08": "Atlántico", "11": "Bogotá, D.C.",
    "13": "Bolívar", "15": "Boyacá", "17": "Caldas", "18": "Caquetá",
    "19": "Cauca", "20": "Cesar", "23": "Córdoba", "25": "Cundinamarca",
    "27": "Chocó", "41": "Huila", "44": "La Guajira", "47": "Magdalena",
    "50": "Meta", "52": "Nariño", "54": "Norte de Santander",
    "63": "Quindío", "66": "Risaralda", "68": "Santander", "70": "Sucre",
    "73": "Tolima", "76": "Valle del Cauca", "81": "Arauca",
    "85": "Casanare", "86": "Putumayo", "88": "San Andrés y Providencia",
    "91": "Amazonas", "94": "Guainía", "95": "Guaviare", "97": "Vaupés",
    "99": "Vichada",
}
DISTRICTS = {
    "08001": ("08", "Barranquilla"), "13001": ("13", "Cartagena"),
    "47001": ("47", "Santa Marta"), "76001": ("76", "Cali"),
    "76109": ("76", "Buenaventura"),
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def query_url(parameters: dict[str, str]) -> str:
    return API + "?" + urllib.parse.urlencode(parameters)


def snapshot_queries() -> dict[str, str]:
    queries = {
        f"ins_dengue_{year}.json": query_url({
            "$where": f"ano={year} AND cod_eve in(210,220)",
            "$order": "cod_eve,semana,cod_dpto_o,cod_mun_o", "$limit": "50000",
        }) for year in YEARS
    }
    queries["ins_metadata.json"] = "https://www.datos.gov.co/api/views/4hyg-wa9d.json"
    queries["ins_independent_weekly_totals.json"] = query_url({
        "$select": "ano,cod_eve,cod_dpto_o,semana,sum(conteo) as cases,count(*) as source_rows",
        "$where": "ano between 2019 and 2022 AND cod_eve in(210,220)",
        "$group": "ano,cod_eve,cod_dpto_o,semana",
        "$order": "ano,cod_eve,cod_dpto_o,semana", "$limit": "50000",
    })
    return queries


def fetch_snapshot(destination: Path) -> None:
    """Save original response bytes, without changing the pinned release inputs."""
    if destination.exists():
        raise ValueError("Candidate snapshot directory must not already exist")
    destination.mkdir(parents=True)
    records = []
    for filename, url in snapshot_queries().items():
        request = urllib.request.Request(url, headers={"User-Agent": "ColombiaDengueAtlas/1.0"})
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
            last_modified = response.headers.get("Last-Modified")
        decoded = json.loads(payload)
        if isinstance(decoded, list) and len(decoded) >= 50000:
            raise ValueError("Query hit its row limit; add pagination before using this snapshot")
        (destination / filename).write_bytes(payload)
        records.append({"filename": filename, "url": url, "bytes": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                        "http_last_modified": last_modified})
    metadata = json.loads((destination / "ins_metadata.json").read_bytes())
    if metadata.get("licenseId") != "CC_40_BY_SA":
        raise ValueError("Source license changed; review redistribution before use")
    write_json(destination / "ins_manifest.json", {
        "source_id": SOURCE_ID, "dataset_id": "4hyg-wa9d", "license": "CC-BY-SA-4.0",
        "snapshot_date": datetime.now(timezone.utc).date().isoformat(), "files": records,
    })


def build(raw_dir: Path, output_dir: Path) -> dict:
    manifest = json.loads((raw_dir / "ins_manifest.json").read_bytes())
    file_records = {record["filename"]: record for record in manifest["files"]}
    if set(file_records) != set(snapshot_queries()):
        raise ValueError("Manifest does not contain the exact expected source files")
    for filename, record in file_records.items():
        payload = (raw_dir / filename).read_bytes()
        if hashlib.sha256(payload).hexdigest() != record["sha256"]:
            raise ValueError(f"Source fingerprint mismatch: {filename}")
    metadata = json.loads((raw_dir / "ins_metadata.json").read_bytes())
    if metadata["licenseId"] != "CC_40_BY_SA":
        raise ValueError("Expected CC BY-SA 4.0 for the source snapshot")

    aggregates: Counter = Counter()
    source_rows: Counter = Counter()
    excluded: Counter = Counter()
    districts: Counter = Counter()
    municipal_keys: set = set()
    expected_fields = {"ano", "semana", "cod_eve", "cod_dpto_o", "cod_mun_o",
                       "nombre_evento", "departamento_ocurrencia", "municipio_ocurrencia", "conteo"}
    raw_rows = 0
    raw_zeros = 0
    for year in YEARS:
        rows = json.loads((raw_dir / f"ins_dengue_{year}.json").read_bytes())
        if len(rows) >= 50000:
            raise ValueError("Snapshot may be truncated at query limit")
        for row in rows:
            if set(row) != expected_fields:
                raise ValueError("Missing/unexpected source fields")
            y, week, event = int(row["ano"]), int(row["semana"]), str(row["cod_eve"])
            dept = str(int(row["cod_dpto_o"])).zfill(2)
            mun = str(int(row["cod_mun_o"])).zfill(5)
            count = int(row["conteo"])
            if str(count) != str(row["conteo"]) or count < 0:
                raise ValueError("Count is not a nonnegative integer")
            if y != year or event not in EVENTS or not 1 <= week <= WEEKS[year]:
                raise ValueError("Unexpected year, event, or epidemiological week")
            municipal_key = (y, week, event, dept, mun)
            if municipal_key in municipal_keys:
                raise ValueError("Duplicate municipality-week-event key; review before aggregation")
            municipal_keys.add(municipal_key)
            if dept not in DEPARTMENTS and dept not in {"00", "01"}:
                raise ValueError(f"Unmatched source department: {dept}")
            if dept in DEPARTMENTS and not mun.startswith(dept):
                raise ValueError(f"Municipal identifier does not match department: {mun}/{dept}")
            key = (y, week, dept, event)
            aggregates[key] += count
            source_rows[key] += 1
            raw_rows += 1
            raw_zeros += count == 0
            if dept in {"00", "01"}:
                excluded[(y, dept, event)] += count
            if mun in DISTRICTS:
                expected_dept, _ = DISTRICTS[mun]
                if dept != expected_dept:
                    raise ValueError("District parent mismatch")
                districts[(y, mun, event)] += count

    # The second query was independently grouped by the public Socrata API.
    independent = json.loads((raw_dir / "ins_independent_weekly_totals.json").read_bytes())
    remote = {}
    for row in independent:
        key = (int(row["ano"]), int(row["semana"]), str(int(row["cod_dpto_o"])).zfill(2), str(row["cod_eve"]))
        if key in remote:
            raise ValueError("Duplicate independent aggregate key")
        remote[key] = (int(row["cases"]), int(row["source_rows"]))
    local = {key: (value, source_rows[key]) for key, value in aggregates.items()}
    if local != remote:
        raise ValueError("Local sums disagree with the independently grouped source API snapshot")

    output = []
    for year in YEARS:
        for week in range(1, WEEKS[year] + 1):
            for dept, name in DEPARTMENTS.items():
                for event, event_name in EVENTS.items():
                    key = (year, week, dept, event)
                    value = aggregates[key] if key in aggregates else None
                    status = "source_absent" if value is None else "explicit_zero" if value == 0 else "observed_positive"
                    output.append({"year": year, "week": week, "department_code": dept,
                                   "department_name": name, "event_code": event, "event_name": event_name,
                                   "cases": value, "observation_status": status,
                                   "source_rows": source_rows[key], "source_id": SOURCE_ID})
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(output)
    frame["cases"] = frame["cases"].astype("Int64")
    frame.to_csv(output_dir / "surveillance_weekly.csv", index=False, encoding="utf-8", lineterminator="\n")
    # JSON null is deliberate; sparse source absence is never serialized as zero.
    write_json(output_dir / "surveillance_weekly.json", output)
    annual = []
    for year in YEARS:
        for event in EVENTS:
            matching = [r for r in output if r["year"] == year and r["event_code"] == event]
            annual.append({"year": year, "event_code": event,
                           "mapped_cases": sum(r["cases"] for r in matching if r["cases"] is not None),
                           "source_department_week_rows": sum(r["cases"] is not None for r in matching),
                           "expected_department_week_cells": len(matching),
                           "excluded_foreign_cases": excluded[(year, "01", event)],
                           "excluded_unknown_geography_cases": excluded[(year, "00", event)]})
    district_audit = [{"year": y, "municipality_code": mun, "district": DISTRICTS[mun][1],
                       "department_code": DISTRICTS[mun][0], "event_code": event, "cases": cases}
                      for (y, mun, event), cases in sorted(districts.items())]
    report = {
        "source_id": SOURCE_ID, "snapshot_date": manifest["snapshot_date"],
        "source_title": metadata["name"], "source_organization": metadata["attribution"],
        "source_url": "https://www.datos.gov.co/d/4hyg-wa9d",
        "source_data_updated_utc": datetime.fromtimestamp(metadata["rowsUpdatedAt"], timezone.utc).isoformat(),
        "license": "CC-BY-SA-4.0", "years": list(YEARS),
        "epidemiological_weeks_by_year": WEEKS, "geographic_units": len(DEPARTMENTS),
        "raw_municipal_week_event_rows": raw_rows, "explicit_zero_source_rows": raw_zeros,
        "duplicate_municipal_keys": 0, "unmatched_department_codes": 0,
        "independently_verified_week_event_geography_sums": len(remote),
        "output_rows": len(output), "observation_status_counts": dict(Counter(r["observation_status"] for r in output)),
        "annual_audit": annual, "district_audit": district_audit,
        "missingness": "Absent source cells remain null. Row presence is not a reporting-completeness measure.",
        "date_basis": "Source epidemiological year and week; underlying onset-versus-notification date basis is not established by this aggregate dataset's metadata.",
        "case_basis": "Event 210 and event 220 are separate published surveillance categories, not combined. Routine portal describes confirmed-as-notified cases; laboratory confirmation is not supplied.",
        "geography_basis": "Municipality/department of occurrence or procedence, not reporting office or proven residence. Five separately reported districts already carry parent department codes and are included once.",
        "limits": ["No person-level de-duplication is possible from these aggregates.",
                   "Source snapshots and annual event reports can disagree after different revisions or case cleaning.",
                   "Bogotá has no selected-event rows; missing is not evidence of zero disease.",
                   "Calendar years are fully elapsed; this does not establish surveillance capture completeness."],
    }
    write_json(output_dir / "surveillance_audit.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument("--fetch-to", type=Path, help="Download candidate inputs into a NEW directory; never overwrite pinned inputs")
    args = parser.parse_args()
    if args.fetch_to:
        fetch_snapshot(args.fetch_to)
        print(f"Candidate snapshot saved to {args.fetch_to.resolve()}; review before adoption.")
    else:
        report = build(args.raw_dir, args.output_dir)
        print(json.dumps({k: report[k] for k in ["raw_municipal_week_event_rows", "output_rows", "independently_verified_week_event_geography_sums", "observation_status_counts"]}))


if __name__ == "__main__":
    main()
