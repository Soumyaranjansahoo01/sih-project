# Developer Guide: VS Code Workflow & Mobile View Implementation

## SIH26027: AI-Powered Automatic Block Planning for Indian Railways

This guide walks you step-by-step through developing, running, debugging, and viewing the project inside **Visual Studio Code (VS Code)**, as well as testing and developing for **Mobile / Tablet Views**.

---

## Part 1: VS Code Step-by-Step Setup & Execution

### 1. Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File > Open Folder...** (or press `Ctrl + K`, `Ctrl + O`).
3. Select the folder:
   `c:\Users\HP\OneDrive\Desktop - Copy\Desktop\SIH26027`

---

### 2. Select the Python Interpreter
1. Press `Ctrl + Shift + P` to open the Command Palette.
2. Type and select: `Python: Select Interpreter`.
3. Choose **Python 3.14 (64-bit)**:
   `C:\Users\HP\AppData\Local\Programs\Python\Python314\python.exe`
   *(This is pre-configured in `.vscode/settings.json`)*.

---

### 3. Recommended VS Code Extensions
Open the Extensions view (`Ctrl + Shift + X`) and install:
- **Python** (by Microsoft)
- **Pylance** (by Microsoft)
- **Thunder Client** or **REST Client** (for API testing inside VS Code)
- **Tailwind CSS IntelliSense** (for frontend design)
- **ESLint** & **Prettier**

---

### 4. Running the Backend in VS Code

You have three convenient ways to run the backend:

#### Option A: One-Click Debugging (F5)
1. Press `Ctrl + Shift + D` to open the **Run & Debug** panel.
2. Select **"FastAPI: Run Backend Server (Reload)"** from the dropdown.
3. Press **F5** (or click the green Play button).
4. VS Code will launch Uvicorn with auto-reload at:
   - Root URL: `http://localhost:8000`
   - Interactive Swagger API: `http://localhost:8000/docs`
   - Baseline Endpoint: `http://localhost:8000/baseline`

#### Option B: Built-in VS Code Task
1. Press `Ctrl + Shift + B` (or `Terminal > Run Build Task...`).
2. Select **"Run Backend Server"**.

#### Option C: Integrated Terminal
1. Press ``Ctrl + ` `` to open the integrated PowerShell terminal.
2. Run:
   ```powershell
   py -3.14 -m uvicorn backend.main:app --reload --port 8000
   ```

---

### 5. Running Tests in VS Code

#### Option A: The Testing Explorer (GUI)
1. Click the **Testing (Flask icon)** on the left sidebar.
2. Click **Run Tests** (Play icon).
3. VS Code discovers all 16 tests in `tests/` and shows green checkmarks next to each passed test.

#### Option B: Terminal Command
```powershell
py -3.14 -m pytest tests -v
```

---

## Part 2: Mobile View Implementation & Testing Guide

In Indian Railways operations, section controllers typically work on large multi-monitor consoles, but **divisional officers, field safety supervisors, and inspection gangs require mobile/tablet access** to verify track blocks and train conflicts on the move.

### 1. How to Test Mobile View in VS Code & Chrome

#### In Google Chrome / Edge:
1. Open `http://localhost:8000/docs` (or your frontend when running).
2. Press **F12** to open Developer Tools.
3. Press `Ctrl + Shift + M` (or click the **Device Toggle icon** in the top-left of DevTools).
4. In the top dropdown, select a device preset:
   - **iPhone 14 Pro / 15** (393 × 852 px)
   - **Samsung Galaxy S20 / Ultra** (412 × 915 px)
   - **iPad Air / Pro** (820 × 1180 px - Tablet controller view)
5. Test:
   - Portrait orientation and Landscape orientation.
   - Touch scrolling and swipe gestures.

#### Direct Mobile Device Testing (Local Wi-Fi):
To view the prototype directly on your physical smartphone connected to the same Wi-Fi:
1. In PowerShell, find your local IP address:
   ```powershell
   ipconfig
   ```
   *(Look for `IPv4 Address`, e.g., `192.168.1.15`)*
2. The FastAPI server is already configured to listen on `0.0.0.0` (all network interfaces).
3. On your mobile phone browser, open:
   `http://192.168.1.15:8000/docs`
   or
   `http://192.168.1.15:8000/baseline`

---

### 2. Key Mobile UI Design Principles Implemented

When designing the frontend components (Phase 8–10), we follow these mobile-first responsive design standards:

| Component | Desktop Experience | Mobile / Tablet Experience |
| :--- | :--- | :--- |
| **KPI Metric Cards** | 4-column horizontal grid (`grid-cols-4`) | 1 or 2-column stacked layout (`grid-cols-1 sm:grid-cols-2`) |
| **Navigation** | Sticky left sidebar (260px) | Collapsible bottom navigation bar or sliding drawer hamburger menu |
| **Gantt Chart** | Full panoramic timeline | Horizontally swipeable container (`overflow-x-auto`) with touch pinch-to-zoom |
| **Railway Map** | Fullscreen multi-section Leaflet canvas | Responsive viewport with floating touch controls and bottom modal drawer |
| **Data Tables** | Wide multi-column tables | Card-based stacked list views for tasks and conflicts on small viewports |
| **Touch Targets** | Standard 32px buttons | Minimum 48px touch-friendly hit areas for field glove accessibility |

---

### 3. Responsive Breakpoints Reference (Tailwind CSS)

When building UI components:
```tsx
// Example responsive layout pattern:
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
  {/* KPI Cards automatically wrap on mobile screens */}
  <KpiCard title="Total Blocks" value={metrics.number_of_blocks} />
  <KpiCard title="Downtime" value={`${metrics.total_block_hours} hrs`} />
  <KpiCard title="Conflicts" value={metrics.total_train_conflicts} alert />
  <KpiCard title="Tasks" value={metrics.total_tasks} />
</div>
```

- `< 640px` (`default`): Mobile portrait (stacked 1-column layout)
- `640px` (`sm:`): Mobile landscape / small tablets (2-column layout)
- `768px` (`md:`): Tablets (intermediate dashboard layout)
- `1024px` (`lg:`): Desktop / Railway Controller Workstation (full panoramic layout)
