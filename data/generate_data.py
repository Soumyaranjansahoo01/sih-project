"""
Synthetic Dataset Generator for SIH26027
AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways

DISCLAIMER:
This dataset is completely SYNTHETIC and generated strictly for decision-support algorithm testing,
academic prototyping, and demonstration purposes. It does not represent or access internal Indian Railways
production systems (TMS, SMMS, TDMS, or COA).
"""

import os
import csv
import random
from datetime import datetime, timedelta

# Set fixed seed for reproducibility while generating realistic variability
random.seed(26027)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(BASE_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# 1. DEPARTMENTS
# ----------------------------------------------------------------------
DEPARTMENTS = [
    {
        "department_code": "ENG",
        "department_name": "Civil Engineering (P-Way)",
        "system_source": "TMS",
        "color_code": "#2563eb",
        "description": "Permanent Way, Track Structure, Sleepers, Ballast, Bridges, Turnouts"
    },
    {
        "department_code": "OHE",
        "department_name": "Traction Distribution / OHE",
        "system_source": "TDMS",
        "color_code": "#f59e0b",
        "description": "25kV AC Overhead Catenary, Contact Wire, Cantilevers, Neutral Sections, Sub-stations"
    },
    {
        "department_code": "S&T",
        "department_name": "Signal & Telecommunication",
        "system_source": "SMMS",
        "color_code": "#10b981",
        "description": "Electronic Interlocking, Point Machines, Digital Axle Counters, Track Circuits, Signals"
    }
]

# ----------------------------------------------------------------------
# 2. STATIONS (Realistic 105 stations on Northern/North Central trunk corridor)
# ----------------------------------------------------------------------
STATION_DEFINITIONS = [
    ("NDLS", "New Delhi", "NR", "DLI", 28.6427, 77.2195, 16),
    ("CSB", "Shivaji Bridge", "NR", "DLI", 28.6320, 77.2285, 4),
    ("TKJ", "Tilak Bridge", "NR", "DLI", 28.6254, 77.2396, 4),
    ("MWC", "Mandawali Chander Vihar", "NR", "DLI", 28.6268, 77.3012, 2),
    ("ANVR", "Anand Vihar", "NR", "DLI", 28.6502, 77.3150, 4),
    ("ANVT", "Anand Vihar Terminal", "NR", "DLI", 28.6469, 77.3164, 7),
    ("CNJ", "Chander Nagar", "NR", "DLI", 28.6621, 77.3298, 2),
    ("SBB", "Sahibabad Jn", "NR", "DLI", 28.6734, 77.3615, 6),
    ("GZB", "Ghaziabad Jn", "NR", "DLI", 28.6675, 77.4384, 8),
    ("MIU", "Maripat", "NCR", "PRYJ", 28.5832, 77.5123, 3),
    ("DER", "Dadri", "NCR", "PRYJ", 28.5521, 77.5645, 6),
    ("BRKY", "Boraki", "NCR", "PRYJ", 28.5123, 77.6120, 2),
    ("AJR", "Ajaibpur", "NCR", "PRYJ", 28.4721, 77.6643, 3),
    ("DKDE", "Dankaur", "NCR", "PRYJ", 28.4120, 77.7214, 4),
    ("WAIR", "Wair", "NCR", "PRYJ", 28.3612, 77.7789, 2),
    ("CHL", "Chola", "NCR", "PRYJ", 28.3145, 77.8321, 3),
    ("GNRL", "Gangraul", "NCR", "PRYJ", 28.2712, 77.8745, 2),
    ("SKQ", "Sikandrabad", "NCR", "PRYJ", 28.2321, 77.9123, 3),
    ("KRJ", "Khurja Jn", "NCR", "PRYJ", 28.1890, 77.9456, 5),
    ("KAMP", "Kamalpur", "NCR", "PRYJ", 28.1412, 77.9812, 2),
    ("DAR", "Danwar", "NCR", "PRYJ", 28.0934, 78.0234, 2),
    ("SOM", "Somna", "NCR", "PRYJ", 28.0412, 78.0645, 3),
    ("KLA", "Kulwa", "NCR", "PRYJ", 27.9890, 78.1023, 2),
    ("MZGI", "Mehrawal", "NCR", "PRYJ", 27.9345, 78.1345, 2),
    ("ALJN", "Aligarh Jn", "NCR", "PRYJ", 27.8974, 78.0880, 7),
    ("DAQ", "Daud Khan", "NCR", "PRYJ", 27.8345, 78.1412, 2),
    ("MXK", "Mandrak", "NCR", "PRYJ", 27.7812, 78.1823, 3),
    ("SNS", "Sasni", "NCR", "PRYJ", 27.7123, 78.2245, 3),
    ("HRS", "Hathras Jn", "NCR", "PRYJ", 27.6045, 78.2567, 5),
    ("PORA", "Pora", "NCR", "PRYJ", 27.5412, 78.2989, 2),
    ("CMR", "Chamrola", "NCR", "PRYJ", 27.4812, 78.3412, 3),
    ("BRN", "Barhan Jn", "NCR", "PRYJ", 27.4123, 78.3890, 4),
    ("MTI", "Mitawali", "NCR", "PRYJ", 27.3512, 78.4321, 2),
    ("TDL", "Tundla Jn", "NCR", "PRYJ", 27.2062, 78.2435, 8),
    ("HNG", "Hirangaon", "NCR", "PRYJ", 27.1823, 78.3123, 2),
    ("FZD", "Firozabad", "NCR", "PRYJ", 27.1512, 78.3980, 4),
    ("MNR", "Makkhanpur", "NCR", "PRYJ", 27.1123, 78.4812, 3),
    ("SKB", "Shikohabad Jn", "NCR", "PRYJ", 27.1084, 78.5843, 5),
    ("KAA", "Kaurara", "NCR", "PRYJ", 27.0612, 78.6723, 2),
    ("BDN", "Bhadan", "NCR", "PRYJ", 27.0234, 78.7512, 3),
    ("BBL", "Balrai", "NCR", "PRYJ", 26.9745, 78.8345, 2),
    ("JGR", "Jaswantnagar", "NCR", "PRYJ", 26.8823, 78.9123, 3),
    ("SB", "Sarai Bhopat", "NCR", "PRYJ", 26.8123, 78.9845, 2),
    ("ETW", "Etawah Jn", "NCR", "PRYJ", 26.7768, 79.0222, 6),
    ("EKL", "Ekdil", "NCR", "PRYJ", 26.7512, 79.1123, 3),
    ("BNT", "Bharthana", "NCR", "PRYJ", 26.7545, 79.2345, 4),
    ("SHW", "Samhon", "NCR", "PRYJ", 26.7412, 79.3312, 2),
    ("ULD", "Achalda", "NCR", "PRYJ", 26.7123, 79.4123, 3),
    ("GHSR", "Ghasara Halt", "NCR", "PRYJ", 26.6812, 79.4812, 2),
    ("PATA", "Pata", "NCR", "PRYJ", 26.6545, 79.5412, 3),
    ("PHD", "Phaphund", "NCR", "PRYJ", 26.6123, 79.6123, 4),
    ("KNS", "Kanchausi", "NCR", "PRYJ", 26.5812, 79.7123, 3),
    ("PJY", "Parjani", "NCR", "PRYJ", 26.5412, 79.7912, 2),
    ("JJK", "Jhinjhak", "NCR", "PRYJ", 26.5312, 79.8412, 3),
    ("AAP", "Ambiapur", "NCR", "PRYJ", 26.5123, 79.9123, 2),
    ("RURA", "Rura", "NCR", "PRYJ", 26.4912, 79.9912, 4),
    ("ROSN", "Roshan Mau", "NCR", "PRYJ", 26.4712, 80.0612, 2),
    ("MTH", "Maitha", "NCR", "PRYJ", 26.4512, 80.1212, 3),
    ("BPU", "Bhaupur", "NCR", "PRYJ", 26.4312, 80.1912, 3),
    ("PNKD", "Panki Dham", "NCR", "PRYJ", 26.4423, 80.2512, 4),
    ("GOY", "Govindpuri Jn", "NCR", "PRYJ", 26.4489, 80.3123, 6),
    ("CNB", "Kanpur Central", "NCR", "PRYJ", 26.4542, 80.3507, 10),
    ("CPB", "Kanpur Bridge Left Bank", "NR", "LKO", 26.4721, 80.3721, 3),
    ("MGW", "Magarwara", "NR", "LKO", 26.4912, 80.4312, 2),
    ("ON", "Unnao Jn", "NR", "LKO", 26.5412, 80.4912, 5),
    ("MKG", "Manak Nagar", "NR", "LKO", 26.8123, 80.8912, 4),
    ("LKO", "Lucknow Charbagh", "NR", "LKO", 26.8322, 80.9228, 9),
    ("CHK", "Chakeri", "NCR", "PRYJ", 26.4123, 80.4212, 3),
    ("RXM", "Rooma", "NCR", "PRYJ", 26.3812, 80.4812, 2),
    ("SSL", "Sirsaul", "NCR", "PRYJ", 26.3312, 80.5412, 3),
    ("PMPR", "Prempur", "NCR", "PRYJ", 26.2812, 80.6123, 2),
    ("KBN", "Karbigwan", "NCR", "PRYJ", 26.2312, 80.6812, 3),
    ("AUNG", "Aung", "NCR", "PRYJ", 26.1812, 80.7512, 2),
    ("BKO", "Bindki Road", "NCR", "PRYJ", 26.1312, 80.8123, 4),
    ("KSQ", "Kanspur Gugauli", "NCR", "PRYJ", 26.0812, 80.8712, 2),
    ("MWH", "Malwan", "NCR", "PRYJ", 26.0312, 80.9312, 3),
    ("KKS", "Kurasti Kalan", "NCR", "PRYJ", 25.9812, 80.9912, 2),
    ("FTP", "Fatehpur", "NCR", "PRYJ", 25.9284, 80.8123, 5),
    ("RAMA", "Ramva", "NCR", "PRYJ", 25.8812, 80.8812, 2),
    ("FYZ", "Faizullahpur", "NCR", "PRYJ", 25.8312, 80.9412, 2),
    ("RUB", "Rasulabad", "NCR", "PRYJ", 25.7812, 81.0123, 3),
    ("SNIE", "Sath Naraini", "NCR", "PRYJ", 25.7312, 81.0712, 2),
    ("KGA", "Khaga", "NCR", "PRYJ", 25.6812, 81.1412, 4),
    ("KUW", "Kanwar", "NCR", "PRYJ", 25.6312, 81.2112, 2),
    ("SRO", "Sirathu", "NCR", "PRYJ", 25.5812, 81.2812, 3),
    ("ASCE", "Athsarai", "NCR", "PRYJ", 25.5312, 81.3512, 2),
    ("BRE", "Bharwari", "NCR", "PRYJ", 25.4812, 81.4212, 3),
    ("MNJ", "Manoharganj", "NCR", "PRYJ", 25.4512, 81.4912, 2),
    ("SYWN", "Saiyid Sarawan", "NCR", "PRYJ", 25.4312, 81.5612, 3),
    ("BMU", "Bamhrauli", "NCR", "PRYJ", 25.4412, 81.7123, 4),
    ("SFG", "Subedarganj", "NCR", "PRYJ", 25.4467, 81.7912, 5),
    ("PRYJ", "Prayagraj Jn", "NCR", "PRYJ", 25.4484, 81.8340, 10),
    ("NYN", "Naini Jn", "NCR", "PRYJ", 25.3812, 81.8712, 5),
    ("KCN", "Karchana", "NCR", "PRYJ", 25.3212, 81.9312, 3),
    ("BEP", "Bheerpur", "NCR", "PRYJ", 25.2712, 81.9912, 2),
    ("MJA", "Meja Road", "NCR", "PRYJ", 25.2112, 82.0812, 4),
    ("MNF", "Manda Road", "NCR", "PRYJ", 25.1712, 82.1612, 3),
    ("JIA", "Jigna", "NCR", "PRYJ", 25.1412, 82.2412, 2),
    ("GAE", "Gaipura", "NCR", "PRYJ", 25.1312, 82.3212, 3),
    ("BDL", "Vindhyachal", "NCR", "PRYJ", 25.1512, 82.4912, 4),
    ("MZP", "Mirzapur", "NCR", "PRYJ", 25.1460, 82.5690, 5),
    ("JEP", "Jeonathpur", "NCR", "DDU", 25.2612, 83.0512, 3),
    ("DDU", "Pt. Deen Dayal Upadhyaya Jn", "ECR", "DDU", 25.2818, 83.1167, 12),
    ("BSB", "Varanasi Jn", "NR", "LKO", 25.3298, 82.9868, 9),
    ("MGS", "Mughal Sarai Yard", "ECR", "DDU", 25.2890, 83.1250, 8),
]

def generate_stations():
    stations = []
    for idx, s in enumerate(STATION_DEFINITIONS, start=1):
        stations.append({
            "station_id": idx,
            "code": s[0],
            "name": s[1],
            "zone": s[2],
            "division": s[3],
            "latitude": s[4],
            "longitude": s[5],
            "lines_count": s[6]
        })
    return stations

# ----------------------------------------------------------------------
# 3. SECTIONS (55 realistic corridor sections connecting contiguous stations)
# ----------------------------------------------------------------------
def generate_sections(stations):
    sections = []
    # Create main trunk sequence
    main_trunk_codes = [
        "NDLS", "TKJ", "ANVT", "SBB", "GZB", "DER", "DKDE", "KRJ", "SOM", "ALJN",
        "HRS", "BRN", "TDL", "FZD", "SKB", "BDN", "JGR", "ETW", "BNT", "ULD",
        "PATA", "PHD", "JJK", "RURA", "BPU", "PNKD", "CNB", "CHK", "SSL", "KBN",
        "BKO", "MWH", "FTP", "RUB", "KGA", "SRO", "BRE", "SYWN", "SFG", "PRYJ",
        "NYN", "KCN", "MJA", "MNF", "GAE", "BDL", "MZP", "JEP", "DDU"
    ]
    code_to_station = {s["code"]: s for s in stations}

    sec_id = 1
    for i in range(len(main_trunk_codes) - 1):
        st_from = code_to_station.get(main_trunk_codes[i])
        st_to = code_to_station.get(main_trunk_codes[i+1])
        if not st_from or not st_to:
            continue
        dist = round(random.uniform(12.0, 32.0), 1)
        speed = 130 if dist > 18 else 110
        sections.append({
            "section_id": sec_id,
            "section_code": f"SEC_{sec_id:03d}",
            "name": f"{st_from['code']}-{st_to['code']} Main Corridor",
            "station_from_code": st_from["code"],
            "station_to_code": st_to["code"],
            "station_from_id": st_from["station_id"],
            "station_to_id": st_to["station_id"],
            "distance_km": dist,
            "max_speed_kmh": speed,
            "tracks_count": 2 if dist > 20 else 3,
            "electrified": 1,
            "line_capacity_trains_per_day": random.randint(110, 160)
        })
        sec_id += 1

    # Feeder / loop branch sections (CNB to LKO, DDU to BSB, etc.)
    extra_branches = [
        ("CNB", "CPB"), ("CPB", "ON"), ("ON", "MKG"), ("MKG", "LKO"),
        ("DDU", "BSB"), ("DDU", "MGS"), ("GZB", "ANVR")
    ]
    for b_from, b_to in extra_branches:
        st_from = code_to_station.get(b_from)
        st_to = code_to_station.get(b_to)
        if st_from and st_to:
            sections.append({
                "section_id": sec_id,
                "section_code": f"SEC_{sec_id:03d}",
                "name": f"{b_from}-{b_to} Feeder Section",
                "station_from_code": st_from["code"],
                "station_to_code": st_to["code"],
                "station_from_id": st_from["station_id"],
                "station_to_id": st_to["station_id"],
                "distance_km": round(random.uniform(14.0, 28.0), 1),
                "max_speed_kmh": 110,
                "tracks_count": 2,
                "electrified": 1,
                "line_capacity_trains_per_day": 100
            })
            sec_id += 1

    return sections

# ----------------------------------------------------------------------
# 4. ASSETS (350+ realistic infrastructure assets)
# ----------------------------------------------------------------------
ASSET_TYPES_BY_DEPT = {
    "ENG": [
        "Track Segment", "Turnout / Point Crossing", "Sleeper Bed & Fastenings",
        "Ballast Cushion", "Railway Bridge Girder", "Expansion Joint (SEJ)"
    ],
    "OHE": [
        "25kV Catenary Wire", "Contact Wire Segment", "Cantilever Assembly",
        "Neutral Section Insulator", "Traction Substation Feeder", "OHE Mast Grounding"
    ],
    "S&T": [
        "Digital Axle Counter (DAC)", "Electric Point Machine",
        "Electronic Interlocking (EI) Unit", "High-Voltage Track Circuit",
        "LED Signal Aspect Unit", "Integrated Power Supply (IPS)"
    ]
}

def generate_assets(sections):
    assets = []
    asset_id_counter = 1
    base_date = datetime(2026, 8, 15, 0, 0)

    for sec in sections:
        # Create 6 to 9 assets per section distributed among ENG, OHE, S&T
        for dept in ["ENG", "OHE", "S&T"]:
            types = ASSET_TYPES_BY_DEPT[dept]
            for _ in range(random.randint(2, 3)):
                a_type = random.choice(types)
                cond_score = round(random.uniform(25.0, 98.0), 1)
                crit = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 40, 25, 15])[0]
                days_since_maint = random.randint(30, 240)
                last_maint = base_date - timedelta(days=days_since_maint)
                days_to_due = random.randint(-25, 45)  # negative means overdue!
                next_due = base_date + timedelta(days=days_to_due)

                assets.append({
                    "id": asset_id_counter,
                    "asset_id": f"AST_{dept}_{asset_id_counter:04d}",
                    "name": f"{sec['section_code']} {a_type}",
                    "asset_type": a_type,
                    "department": dept,
                    "section_id": sec["section_id"],
                    "section_code": sec["section_code"],
                    "condition_score": cond_score,
                    "last_maintenance_date": last_maint.strftime("%Y-%m-%d"),
                    "next_due_date": next_due.strftime("%Y-%m-%d"),
                    "criticality": crit
                })
                asset_id_counter += 1
    return assets

