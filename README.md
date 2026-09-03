# SIH26027: AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways

[![Organization: Ministry of Railways](https://img.shields.io/badge/Organization-Ministry%20of%20Railways-004080.svg)](https://indianrailways.gov.in/)
[![Theme: Transportation & Logistics](https://img.shields.io/badge/Theme-Transportation%20%26%20Logistics-2E7D32.svg)]()
[![SIH 2026 Prototype](https://img.shields.io/badge/SIH-2026-orange.svg)]()
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Academic%20Use-lightgrey.svg)]()

> **Decision-Support Prototype for Railway Planners & Section Controllers**  
> *Note: This system is a decision-support advisory prototype. It does NOT autonomously issue real railway signalling commands or control train operations.*

---

## 1. Problem Statement & Background

In Indian Railways (IR), infrastructure maintenance is planned and executed independently across three critical engineering departments:
1. **Civil Engineering (P-Way / ENG)**: Track geometry, rails, sleepers, ballast, turnouts (managed via **TMS** - Track Management System).
2. **Traction Distribution (TRD / OHE)**: Overhead catenary wire, contact wire, cantilevers, neutral sections, substations (managed via **TDMS** - Traction Distribution Management System).
3. **Signal & Telecommunication (S&T)**: Electronic Interlocking (EI), point machines, digital axle counters, track circuits, signals (managed via **SMMS** - Signalling Maintenance & Management System).

Operational train movements and corridor availability are managed through systems such as **COA (Control Office Application)**.

### The Real-World Challenge
Because each department submits block requests in silos:
- **Duplicate & Fragmented Blocks**: Section S01 is blocked 10:00–12:00 for track maintenance, then blocked again 14:00–15:00 for OHE inspection, and again next day for signalling testing.
- **Corridor Capacity Choke**: Multiple separate possessions multiply asset downtime and cause cascading delays across passenger and freight corridors.
- **Train Clashes**: Uncoordinated possessions clash with high-priority trains (Vande Bharat, Rajdhani, Goods rakes).

---

## 2. The Solution: Coordinated Multi-Department Block Optimization

**SIH26027** is an AI-assisted decision-support platform that unifies maintenance demands from TMS, TDMS, and SMMS, analyzes train schedules from COA, and uses mathematical optimization to:
- **Detect Spatially & Temporally Compatible Activities**: Merge maintenance tasks occurring on the same or adjacent sections into coordinated multi-department blocks.
- **Avoid Operational Train Conflicts**: Identify optimal daylight and night shadow windows that minimize interference with high-priority passenger and freight trains.
- **Provide Dynamic, Measurable Improvement**: Quantify the exact hours of asset downtime saved, block count reduction, and punctuality protection compared to baseline manual planning.

```
+-----------------------------------------------------------------------------------+
| BEFORE (Independent Manual Planning):                                             |
|   Engineering Block (Track Tamping):        10:00 - 12:00 (2.0 hours)             |
|   OHE Block (Contact Wire Check):           10:30 - 11:30 (1.0 hour)              |
|   Signalling Block (Point Machine Testing): 11:00 - 12:00 (1.0 hour)              |
|   --> Total Track Possession = 4.0 Hours across 3 Separate Disruptions             |
+-----------------------------------------------------------------------------------+
| AFTER (AI-Assisted Coordinated Planning):                                         |
|   Coordinated Block (ENG + OHE + S&T):     10:00 - 12:00 (2.0 hours)             |
|   --> Total Track Possession = 2.0 Hours in 1 Single Coordinated Possession       |
|   --> Measured Improvement = 50% Downtime Reduction, 67% Fewer Corridor Closures   |
+-----------------------------------------------------------------------------------+
```

---

## 3. Synthetic Data Disclaimer

> [!IMPORTANT]
> **This prototype uses synthetic data because internal railway maintenance systems such as TMS, SMMS, TDMS and operational interfaces are not publicly accessible.**
>
> All station codes (e.g. NDLS, CNB, PRYJ, DDU), section topologies, asset numbers, maintenance tasks, and train movements are generated using realistic operational rules modeled after Indian Railways high-density trunk routes (Delhi-Kanpur-Prayagraj-Pt. Deen Dayal Upadhyaya Jn corridor). No internal railway credentials or live operational systems are accessed.

---

## 4. System Architecture

```
                ┌───────────────────────────────────────────┐
                │             Maintenance Data              │
                │        TMS (ENG) / TDMS (OHE) / SMMS (S&T)│
                └─────────────────────┬─────────────────────┘
                                      │
                                      ▼
                ┌───────────────────────────────────────────┐
                │          Data Integration Layer           │
                │  - Ingestion Normalization & Validation   │
                └─────────────────────┬─────────────────────┘
                                      │
                                      ▼
                ┌───────────────────────────────────────────┐
                │            Task Priority Engine           │
                │  - Criticality + Urgency + Overdue        │
                │  - Asset Condition + Safety Requirements  │
                └─────────────────────┬─────────────────────┘
                                      │
                                      ▼
                ┌───────────────────────────────────────────┐
                │          Railway Availability Model       │
                │  - Corridor Availability + COA Timetable  │
                │  - Train Priority Weighting (1 to 5)      │
                └─────────────────────┬─────────────────────┘
                                      │
                                      ▼
                ┌───────────────────────────────────────────┐
                │         BLOCK OPTIMIZATION ENGINE         │
                │  - Mixed-Integer Linear Programming (MILP)│
                │  - PuLP / Google OR-Tools CP-SAT          │
                └─────────────────────┬─────────────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                Weekly Block Plan          Monthly Block Plan
                 (7-day horizon)            (30-day horizon)
                         │                         │
                         └────────────┬────────────┘
                                      ▼
                ┌───────────────────────────────────────────┐
                │             Planner Dashboard             │
                │  - Multi-Department Gantt Chart           │
                │  - Baseline vs Optimized KPIs             │
                │  - Synthetic Topology Map (Leaflet / OSM) │
                │  - Explainable Decision Modal             │
                └───────────────────────────────────────────┘
```

---

## 5. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Pydantic-Settings, SQLAlchemy 2.0
- **Database**: SQLite (local rapid zero-config development) / PostgreSQL (production)
- **Optimization**: PuLP (MILP with CBC/HiGHS solvers) / Google OR-Tools CP-SAT
- **Data Science & ML**: Pandas, NumPy, Scikit-learn
- **Frontend**: React 18, Vite, Tailwind CSS, Recharts, Leaflet + OpenStreetMap
- **Testing & Tooling**: Pytest, HTTPX, Docker, Docker Compose

---

## 6. Dataset Structure & Statistics

The dataset generator (`data/generate_data.py`) creates 9 synchronized CSV datasets:

| Dataset CSV | Description | Count | Target Standard |
| :--- | :--- | :--- | :--- |
| `departments.csv` | ENG (TMS), OHE (TDMS), S&T (SMMS) | 3 records | Multiple departments |
| `stations.csv` | Major junctions & block stations with coordinates | 105 stations | $\ge 100$ |
| `sections.csv` | Consecutive track sections with speed and line capacity | 55 sections | $\ge 50$ |
| `assets.csv` | Rails, catenaries, turnouts, point machines, axle counters | 416 assets | $\ge 300$ |
| `maintenance_tasks.csv`| Tasks with duration, crew, machinery, and urgency | 600 tasks | $\ge 500$ |
| `train_schedule.csv` | Vande Bharat, Rajdhani, Express, MEMU, Freight | 220 trains | $\ge 200$ |
| `train_movements.csv` | Spatio-temporal section entry/exit times over 7 days | 7,615 movements | $\ge 1,000$ |
| `corridor_availability.csv`| Day/night slot ratings for maintenance windows | 1,155 slots | 7-day operational horizon |
| `block_requests.csv` | Baseline uncoordinated manual requests | 436 requests | Real baseline comparison |

---

## 7. Installation & Quickstart

### Prerequisites
- Python 3.11+ (or Python 3.14/3.15)
- Node.js 18+ and npm
- Git

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-org/SIH26027.git
cd SIH26027

# Copy environment template
cp .env.example .env
```

### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Synthetic Dataset & Seed Database
```bash
# Generate high-fidelity synthetic IR operational dataset
python data/generate_data.py

# Initialize database schema and seed tables into backend/railway.db
python data/seed_db.py
```

### 4. Run Automated Tests
```bash
pytest tests/ -v
```

### 5. Launch Backend Server
```bash
uvicorn backend.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at: `http://localhost:8000/docs`

---

## 8. Implementation Phases & Roadmap

- [x] **Phase 1: Project Architecture, Data Generation & Database Models** (Complete)
  - Full project structure and configuration
  - Synthetic dataset generator (600 tasks, 220 trains, 55 sections, 105 stations)
  - Relational database schema with 12 SQLAlchemy ORM models
  - Unit test suite with 100% pass rate
  - Complete architecture, optimization, and demonstration documentation
- [ ] **Phase 2: Baseline Scheduler** (Independent department planning without coordination)
- [ ] **Phase 3: Task Priority Engine** (Explainable 5-factor scoring model)
- [ ] **Phase 4: Optimization Engine** (MILP block formulation and multi-department solver)
- [ ] **Phase 5: Conflict Detection & Train Avoidance Engine**
- [ ] **Phase 6: Baseline vs. Optimized Analytics & Improvement Metrics**
- [ ] **Phase 7: FastAPI Endpoints & REST Services**
- [ ] **Phase 8: React Dashboard & UI Framework**
- [ ] **Phase 9: Multi-Track Interactive Gantt Chart**
- [ ] **Phase 10: Synthetic Railway Topology Network Map (Leaflet / OSM)**
- [ ] **Phase 11: "What-If" Simulation Engine**
- [ ] **Phase 12: End-to-End Integration & Scenario Testing**
- [ ] **Phase 13: Docker Containerization & Deployment Configuration**

---

## 9. Ethics, Safety & Decision-Support Notice

- **Advisory Role**: The platform operates as a recommendation engine for human railway controllers.
- **Safety First**: Power isolation, caution orders, and track protection protocols must always follow Indian Railways General & Subsidiary Rules (G&SR).
- **No Signalling Override**: The software provides planning schedules and does not interface directly with physical interlocking or signals.
