# System Architecture Specification

## Project: SIH26027 – AI-Powered Automatic Block Planning for Indian Railways
**Organization**: Ministry of Railways (MoR)  
**Theme**: Transportation & Logistics  
**Category**: Software (Decision-Support System)

---

## 1. High-Level Architecture

The platform aggregates siloed maintenance demands across civil engineering, electrical traction distribution, and signalling, cross-references these against corridor availability and operational train timetables (COA), and deploys an explainable mathematical optimization engine to formulate coordinated, multi-department track possessions.

```
                     ┌────────────────────────────────────────────────────────┐
                     │           Maintenance Management Systems               │
                     │  TMS (P-Way/Civil) │ TDMS (OHE) │ SMMS (Signalling)    │
                     └─────────────────────────┬──────────────────────────────┘
                                               │
                                               ▼
                     ┌────────────────────────────────────────────────────────┐
                     │              Data Integration Layer                    │
                     │  - Ingestion Normalization & Validation                │
                     │  - Asset Condition & Overdue Tracking                  │
                     └─────────────────────────┬──────────────────────────────┘
                                               │
                                               ▼
                     ┌────────────────────────────────────────────────────────┐
                     │               Task Priority Engine                     │
                     │  - Multi-Factor Priority Scoring (0-100)               │
                     │  - Explainable Classification (Critical/High/Med/Low)  │
                     └─────────────────────────┬──────────────────────────────┘
                                               │
               ┌───────────────────────────────┴──────────────────────────────┐
               │                                                              │
               ▼                                                              ▼
┌───────────────────────────────┐                             ┌───────────────────────────────┐
│     Operational Timetable     │                             │     Corridor Availability     │
│   COA Train Movements (1-5)   │                             │   Day/Night Maintenance Slots │
└──────────────┬────────────────┘                             └──────────────┬────────────────┘
               │                                                             │
               └───────────────────────────────┬─────────────────────────────┘
                                               │
                                               ▼
                     ┌────────────────────────────────────────────────────────┐
                     │          BLOCK SCHEDULING OPTIMIZATION ENGINE          │
                     │  - MILP / CP-SAT Mathematical Solver (PuLP/CBC)        │
                     │  - Section Spatial-Temporal Conflict Constraints       │
                     │  - Multi-Department Co-location Compatibility Logic     │
                     │  - Train Path De-confliction & Delay Minimization      │
                     └─────────────────────────┬──────────────────────────────┘
                                               │
                         ┌─────────────────────┴─────────────────────┐
                         ▼                                           ▼
             ┌───────────────────────┐                   ┌───────────────────────┐
             │   Weekly Block Plan   │                   │  Monthly Block Plan   │
             │ (Hourly Slot Level)   │                   │  (Daily Slot Level)   │
             └───────────┬───────────┘                   └───────────┬───────────┘
                         │                                           │
                         └─────────────────────┬─────────────────────┘
                                               │
                                               ▼
                     ┌────────────────────────────────────────────────────────┐
                     │               Interactive Controller UI                │
                     │  - Executive KPI Cards & Dynamic Comparison Metrics    │
                     │  - Multi-Track Gantt Chart (ENG, OHE, S&T)             │
                     │  - Prototype Railway Topology Map (Leaflet / OSM)      │
                     │  - Explainable AI Rationale Modal                      │
                     │  - Interactive "What-If" Simulation Engine             │
                     └────────────────────────────────────────────────────────┘
```

---

## 2. Core Functional Components

### 2.1 Data Integration Layer
- **Source Systems Modeled**:
  - **TMS (Track Management System)**: Tracks, turnout crossings, ballast, sleeper renewals.
  - **TDMS (Traction Distribution Management System)**: Overhead contact wire, catenary, insulators, substations.
  - **SMMS (Signalling Maintenance & Management System)**: Point machines, digital axle counters, audio-frequency track circuits, electronic interlocking.
- **Corridor Topology**:
  - Models realistic double and triple-line high-density trunk routes (inspired by Northern Railway / North Central Railway New Delhi–Kanpur–Prayagraj–Pt. Deen Dayal Upadhyaya corridor).
  - Stations, sections, track lengths, permissible speeds, line capacities, and electrified statuses.

### 2.2 Task Priority Engine
- **Scoring Function**: Calculates a dynamic transparent score $P_i \in [0, 100]$:
  $$P_i = w_c \cdot C_i + w_u \cdot U_i + w_o \cdot O_i + w_a \cdot A_i + w_s \cdot S_i$$
  where:
  - $C_i$: Asset Criticality Level (1 to 5)
  - $U_i$: Operational Urgency (Immediate, High, Normal, Low)
  - $O_i$: Overdue Maintenance Days
  - $A_i$: Inverse Condition Score $(100 - \text{condition})$
  - $S_i$: Safety Isolation Requirements (Traffic Block, Power Block)
- **Explainability**: Outputs explicit natural-language justifications for each score (e.g., "18 days overdue; Poor asset condition; Safety-critical catenary").

### 2.3 Train Conflict Engine
- Tracks precise train entry and exit timestamps per corridor section.
- Weights conflicts according to train class (Vande Bharat / Rajdhani = Priority 5; Express = Priority 4; Freight = Priority 1–2).
- Automatically rejects maintenance windows causing major corridor choke-points.

### 2.4 Multi-Department Coordination Engine
- Detects tasks across Engineering, OHE, and S&T sharing:
  1. Identical physical section ID or adjacent interlocking limits.
  2. Overlapping or contiguous execution horizons.
  3. Compatible safety requirements (e.g. OHE power de-energization combined with mechanical track tamping).
- Combines $N$ separate requests into a single unified track block, maximizing downtime savings.

---

## 3. Database Schema Blueprint
The system uses a relational architecture running SQLite (local development) and PostgreSQL (containerized production):
1. `departments`: System source (TMS/SMMS/TDMS), department code, metadata.
2. `stations`: 100+ stations with GIS coordinates and line topology.
3. `sections`: 50+ corridor track segments with speed limits, distance, and capacity.
4. `assets`: 400+ physical assets with degradation condition score, last/next maintenance dates.
5. `maintenance_tasks`: 600+ tasks with crew/machinery constraints and priority indices.
6. `trains`: 220 passenger, superfast, premium, and freight services.
7. `train_movements`: 7,600+ scheduled spatio-temporal section movements over 7 days.
8. `block_requests`: Baseline independent manual requests.
9. `optimization_runs`: Run metadata, baseline vs. optimized KPIs, execution time.
10. `optimized_blocks`: Coordinated maintenance windows.
11. `block_task_assignments`: Multi-department task mappings to scheduled blocks.
12. `conflicts`: Detected operational or timetable clashes and resolution pathways.