# ----------------------------------------------------------------------
# 5. MAINTENANCE TASKS (550+ tasks across 7 days)
# ----------------------------------------------------------------------
TASK_TEMPLATES = {
    "ENG": [
        ("Tamping & Track Alignment", 120, "BCM / Track Tamper", 8, "Traffic Block"),
        ("Ballast Cleaning & Screening", 180, "BCM & Hopper Rake", 12, "Traffic Block"),
        ("Rail Joint Ultrasonic Testing (USFD)", 90, "USFD Trolley", 4, "Caution Order"),
        ("Switch Expansion Joint (SEJ) Replacement", 150, "Mobile Crane", 10, "Traffic Block"),
        ("Sleeper Renewal & Ballast Packing", 120, "Duo-matic Tamper", 8, "Traffic Block"),
        ("Point & Crossing Diamond Overhaul", 180, "Heavy P-Way Kit", 10, "Traffic Block")
    ],
    "OHE": [
        ("Catenary & Contact Wire Height Stagger Check", 90, "OHE Tower Wagon", 6, "Power Block"),
        ("Cantilever & Insulator Washing", 60, "Tower Wagon with Jet", 5, "Power Block"),
        ("Neutral Section Assembly Inspection", 120, "Tower Wagon", 6, "Power Block"),
        ("Dropper Adjustment & Splice Replacement", 90, "Tower Wagon", 5, "Power Block"),
        ("Substation Feeder Breaker Maintenance", 120, "Electrical Tool Kit", 4, "Power Block"),
        ("Section Insulator Replacement", 150, "OHE Gang Equipment", 7, "Power Block")
    ],
    "S&T": [
        ("Electric Point Machine Overhauling & Obstruction Test", 90, "S&T Tool Kit", 4, "Caution Order"),
        ("Digital Axle Counter (DAC) Tuning & Calibration", 60, "Oscilloscope & Multimeter", 3, "None"),
        ("Electronic Interlocking (EI) Diagnostic & Redundancy Test", 120, "EI Programmer Terminal", 4, "Traffic Block"),
        ("Audio Frequency Track Circuit (AFTC) Inspection", 60, "Testing Shunt Box", 3, "None"),
        ("Color Light Signal LED Aspect & Wiring Check", 60, "Signal Alignment Kit", 3, "Caution Order"),
        ("Block Proving by Axle Counter (BPAC) Validation", 90, "S&T Relay Testing Unit", 4, "Caution Order")
    ]
}

