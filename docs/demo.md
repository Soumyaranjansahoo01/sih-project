# SIH 2026 Jury Demonstration Flow: SIH26027

## AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways

---

## 1. Opening Narrative (The Operational Problem)
- Introduce the real-world operational friction in Indian Railways:
  - **TMS** (Civil P-Way), **TDMS** (OHE Electrification), and **SMMS** (Signalling) each request track possessions independently.
  - Section controllers manually grant separate blocks at different hours, causing frequent corridor closures, train punctuality loss, and wasted capacity.
- **The Core Solution**:
  - Automatically synthesize maintenance needs from all three departments.
  - Formulate mathematically coordinated blocks that consolidate multiple activities into the same track possession window.
  - Safeguard train traffic schedules by avoiding clashes with high-priority services.

---

## 2. Step-by-Step Live Demonstration Script

| Step | Screen / Action | What the Jury Sees | Key Talking Point |
| :--- | :--- | :--- | :--- |
| **1** | **Operational Dashboard** | System overview, 600 tasks, 220 trains, 55 sections across Delhi–Kanpur–Prayagraj–DDU trunk route. | "All data is dynamically modeled with realistic IR operational parameters." |
| **2** | **Maintenance Ingestion** | Tasks from ENG (Track tamping), OHE (Catenary check), S&T (Point machine test). | "Every task has transparent priority scoring based on criticality, overdue days, and safety." |
| **3** | **Timetable View** | 7-day train movement diagram with Vande Bharat, Rajdhani, and freight corridors. | "The optimizer respects train timetable density and avoids blocking premium traffic." |
| **4** | **Baseline Generation** | Click **"Generate Baseline Plan"**. Independent department blocks appear. | "Notice how independent scheduling creates 30+ separate blocks and high asset downtime." |
| **5** | **Run AI Optimization** | Click **"Run Block Optimizer"**. Solver computes coordinated plan in seconds. | "The MILP engine identifies spatially and temporally compatible activities on the same section." |
| **6** | **Gantt Chart Review** | Coordinated blocks showing combined ENG + OHE + S&T badges. | "Instead of 3 separate track possessions totaling 4.5 hours, 1 combined 2-hour window finishes all 3 tasks." |
| **7** | **Measurable Comparison** | KPI Comparison Panel: Downtime saved (hrs), Block reduction (%), Conflict reduction (%). | "Every number is calculated dynamically by the solver from the dataset, not hardcoded." |
| **8** | **Interactive Map** | Geographic corridor view with color-coded section status and active blocks. | "Controllers can inspect section health, active maintenance, and train movements at a glance." |
| **9** | **Explainable AI Modal** | Click any block to view decision justification. | "Controllers see exact reasons: priority factors, avoided train clashes, and co-located tasks." |
| **10**| **What-If Simulation** | Adjust train density or introduce an emergency track fracture defect. | "The solver re-plans immediately, elevating emergency tasks and identifying safe windows." |

---

## 3. Key Jury Takeaway
> **"Coordinating maintenance blocks across Engineering, OHE, and Signalling reduces corridor downtime while respecting train operations."**
