"""
Database Initialization & Seeder for SIH26027
Loads generated CSV datasets into SQLite/PostgreSQL using SQLAlchemy models.
"""

import os
import csv
import sys
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.database import engine, SessionLocal, Base
from backend.models.department import Department
from backend.models.station import Station
from backend.models.section import Section
from backend.models.asset import Asset
from backend.models.task import MaintenanceTask
from backend.models.train import Train, TrainMovement
from backend.models.block import BlockRequest, OptimizedBlock, BlockTaskAssignment
from backend.models.optimization_run import OptimizationRun, Conflict

DATA_DIR = os.path.join(BASE_DIR, "data")


def parse_datetime(dt_str):
    if not dt_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            pass
    return None


def seed_database():
    print("Creating all database tables via SQLAlchemy metadata...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()

    try:
        # 1. Departments
        print("Seeding departments...")
        dept_map = {}
        with open(os.path.join(DATA_DIR, "departments.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dept = Department(
                    code=row["department_code"],
                    name=row["department_name"],
                    system_source=row["system_source"],
                    color_code=row["color_code"],
                    description=row["description"]
                )
                db.add(dept)
                db.flush()
                dept_map[dept.code] = dept.id

        # 2. Stations
        print("Seeding stations...")
        station_map = {}
        with open(os.path.join(DATA_DIR, "stations.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                st = Station(
                    code=row["code"],
                    name=row["name"],
                    zone=row["zone"],
                    division=row["division"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    lines_count=int(row["lines_count"])
                )
                db.add(st)
                db.flush()
                station_map[st.code] = st.id

        # 3. Sections
        print("Seeding sections...")
        section_map = {}
        with open(os.path.join(DATA_DIR, "sections.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sec = Section(
                    section_code=row["section_code"],
                    name=row["name"],
                    station_from_id=station_map[row["station_from_code"]],
                    station_to_id=station_map[row["station_to_code"]],
                    distance_km=float(row["distance_km"]),
                    max_speed_kmh=int(row["max_speed_kmh"]),
                    tracks_count=int(row["tracks_count"]),
                    electrified=bool(int(row["electrified"])),
                    line_capacity_trains_per_day=int(row["line_capacity_trains_per_day"])
                )
                db.add(sec)
                db.flush()
                section_map[sec.section_code] = sec.id
                section_map[int(row["section_id"])] = sec.id

        # 4. Assets
        print("Seeding assets...")
        asset_map = {}
        with open(os.path.join(DATA_DIR, "assets.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ast = Asset(
                    asset_id=row["asset_id"],
                    name=row["name"],
                    asset_type=row["asset_type"],
                    department_id=dept_map[row["department"]],
                    section_id=section_map[row["section_code"]],
                    condition_score=float(row["condition_score"]),
                    last_maintenance_date=parse_datetime(row["last_maintenance_date"]),
                    next_due_date=parse_datetime(row["next_due_date"]),
                    criticality=int(row["criticality"])
                )
                db.add(ast)
                db.flush()
                asset_map[ast.asset_id] = ast.id

        # 5. Maintenance Tasks
        print("Seeding maintenance tasks...")
        task_map = {}
        with open(os.path.join(DATA_DIR, "maintenance_tasks.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sec_id = section_map[int(row["section_id"])]
                ast_id = asset_map[row["asset_id"]]
                dept_id = dept_map[row["department"]]

                task = MaintenanceTask(
                    task_id=row["task_id"],
                    department_id=dept_id,
                    asset_id=ast_id,
                    section_id=sec_id,
                    task_type=row["task_type"],
                    description=row["description"],
                    criticality=int(row["criticality"]),
                    urgency=row["urgency"],
                    overdue_days=int(row["overdue_days"]),
                    duration_minutes=int(row["duration_minutes"]),
                    crew_required=int(row["crew_required"]),
                    equipment_required=row["equipment_required"],
                    preferred_start=parse_datetime(row["preferred_start"]),
                    preferred_end=parse_datetime(row["preferred_end"]),
                    safety_required=row["safety_required"],
                    priority_score=float(row["priority_score"]),
                    priority_reason=row["priority_reason"],
                    priority_class=row["priority_class"],
                    status=row["status"]
                )
                db.add(task)
                db.flush()
                task_map[task.task_id] = task.id

        # 6. Trains
        print("Seeding trains...")
        train_map = {}
        with open(os.path.join(DATA_DIR, "train_schedule.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                orig_id = station_map.get(row["origin"])
                dest_id = station_map.get(row["destination"])
                if not orig_id or not dest_id:
                    continue

                train = Train(
                    train_id=row["train_id"],
                    train_number=row["train_number"],
                    train_name=row["train_name"],
                    train_type=row["train_type"],
                    origin_id=orig_id,
                    destination_id=dest_id,
                    priority=int(row["priority"])
                )
                db.add(train)
                db.flush()
                train_map[train.train_id] = train.id

        # 7. Train Movements (batch insert for high speed)
        print("Seeding train movements...")
        movement_objects = []
        with open(os.path.join(DATA_DIR, "train_movements.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                t_id = train_map.get(row["train_id"])
                s_id = section_map.get(row["section_code"])
                if t_id and s_id:
                    movement_objects.append(TrainMovement(
                        movement_id=row["movement_id"],
                        train_id=t_id,
                        section_id=s_id,
                        scheduled_entry=parse_datetime(row["scheduled_entry"]),
                        scheduled_exit=parse_datetime(row["scheduled_exit"]),
                        speed_restriction_kmh=None
                    ))
        db.bulk_save_objects(movement_objects)
        db.commit()

        # 8. Block Requests
        print("Seeding block requests...")
        request_objects = []
        with open(os.path.join(DATA_DIR, "block_requests.csv"), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dept_id = dept_map.get(row["department"])
                s_id = section_map.get(int(row["section_id"]))
                t_id = task_map.get(row["task_id"])
                if dept_id and s_id:
                    request_objects.append(BlockRequest(
                        request_id=row["request_id"],
                        department_id=dept_id,
                        section_id=s_id,
                        task_id=t_id,
                        requested_start=parse_datetime(row["requested_start"]),
                        requested_end=parse_datetime(row["requested_end"]),
                        duration_minutes=int(row["duration_minutes"]),
                        purpose=row["purpose"],
                        status=row["status"]
                    ))
        db.bulk_save_objects(request_objects)
        db.commit()

        print("Database seeded successfully with all tables!")
        # Print counts
        print(f"Total Departments:     {db.query(Department).count()}")
        print(f"Total Stations:        {db.query(Station).count()}")
        print(f"Total Sections:        {db.query(Section).count()}")
        print(f"Total Assets:          {db.query(Asset).count()}")
        print(f"Total Tasks:           {db.query(MaintenanceTask).count()}")
        print(f"Total Trains:          {db.query(Train).count()}")
        print(f"Total Movements:       {db.query(TrainMovement).count()}")
        print(f"Total Block Requests:  {db.query(BlockRequest).count()}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