def generate_maintenance_tasks(assets, sections):
    tasks = []
    task_id_counter = 1
    start_date = datetime(2026, 9, 7, 0, 0)  # Planning horizon start: Monday Sept 7, 2026

    # Cluster compatible tasks on the same section and approximate day
    # to guarantee real multi-department combination opportunities!
    grouped_assets = {}
    for a in assets:
        sec_id = a["section_id"]
        grouped_assets.setdefault(sec_id, []).append(a)

    sec_map = {s["section_id"]: s for s in sections}

    for sec_id, sec_assets in grouped_assets.items():
        sec = sec_map[sec_id]
        dept_assets = {"ENG": [], "OHE": [], "S&T": []}
        for a in sec_assets:
            dept_assets[a["department"]].append(a)

        # Generate 9-14 tasks per section across the week
        num_tasks_for_sec = random.randint(10, 14)
        for _ in range(num_tasks_for_sec):
            # Select department with realistic distribution
            dept = random.choice(["ENG", "OHE", "S&T"])
            chosen_asset = random.choice(dept_assets[dept]) if dept_assets[dept] else random.choice(sec_assets)

            task_name, base_duration, equipment, crew, safety = random.choice(TASK_TEMPLATES[dept])
            duration = base_duration + random.choice([-30, 0, 30])
            duration = max(60, min(240, duration))

            # Task criticality correlated with asset condition and criticality
            if chosen_asset["condition_score"] < 40 or chosen_asset["criticality"] >= 4:
                urgency = random.choices(["Immediate", "High", "Normal"], weights=[30, 50, 20])[0]
                crit = random.choices([4, 5], weights=[40, 60])[0]
                overdue = random.randint(5, 30)
            else:
                urgency = random.choices(["High", "Normal", "Low"], weights=[20, 60, 20])[0]
                crit = random.choices([1, 2, 3], weights=[20, 50, 30])[0]
                overdue = random.randint(0, 10)

            # Preferred day within 7-day horizon (Day 0 to Day 6)
            day_offset = random.randint(0, 6)
            preferred_hour = random.choice([1, 2, 3, 4, 10, 11, 12, 13, 14, 23])
            pref_start = start_date + timedelta(days=day_offset, hours=preferred_hour)
            pref_end = pref_start + timedelta(minutes=duration + 60)

            # Transparent priority score calculation for Phase 1
            w_crit = crit * 14.0
            w_urg = {"Immediate": 25.0, "High": 18.0, "Normal": 10.0, "Low": 4.0}[urgency]
            w_overdue = min(20.0, overdue * 0.8)
            w_cond = (100.0 - chosen_asset["condition_score"]) * 0.20
            w_safety = 10.0 if "Block" in safety else 4.0
            p_score = round(min(100.0, max(5.0, w_crit + w_urg + w_overdue + w_cond + w_safety)), 1)

            if p_score >= 81:
                p_class = "Critical"
            elif p_score >= 61:
                p_class = "High"
            elif p_score >= 31:
                p_class = "Medium"
            else:
                p_class = "Low"

            reason_items = []
            if crit >= 4:
                reason_items.append(f"Criticality Level {crit}/5")
            if urgency in ["Immediate", "High"]:
                reason_items.append(f"{urgency} urgency")
            if overdue > 0:
                reason_items.append(f"{overdue} days overdue")
            if chosen_asset["condition_score"] < 50:
                reason_items.append(f"Degraded asset condition ({chosen_asset['condition_score']}%)")
            if "Block" in safety:
                reason_items.append(f"Requires {safety}")

            priority_reason = "; ".join(reason_items) if reason_items else "Routine preventive maintenance"

            tasks.append({
                "task_id": f"MT_{task_id_counter:04d}",
                "department": dept,
                "asset_id": chosen_asset["asset_id"],
                "asset_type": chosen_asset["asset_type"],
                "section_id": sec["section_id"],
                "station_from": sec["station_from_code"],
                "station_to": sec["station_to_code"],
                "task_type": task_name,
                "description": f"{dept} {task_name} on {chosen_asset['asset_id']} ({sec['name']})",
                "criticality": crit,
                "urgency": urgency,
                "overdue_days": overdue,
                "duration_minutes": duration,
                "crew_required": crew,
                "equipment_required": equipment,
                "preferred_start": pref_start.strftime("%Y-%m-%d %H:%M:%S"),
                "preferred_end": pref_end.strftime("%Y-%m-%d %H:%M:%S"),
                "safety_required": safety,
                "priority_score": p_score,
                "priority_reason": priority_reason,
                "priority_class": p_class,
                "status": "Pending"
            })
            task_id_counter += 1

            if len(tasks) >= 600:
                break
        if len(tasks) >= 600:
            break

    return tasks

