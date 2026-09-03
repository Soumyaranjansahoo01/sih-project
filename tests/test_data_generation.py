import os
import csv
import pytest

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    assert os.path.exists(path), f"CSV file {filename} does not exist in {DATA_DIR}"
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_stations_dataset():
    stations = load_csv("stations.csv")
    assert len(stations) >= 100, f"Expected at least 100 stations, got {len(stations)}"
    # Verify mandatory keys
    for s in stations[:10]:
        assert "code" in s and len(s["code"]) > 0
        assert "latitude" in s and float(s["latitude"]) > 0
        assert "longitude" in s and float(s["longitude"]) > 0
        assert "lines_count" in s and int(s["lines_count"]) >= 2


def test_sections_dataset():
    sections = load_csv("sections.csv")
    assert len(sections) >= 50, f"Expected at least 50 sections, got {len(sections)}"
    for sec in sections[:10]:
        assert "section_code" in sec
        assert "station_from_code" in sec
        assert "station_to_code" in sec
        assert float(sec["distance_km"]) > 0
        assert int(sec["max_speed_kmh"]) >= 80


def test_assets_dataset():
    assets = load_csv("assets.csv")
    assert len(assets) >= 300, f"Expected at least 300 assets, got {len(assets)}"
    depts = {a["department"] for a in assets}
    assert {"ENG", "OHE", "S&T"}.issubset(depts), f"Assets missing key departments: {depts}"
    for a in assets[:10]:
        assert float(a["condition_score"]) >= 0.0 and float(a["condition_score"]) <= 100.0
        assert int(a["criticality"]) in [1, 2, 3, 4, 5]


def test_maintenance_tasks_dataset():
    tasks = load_csv("maintenance_tasks.csv")
    assert len(tasks) >= 500, f"Expected at least 500 maintenance tasks, got {len(tasks)}"
    depts = {t["department"] for t in tasks}
    assert {"ENG", "OHE", "S&T"}.issubset(depts), f"Tasks missing departments: {depts}"

    priorities = [float(t["priority_score"]) for t in tasks]
    assert min(priorities) >= 0.0
    assert max(priorities) <= 100.0

    # Ensure critical tasks exist
    critical_tasks = [t for t in tasks if t["priority_class"] == "Critical"]
    assert len(critical_tasks) > 0, "No critical tasks generated"

    # Ensure realistic duration
    for t in tasks[:20]:
        duration = int(t["duration_minutes"])
        assert 30 <= duration <= 360, f"Abnormal task duration: {duration}"
        assert int(t["crew_required"]) >= 1


def test_trains_and_movements_dataset():
    trains = load_csv("train_schedule.csv")
    assert len(trains) >= 200, f"Expected at least 200 trains, got {len(trains)}"

    movements = load_csv("train_movements.csv")
    assert len(movements) >= 1000, f"Expected at least 1000 train movements, got {len(movements)}"

    # Check premium train presence
    vande_bharats = [t for t in trains if "Vande Bharat" in t["train_type"] or "Vande Bharat" in t["train_name"]]
    assert len(vande_bharats) >= 3, "Realistic premium Vande Bharat trains missing"


def test_corridor_availability():
    corridors = load_csv("corridor_availability.csv")
    assert len(corridors) > 0
    slot_types = {c["slot_type"] for c in corridors}
    assert "NIGHT_WINDOW" in slot_types


def test_block_requests():
    requests = load_csv("block_requests.csv")
    assert len(requests) >= 200
    for r in requests[:10]:
        assert int(r["duration_minutes"]) > 0
        assert r["department"] in ["ENG", "OHE", "S&T"]
