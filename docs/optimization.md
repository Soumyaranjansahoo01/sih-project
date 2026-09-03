# Mathematical Optimization Formulation

## 1. Problem Formulation: Coordinated Block Scheduling

In Indian Railways, uncoordinated track possession requests from Civil Engineering (ENG), Overhead Electrification (OHE), and Signal & Telecommunication (S&T) cause fragmented corridor closures, train delays, and low asset utilization.

The **SIH26027 Optimization Engine** solves a Mixed-Integer Linear Program (MILP) to identify compatible maintenance activities and merge them into synchronized maintenance blocks while avoiding train operations.

---

## 2. Mathematical Model

### Sets & Indices
- $T$: Set of maintenance tasks, index $i \in T$.
- $S$: Set of corridor railway sections, index $s \in S$.
- $W$: Set of potential maintenance windows / candidate time slots, index $w \in W$.
- $D$: Set of departments $D = \{\text{ENG}, \text{OHE}, \text{S\&T}\}$, index $d \in D$.
- $R$: Set of scheduled train movements, index $r \in R$.

### Parameters
- $P_i \in [0, 100]$: Composite priority score of maintenance task $i$.
- $\text{dur}_i$: Required duration of task $i$ (minutes).
- $\text{cap}_w$: Available duration of time window $w$ (minutes).
- $\text{sec}_i \in S$: Section required by task $i$.
- $\text{dept}_i \in D$: Department requesting task $i$.
- $\text{crew}_i$: Specialized gang/crew required for task $i$.
- $\text{train\_impact}_{s, w}$: Weighted penalty score of scheduled train movements traversing section $s$ during window $w$.
- $\text{compat}_{i, j} \in \{0, 1\}$: Binary parameter indicating physical and safety compatibility between tasks $i$ and $j$.

### Decision Variables
- $x_{i, w} \in \{0, 1\}$: 1 if task $i$ is assigned to maintenance window $w$; 0 otherwise.
- $y_{s, w} \in \{0, 1\}$: 1 if a track block is activated on section $s$ during window $w$; 0 otherwise.
- $z_{s, w} \in \{0, 1\}$: 1 if window $w$ on section $s$ hosts a **multi-department coordinated block** (at least 2 departments); 0 otherwise.

---

## 3. Objective Function

$$\max \mathcal{Z} = \lambda_1 \sum_{i \in T} \sum_{w \in W} P_i \cdot x_{i, w} + \lambda_2 \sum_{s \in S} \sum_{w \in W} z_{s, w} - \lambda_3 \sum_{s \in S} \sum_{w \in W} \text{dur}_w \cdot y_{s, w} - \lambda_4 \sum_{i \in T} \sum_{w \in W} \text{train\_impact}_{\text{sec}_i, w} \cdot x_{i, w}$$

Where:
- $\lambda_1$: Weight on completing high-priority and critical maintenance tasks.
- $\lambda_2$: Incentive reward for multi-department coordination (combining ENG + OHE + S&T).
- $\lambda_3$: Penalty for total corridor downtime (minimizing track closure hours).
- $\lambda_4$: Penalty for train traffic disruptions.

---

## 4. Key Constraints

### 4.1 Task Assignment Limit
Each task can be scheduled at most once:
$$\sum_{w \in W} x_{i, w} \le 1 \quad \forall i \in T$$

### 4.2 Block Activation Coupling
If any task $i$ is scheduled in window $w$ on section $s = \text{sec}_i$, the block must be active:
$$x_{i, w} \le y_{\text{sec}_i, w} \quad \forall i \in T, \forall w \in W$$

### 4.3 Window Capacity Constraint
The maximum task duration in any window $w$ cannot exceed the window duration:
$$\text{dur}_i \cdot x_{i, w} \le \text{cap}_w \quad \forall i \in T, \forall w \in W$$

### 4.4 Multi-Department Coordination Trigger
Let $\text{dept\_count}_{s, w} = \sum_{d \in D} \min\left(1, \sum_{i \in T: \text{sec}_i = s, \text{dept}_i = d} x_{i, w}\right)$.
If $\text{dept\_count}_{s, w} \ge 2$, then $z_{s, w} = 1$:
$$z_{s, w} \le \frac{1}{2} \sum_{i \in T: \text{sec}_i = s} x_{i, w} \quad \forall s \in S, \forall w \in W$$

### 4.5 Train Non-Interference
High-priority trains (e.g. Vande Bharat, Rajdhani) impose absolute hard barriers or high penalty multipliers on window activation:
$$y_{s, w} \cdot \text{has\_premium\_train}_{s, w} = 0$$

---

## 5. Demonstration Example: Measurable Mathematical Gain

- **Baseline Manual Planning**:
  - ENG requests 120 min block on Section S01 (10:00–12:00) = 2.0 h
  - OHE requests 60 min block on Section S01 (10:30–11:30) = 1.0 h
  - S&T requests 60 min block on Section S01 (11:00–12:00) = 1.0 h
  - **Total Baseline Downtime = 4.0 hours across 3 independent blocks.**

- **AI Coordinated Block**:
  - Unified Block scheduled: 10:00–12:00 on Section S01
  - Tasks executed simultaneously with safety de-energization and track possession.
  - **Total Optimized Downtime = 2.0 hours in 1 block.**
  - **Measurable Result**: 50% downtime reduction, 66.7% reduction in total blocks.