# ----------------------------------------------------------------------
# 6. TRAINS & SCHEDULE (215 realistic Indian Railways trains)
# ----------------------------------------------------------------------
REALISTIC_TRAIN_CONFIGS = [
    # Premium Vande Bharat Trains (Priority 5)
    ("22436", "Vande Bharat Express (NDLS-BSB)", "Vande Bharat", "NDLS", "BSB", 5),
    ("22435", "Vande Bharat Express (BSB-NDLS)", "Vande Bharat", "BSB", "NDLS", 5),
    ("20888", "Vande Bharat Express (PRYJ-NDLS)", "Vande Bharat", "PRYJ", "NDLS", 5),
    ("22416", "Vande Bharat Express (NDLS-DDU)", "Vande Bharat", "NDLS", "DDU", 5),
    ("20172", "Vande Bharat Express (NDLS-CNB)", "Vande Bharat", "NDLS", "CNB", 5),

    # Rajdhani & Tejas Express (Priority 5)
    ("12301", "Howrah Rajdhani Express (via CNB)", "Rajdhani", "NDLS", "DDU", 5),
    ("12302", "New Delhi Rajdhani Express", "Rajdhani", "DDU", "NDLS", 5),
    ("12423", "Dibrugarh Rajdhani Express", "Rajdhani", "NDLS", "DDU", 5),
    ("12424", "New Delhi Dibrugarh Rajdhani", "Rajdhani", "DDU", "NDLS", 5),
    ("20501", "Tejas Rajdhani Express", "Rajdhani", "NDLS", "DDU", 5),
    ("12305", "Kolkata Rajdhani Express", "Rajdhani", "NDLS", "DDU", 5),
    ("12313", "Sealdah Rajdhani Express", "Rajdhani", "NDLS", "DDU", 5),

    # Superfast Mail/Express (Priority 4)
    ("12417", "Prayagraj Express", "Superfast Express", "PRYJ", "NDLS", 4),
    ("12418", "Prayagraj Express Return", "Superfast Express", "NDLS", "PRYJ", 4),
    ("12397", "Mahabodhi Express", "Superfast Express", "DDU", "NDLS", 4),
    ("12398", "Mahabodhi Express Return", "Superfast Express", "NDLS", "DDU", 4),
    ("12559", "Shiv Ganga Express", "Superfast Express", "BSB", "NDLS", 4),
    ("12560", "Shiv Ganga Express Return", "Superfast Express", "NDLS", "BSB", 4),
    ("12451", "Shram Shakti Express", "Superfast Express", "CNB", "NDLS", 4),
    ("12452", "Shram Shakti Express Return", "Superfast Express", "NDLS", "CNB", 4),
    ("12801", "Purushottam Express", "Superfast Express", "DDU", "NDLS", 4),
    ("12802", "Purushottam Express Return", "Superfast Express", "NDLS", "DDU", 4),
    ("12381", "Poorva Express", "Superfast Express", "NDLS", "DDU", 4),
    ("12382", "Poorva Express Return", "Superfast Express", "DDU", "NDLS", 4),
    ("12487", "Seemanchal Express", "Superfast Express", "ANVT", "DDU", 4),
    ("12581", "Banaras Superfast Express", "Superfast Express", "BSB", "NDLS", 4),
    ("12427", "Rewa Express", "Superfast Express", "PRYJ", "ANVT", 4),
    ("12553", "Vaishali Express", "Superfast Express", "NDLS", "CNB", 4),
    ("12420", "Gomti Express", "Superfast Express", "NDLS", "LKO", 4),
    ("12004", "Lucknow Swarna Shatabdi", "Shatabdi", "NDLS", "LKO", 5),
    ("12003", "New Delhi Swarna Shatabdi", "Shatabdi", "LKO", "NDLS", 5),

    # Express / Passenger / MEMU (Priority 3)
    ("14217", "Unchahar Express", "Mail/Express", "PRYJ", "CNB", 3),
    ("14218", "Unchahar Express Return", "Mail/Express", "CNB", "PRYJ", 3),
    ("14163", "Sangam Express", "Mail/Express", "PRYJ", "ALJN", 3),
    ("64583", "Tundla - Delhi MEMU", "Suburban MEMU", "TDL", "NDLS", 2),
    ("64584", "Delhi - Tundla MEMU", "Suburban MEMU", "NDLS", "TDL", 2),
    ("64591", "Kanpur - Fatehpur MEMU", "Suburban MEMU", "CNB", "FTP", 2),
    ("64592", "Fatehpur - Kanpur MEMU", "Suburban MEMU", "FTP", "CNB", 2),
    ("64153", "Kanpur - Etawah MEMU", "Suburban MEMU", "CNB", "ETW", 2),
    ("64154", "Etawah - Kanpur MEMU", "Suburban MEMU", "ETW", "CNB", 2),
    ("64593", "Kanpur - Prayagraj MEMU", "Suburban MEMU", "CNB", "PRYJ", 2),
    ("64594", "Prayagraj - Kanpur MEMU", "Suburban MEMU", "PRYJ", "CNB", 2),

    # Freight Trains / Rakes (Priority 1-2)
    ("BOXN_101", "Dadri Thermal Coal Rake 1", "Goods/Freight", "DDU", "DER", 1),
    ("BOXN_102", "Dadri Thermal Coal Rake 2", "Goods/Freight", "DDU", "DER", 1),
    ("BCN_201", "Food Corporation Grain Special", "Goods/Freight", "GZB", "DDU", 2),
    ("CONCOR_301", "Dadri Container Depot Express", "Goods/Freight", "DER", "DDU", 2),
    ("CONCOR_302", "DDU Inland Container Feeder", "Goods/Freight", "DDU", "DER", 2),
    ("BTPN_401", "Petroleum Tanker Special", "Goods/Freight", "CNB", "GZB", 2),
    ("RO_RO_501", "Automobile Carrier Special", "Goods/Freight", "NDLS", "DDU", 1)
]

def generate_trains(stations):
    code_to_station = {s["code"]: s for s in stations}
    trains = []
    trn_id = 1

    # First add predefined iconic trains
    for number, name, t_type, orig, dest, prio in REALISTIC_TRAIN_CONFIGS:
        orig_s = code_to_station.get(orig, stations[0])
        dest_s = code_to_station.get(dest, stations[-1])
        trains.append({
            "train_id": f"TRN_{number}",
            "train_number": number,
            "train_name": name,
            "train_type": t_type,
            "origin": orig_s["code"],
            "destination": dest_s["code"],
            "origin_id": orig_s["station_id"],
            "destination_id": dest_s["station_id"],
            "priority": prio
        })
        trn_id += 1

    # Generate additional trains to exceed 200+
    train_types_pool = [
        ("Superfast Express", 4, 0.40),
        ("Mail/Express", 3, 0.30),
        ("Goods/Freight", 1, 0.20),
        ("Suburban MEMU", 2, 0.10)
    ]

    major_nodes = ["NDLS", "ANVT", "GZB", "ALJN", "TDL", "ETW", "CNB", "FTP", "PRYJ", "MZP", "DDU", "LKO"]
    while len(trains) < 220:
        t_type, prio, _ = random.choices(train_types_pool, weights=[40, 30, 20, 10])[0]
        orig_code = random.choice(major_nodes)
        dest_candidates = [m for m in major_nodes if m != orig_code]
        dest_code = random.choice(dest_candidates)
        orig_s = code_to_station[orig_code]
        dest_s = code_to_station[dest_code]

        if "Goods" in t_type:
            number = f"FRT_{random.randint(1000, 9999)}"
            name = f"Freight Corridor Rake ({orig_code}-{dest_code})"
        elif "MEMU" in t_type:
            number = f"64{random.randint(100, 999)}"
            name = f"{orig_code} - {dest_code} Passenger MEMU"
        else:
            number = f"{random.choice([12, 14, 22])}{random.randint(100, 999)}"
            name = f"{orig_code}-{dest_code} {t_type}"

        # Avoid duplicate numbers
        if any(t["train_number"] == number for t in trains):
            continue

        trains.append({
            "train_id": f"TRN_{number}",
            "train_number": number,
            "train_name": name,
            "train_type": t_type,
            "origin": orig_code,
            "destination": dest_code,
            "origin_id": orig_s["station_id"],
            "destination_id": dest_s["station_id"],
            "priority": prio
        })

    return trains

# ----------------------------------------------------------------------
# 7. TRAIN MOVEMENTS (1,500+ movements across 7 days)
# ----------------------------------------------------------------------
def generate_train_movements(trains, sections):
    movements = []
    movement_id_counter = 1
    start_date = datetime(2026, 9, 7, 0, 0)
    sec_lookup = {s["section_id"]: s for s in sections}

    for day in range(7):
        current_day_date = start_date + timedelta(days=day)

        for train in trains:
            # Stagger departures across the day
            base_dep_hour = (hash(train["train_number"]) % 24)
            base_dep_minute = (hash(train["train_id"]) % 60)
            dep_time = current_day_date + timedelta(hours=base_dep_hour, minutes=base_dep_minute)

            # Assign each train to 3-6 contiguous sections
            num_secs = random.randint(3, 7)
            start_sec_idx = (hash(train["train_id"] + str(day)) % (len(sections) - num_secs))
            route_sections = sections[start_sec_idx: start_sec_idx + num_secs]

            t_cursor = dep_time
            for s in route_sections:
                # Travel time depends on section length and train priority
                speed_kmh = 110 if train["priority"] >= 4 else 80
                travel_minutes = max(10, int((s["distance_km"] / speed_kmh) * 60))

                entry_time = t_cursor
                exit_time = entry_time + timedelta(minutes=travel_minutes)
                t_cursor = exit_time + timedelta(minutes=random.randint(2, 6))

                movements.append({
                    "movement_id": f"TM_{movement_id_counter:06d}",
                    "train_id": train["train_id"],
                    "train_number": train["train_number"],
                    "train_name": train["train_name"],
                    "train_type": train["train_type"],
                    "section_id": s["section_id"],
                    "section_code": s["section_code"],
                    "scheduled_entry": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "scheduled_exit": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "priority": train["priority"]
                })
                movement_id_counter += 1

    return movements

# ----------------------------------------------------------------------
# 8. CORRIDOR AVAILABILITY (Day/Night slots for each section over 7 days)
# ----------------------------------------------------------------------
def generate_corridor_availability(sections):
    corridor_rows = []
    start_date = datetime(2026, 9, 7, 0, 0)

    for day in range(7):
        day_date = start_date + timedelta(days=day)
        for s in sections:
            # IR standard maintenance window slots:
            # Slot 1: Midnight / Early Morning (01:00 to 05:00) - high maintenance availability
            # Slot 2: Mid-day Shadow Window (11:00 to 14:00) - moderate availability
            # Slot 3: Evening Trunk Slot (22:00 to 24:00)
            slots = [
                ("NIGHT_WINDOW", day_date + timedelta(hours=1), day_date + timedelta(hours=5), "Optimal"),
                ("MIDDAY_WINDOW", day_date + timedelta(hours=11), day_date + timedelta(hours=14), "Selective"),
                ("LATE_NIGHT_WINDOW", day_date + timedelta(hours=22), day_date + timedelta(hours=24), "Good")
            ]

            for slot_name, s_start, s_end, rating in slots:
                corridor_rows.append({
                    "section_id": s["section_id"],
                    "section_code": s["section_code"],
                    "slot_type": slot_name,
                    "window_start": s_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "window_end": s_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_minutes": int((s_end - s_start).total_seconds() / 60),
                    "operational_rating": rating
                })
    return corridor_rows

# ----------------------------------------------------------------------
# 9. BLOCK REQUESTS (Baseline Independent Department Requests)
# ----------------------------------------------------------------------
def generate_block_requests(tasks):
    requests = []
    req_counter = 1
    for t in tasks:
        # 75% of tasks have explicit independent block requests from their department
        if random.random() < 0.75:
            p_start = datetime.strptime(t["preferred_start"], "%Y-%m-%d %H:%M:%S")
            duration = t["duration_minutes"]
            p_end = p_start + timedelta(minutes=duration)

            requests.append({
                "request_id": f"BR_{req_counter:04d}",
                "department": t["department"],
                "section_id": t["section_id"],
                "task_id": t["task_id"],
                "requested_start": p_start.strftime("%Y-%m-%d %H:%M:%S"),
                "requested_end": p_end.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": duration,
                "purpose": f"Independent {t['department']} request: {t['task_type']}",
                "status": "Requested"
            })
            req_counter += 1
    return requests

# ----------------------------------------------------------------------
# WRITE CSV FILES
# ----------------------------------------------------------------------
def write_csv(filename, fieldnames, data):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filename}: {len(data)} records")
    return filepath

def main():
    print("================================================================")
    print("SIH26027 Synthetic Dataset Generator")
    print("Indian Railways Automatic Block Planning Decision-Support System")
    print("================================================================")

    # 1. Departments
    dept_file = write_csv(
        "departments.csv",
        ["department_code", "department_name", "system_source", "color_code", "description"],
        DEPARTMENTS
    )

    # 2. Stations (100+)
    stations = generate_stations()
    station_file = write_csv(
        "stations.csv",
        ["station_id", "code", "name", "zone", "division", "latitude", "longitude", "lines_count"],
        stations
    )

    # 3. Sections (50+)
    sections = generate_sections(stations)
    section_file = write_csv(
        "sections.csv",
        ["section_id", "section_code", "name", "station_from_code", "station_to_code",
         "station_from_id", "station_to_id", "distance_km", "max_speed_kmh",
         "tracks_count", "electrified", "line_capacity_trains_per_day"],
        sections
    )

    # 4. Assets (300+)
    assets = generate_assets(sections)
    asset_file = write_csv(
        "assets.csv",
        ["id", "asset_id", "name", "asset_type", "department", "section_id", "section_code",
         "condition_score", "last_maintenance_date", "next_due_date", "criticality"],
        assets
    )

    # 5. Maintenance Tasks (500+)
    tasks = generate_maintenance_tasks(assets, sections)
    task_file = write_csv(
        "maintenance_tasks.csv",
        ["task_id", "department", "asset_id", "asset_type", "section_id", "station_from",
         "station_to", "task_type", "description", "criticality", "urgency", "overdue_days",
         "duration_minutes", "crew_required", "equipment_required", "preferred_start",
         "preferred_end", "safety_required", "priority_score", "priority_reason",
         "priority_class", "status"],
        tasks
    )

    # 6. Trains (200+)
    trains = generate_trains(stations)
    train_file = write_csv(
        "train_schedule.csv",
        ["train_id", "train_number", "train_name", "train_type", "origin", "destination",
         "origin_id", "destination_id", "priority"],
        trains
    )

    # 7. Train Movements (1,000+)
    movements = generate_train_movements(trains, sections)
    movement_file = write_csv(
        "train_movements.csv",
        ["movement_id", "train_id", "train_number", "train_name", "train_type",
         "section_id", "section_code", "scheduled_entry", "scheduled_exit", "priority"],
        movements
    )

    # 8. Corridor Availability
    corridors = generate_corridor_availability(sections)
    corridor_file = write_csv(
        "corridor_availability.csv",
        ["section_id", "section_code", "slot_type", "window_start", "window_end",
         "duration_minutes", "operational_rating"],
        corridors
    )

    # 9. Block Requests
    requests = generate_block_requests(tasks)
    request_file = write_csv(
        "block_requests.csv",
        ["request_id", "department", "section_id", "task_id", "requested_start",
         "requested_end", "duration_minutes", "purpose", "status"],
        requests
    )

    print("\nDataset generation completed successfully!")
    print(f"Summary Statistics:")
    print(f"  Stations:            {len(stations)} (Target: >=100)")
    print(f"  Sections:            {len(sections)} (Target: >=50)")
    print(f"  Assets:              {len(assets)} (Target: >=300)")
    print(f"  Maintenance Tasks:   {len(tasks)} (Target: >=500)")
    print(f"  Trains:              {len(trains)} (Target: >=200)")
    print(f"  Train Movements:     {len(movements)} (Target: >=1000)")
    print(f"  Corridor Slots:      {len(corridors)}")
    print(f"  Block Requests:      {len(requests)}")

if __name__ == "__main__":
    main()
