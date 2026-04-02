# Standard Operating Procedure (SOP)
# Smart Factory Dashboard — Daily Operation Guide

| Field | Details |
|---|---|
| **Document Code** | SOP-SFD-001-EN |
| **Version** | 1.0 |
| **Language** | English |
| **Created** | 2026-04-02 |
| **Department** | Manufacturing / Smart Factory |
| **Applies To** | All operators and engineers using the Smart Factory Dashboard |
| **Review Cycle** | Every 6 months or upon system update |

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Scope](#2-scope)
3. [Responsibilities](#3-responsibilities)
4. [System Requirements](#4-system-requirements)
5. [Daily Startup Procedure](#5-daily-startup-procedure)
6. [Loading OEE Data](#6-loading-oee-data)
7. [Loading AGV Log Data](#7-loading-agv-log-data)
8. [Loading AOI Image Data](#8-loading-aoi-image-data)
9. [Reading and Interpreting the Dashboard](#9-reading-and-interpreting-the-dashboard)
10. [Date Filter Usage](#10-date-filter-usage)
11. [Hover Tooltip Usage](#11-hover-tooltip-usage)
12. [Terminal Log Monitoring](#12-terminal-log-monitoring)
13. [Common Errors and Troubleshooting](#13-common-errors-and-troubleshooting)
14. [End-of-Day Procedure](#14-end-of-day-procedure)
15. [Data File Management Rules](#15-data-file-management-rules)
16. [Emergency Contacts](#16-emergency-contacts)

---

## 1. Purpose

This Standard Operating Procedure (SOP) defines the step-by-step instructions for daily operation of the **Smart Factory Dashboard** system. The dashboard aggregates and visualises real-time and historical data from three core factory systems:

- **OEE (Overall Equipment Effectiveness)** — machine productivity data
- **AGV (Automated Guided Vehicle)** — material transport task logs
- **AOI (Automated Optical Inspection)** — product defect image results

The purpose is to ensure that every operator follows a consistent, reliable process when loading, reviewing, and reporting factory data, and to prevent data errors, system crashes, or misinterpretation of results.

---

## 2. Scope

This SOP applies to:

- All shift operators (Morning / Afternoon / Night)
- Production engineers and supervisors
- Quality engineers reviewing AOI pass rates
- Logistics staff reviewing AGV task distribution

This SOP does **not** cover:
- Software installation or environment setup (refer to INSTALL.md)
- Backend server configuration
- Modifying source code or configuration files

---

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| **Shift Operator** | Load daily data at shift start; monitor KPI cards; report anomalies |
| **Production Engineer** | Verify OEE data accuracy; review floor-level charts; filter by date |
| **Quality Engineer** | Review AOI pass rate; investigate FAIL images if rate < 90% |
| **Logistics Supervisor** | Monitor AGV task counts; identify busiest stations; log anomalies |
| **IT / System Admin** | Maintain Python environment; handle software errors; update config |

---

## 4. System Requirements

### 4.1 Hardware Minimum Specifications

| Component | Minimum Requirement |
|---|---|
| CPU | Intel Core i5 (8th gen) or equivalent |
| RAM | 8 GB |
| Storage | 50 GB free space |
| Display | 1366 × 768 resolution (Full HD 1920×1080 recommended) |
| Network | Connected to factory intranet (IP: 10.177.117.1) |

### 4.2 Software Requirements

| Software | Version | Notes |
|---|---|---|
| Windows | 10 / 11 (64-bit) | Required |
| Python | 3.10 or later | Must be in system PATH |
| PyQt5 | 5.15+ | UI framework |
| pandas | 1.5+ | Data processing |
| matplotlib | 3.6+ | Chart rendering |
| xlrd | 2.0+ | Reading `.xls` files |
| openpyxl | 3.0+ | Reading `.xlsx` files |

### 4.3 Required Data File Locations

Operators must know where to find the following data files before starting:

| Data Type | Expected Location | File Format |
|---|---|---|
| OEE Report | Shared network drive or USB | `.xls`, `.xlsx`, `.csv` |
| AGV Logs | Local AGV server export folder | `.txt` or `.log` (named `LogYYYYMMDDHH.txt`) |
| AOI Images | AOI machine output folder | Folder containing `.jpg` / `.bmp` / `.png` images |

---

## 5. Daily Startup Procedure

> ⚠️ **IMPORTANT**: Always complete steps in order. Do not skip any step.

### Step 1 — Open Terminal

1. Press `Win + R`, type `cmd`, press **Enter**
2. Navigate to the dashboard folder:
   ```
   cd D:\factory_dashboard
   ```

### Step 2 — Launch the Dashboard

Run the following command:
```bash
python main.py
```

**Expected terminal output at startup:**
```
(No errors shown — the GUI window opens automatically)
```

If the GUI does **not** open within 10 seconds, refer to [Section 13 — Troubleshooting](#13-common-errors-and-troubleshooting).

### Step 3 — Maximise the Window

The application should launch in full-screen mode automatically.  
If not, press `Win + ↑` or manually drag the window to full screen.

### Step 4 — Verify the UI Layout

Confirm the following panels are visible:

| Panel | Location | Description |
|---|---|---|
| ⚙️ Data Control | Top-left | Buttons to load each data type |
| 🔄 Total AGV Tasks | Top-centre | KPI card showing total AGV task count |
| 🖼️ AOI Pass Rate | Top-right | KPI card showing AOI pass percentage |
| Top Active Stations | Mid-left | Bar chart — AGV station activity |
| Action Ratio | Mid-centre | Pie chart — UP vs DOWN actions |
| Hourly Traffic Flow | Mid-right | Line chart — AGV tasks per hour |
| OEE F4 | Bottom-left | Bar chart — Floor 4 OEE per line |
| OEE F5 | Bottom-centre | Bar chart — Floor 5 OEE per line |
| AOI Quality Details | Bottom-right | Pie chart — PASS vs FAIL |

---

## 6. Loading OEE Data

> OEE data shows the productivity (%) of each manufacturing line on each floor.

### Step 1 — Click "📊 Load OEE File"

Located in the **⚙️ Data Control** panel (top-left).

### Step 2 — Select File(s)

A file browser dialog will open.

- Navigate to the OEE report folder
- Select one or multiple files (hold `Ctrl` to select multiple)
- Supported formats: `.xls`, `.xlsx`, `.csv`
- Click **Open**

> ⚠️ If no file is selected and you press Cancel, nothing happens. No error is shown.

### Step 3 — Wait for Processing

Watch the **terminal window** for processing progress:

```
[HH:MM:SS] [INFO] [OEE] Starting OEE processing – N file(s) selected
[HH:MM:SS] [INFO] [OEE] Reading file: filename.xls  (format: .xls)
[HH:MM:SS] [OK  ] [OEE] XLS loaded via xlrd – 527 rows
[HH:MM:SS] [INFO] [OEE] Merging 1 dataframe(s)…
[HH:MM:SS] [OK  ] [OEE] OEE numeric conversion done – 527/527 valid rows
[HH:MM:SS] [OK  ] [OEE] Processing complete in 0.07s – emitting data to UI
```

Processing is complete when you see **"Processing complete"** in the terminal.

### Step 4 — Verify Charts Updated

After loading:
- **OEE F4** chart (bottom-left) should show bars for each line on Floor 4 (4A, 4B, 4C…)
- **OEE F5** chart (bottom-centre) should show bars for each line on Floor 5 (5G, 5H…)
- The **📅 Date Filter** dropdown will populate with available dates

### Step 5 — Check for WARN or ERROR in Terminal

| Terminal Message | Action Required |
|---|---|
| `[WARN] xlrd failed… trying HTML fallback` | Normal — file is HTML-encoded `.xls`, fallback handled automatically |
| `[WARN] Column 'OEE' not found` | The OEE column is missing — verify you selected the correct file |
| `[ERROR] Cannot read 'filename.xls'` | File is corrupted — obtain a new copy from source system |
| `[ERROR] No valid data could be read` | All selected files failed — contact IT |

---

## 7. Loading AGV Log Data

> AGV log data shows how many tasks each station received and when they occurred.

### Step 1 — Click "📜 Load AGV Logs"

Located in the **⚙️ Data Control** panel.

### Step 2 — Select Log File(s)

- Navigate to the AGV log export folder
- Log files are typically named: `Log2026040108.txt` (format: `LogYYYYMMDDHH.txt`)
- Select all files for the desired time range (hold `Ctrl` for multiple)
- Click **Open**

> 💡 **Tip**: For a full-day analysis, select all 24 hourly log files for a given date (00 through 23).

### Step 3 — Monitor Terminal Output

```
[HH:MM:SS] [INFO] [AGV] Starting AGV log processing – 17 file(s) selected
[HH:MM:SS] [INFO] [AGV] Scanning: Log2026040108.txt
[HH:MM:SS] [OK  ] [AGV]   → Log2026040108.txt: 24 task records found
...
[HH:MM:SS] [OK  ] [AGV] Total tasks: 248  |  Elapsed: 0.21s
[HH:MM:SS] [INFO] [AGV] Top stations: [('4C', 80), ('4D-Revlon1-3', 60), ('R650', 40)]
[HH:MM:SS] [INFO] [AGV] Action breakdown: {'DOWN': 124, 'UP': 124}
[HH:MM:SS] [INFO] [AGV] Hourly buckets: 17 hour(s) – emitting to UI
```

### Step 4 — Verify KPI Card Updated

The **🔄 Total AGV Tasks** card should now show:
- **Large number**: Total task count
- **Subtitle**: Busiest station name and processing time

### Step 5 — Verify Charts Updated

| Chart | Expected Content |
|---|---|
| Top Active Stations | Up to 10 bars, sorted descending by task count |
| Action Ratio | Pie with UP/DOWN percentages |
| Hourly Traffic Flow | Line chart with one point per hour |

### Step 6 — Abnormal Readings

| Situation | Meaning | Action |
|---|---|---|
| Total tasks = 0 | No valid log lines parsed | Check if log files are from the correct folder |
| Only "Unknown(XXXX)" stations | Point IDs not in config | Report to IT — POINT_MAP may need updating |
| Action Ratio shows only "DOWN" | AGV only recorded pickups | Verify log files are complete |

---

## 8. Loading AOI Image Data

> AOI data shows the product quality results — how many boards passed or failed inspection.

### Step 1 — Click "🖼️ Select AOI Folder"

Located in the **⚙️ Data Control** panel.

### Step 2 — Select the AOI Output Folder

A folder browser will open.

- Navigate to the AOI machine's image output folder
- Select the **root folder** containing the date/batch subfolders
- Click **Select Folder**

> ⚠️ The system will recursively scan all subfolders up to **5 levels deep**.
> Files that are NOT images (`.jpg`, `.bmp`, `.png`, `.tif`) are automatically skipped.

### Step 3 — Monitor Terminal Output

```
[HH:MM:SS] [INFO] [AOI] Starting AOI folder scan – 1 folder(s) selected
[HH:MM:SS] [INFO] [AOI] Walking folder: D:\AOI\2026-04-02
[HH:MM:SS] [INFO] [AOI]   .: 17 image(s), 3 non-image file(s) skipped
[HH:MM:SS] [OK  ] [AOI] Folder summary → Pass: 7 | Fail: 10 | Pass rate: 41.2% | Unclassified: 0
[HH:MM:SS] [OK  ] [AOI] Grand total → Pass: 7 | Fail: 10 | Pass rate: 41.2%
[HH:MM:SS] [INFO] [AOI] Scan complete in 0.01s – emitting to UI
```

### Step 4 — Verify KPI Card Updated

The **🖼️ AOI Pass Rate** card will show:
- **Percentage**: Current pass rate
  - 🟢 Green = ≥ 90% (acceptable)
  - 🔴 Red = < 90% (requires investigation)
- **Subtitle**: `Pass: N | Fail: N`

### Step 5 — Action on Low Pass Rate

If pass rate < 90%:

1. Note the Pass and Fail counts from the dashboard
2. Open the AOI image folder and sort by filename
3. Files containing `"all pass"` in the name = PASS result
4. Files containing `"fail"` in the name = FAIL result
5. Report to Quality Engineer immediately
6. Log the incident in the daily quality report

---

## 9. Reading and Interpreting the Dashboard

### 9.1 KPI Cards

| Card | Normal Range | Action if Abnormal |
|---|---|---|
| Total AGV Tasks | Varies by shift; should be consistent day-over-day | Investigate if count drops >30% vs previous day |
| AOI Pass Rate | ≥ 90% | Escalate immediately if < 90% |

### 9.2 OEE Bar Charts (Floor F4 / F5)

- **Y-axis**: OEE percentage (0–100%)
- **X-axis**: Production line name (4A, 4B, 4C…)
- **Normal OEE**: ≥ 85% is considered world-class
- **Warning OEE**: < 70% requires investigation
- **Hover over a bar** to see exact OEE value

### 9.3 AGV Station Bar Chart

- Shows the busiest stations (top 10, excluding PATH)
- High-count stations = frequently served → verify AGV schedule matches production demand

### 9.4 Action Ratio Pie Chart

- **DOWN** = AGV picking up materials (feeding to machine)
- **UP** = AGV returning (recovering from machine)
- Ratio should be approximately 50/50; large imbalance may indicate stuck tasks

### 9.5 Hourly Traffic Flow Line Chart

- Shows total AGV task count per hour
- Peaks should align with production shift changes
- Flat periods may indicate AGV downtime or pause in production

---

## 10. Date Filter Usage

After loading OEE data, the **📅 Date Filter** dropdown is populated with available dates.

**To filter by a specific date:**
1. Click the dropdown
2. Select a date (format: `YYYY/MM/DD`)
3. All OEE charts automatically refresh for that date

**To return to all-date view:**
1. Select `📅 Date Filter (All)` from the top of the list

> ⚠️ If the dropdown shows only `"📅 Date Filter (All)"`, either the OEE file has not been loaded yet, or the file does not contain a date column (`日`).

---

## 11. Hover Tooltip Usage

All charts support hover tooltips to display exact values.

**How to use:**
1. Move your mouse cursor over any bar, wedge, or line point
2. A tooltip popup will appear showing:
   - For **bar charts**: Label and exact value
   - For **pie charts**: Label, count, and percentage
   - For **line charts**: Hour and task count

> 💡 Tooltips are particularly useful for OEE lines that are close in value and hard to distinguish by bar height alone.

---

## 12. Terminal Log Monitoring

The terminal window must remain **open** during operation. It reflects the real-time processing state.

### 12.1 Log Level Colour Key

| Colour | Level | Meaning |
|---|---|---|
| 🔵 Cyan | `INFO` | Normal step in progress |
| 🟢 Green | `OK` | Step completed successfully |
| 🟡 Yellow | `WARN` | Non-fatal issue; automatic fallback used |
| 🔴 Red | `ERROR` | Failed step — action required |

### 12.2 When to Escalate

Escalate to IT or your supervisor if you see any of the following:

- `[ERROR]` messages that stop the process
- Charts not updating after a successful `[OK] … emitting to UI`
- Application closes unexpectedly
- Terminal shows `Traceback` (Python crash)

---

## 13. Common Errors and Troubleshooting

| Error / Symptom | Likely Cause | Solution |
|---|---|---|
| GUI does not open | Python not installed or wrong environment | Run `python --version` in CMD; contact IT if missing |
| `ModuleNotFoundError: PyQt5` | Dependencies not installed | Run `pip install PyQt5 pandas matplotlib xlrd openpyxl` |
| Charts remain blank after loading | File format mismatch or missing columns | Check terminal for `[WARN]` or `[ERROR]` messages |
| OEE bars only show for F4 (not F5) | No F5 data in the selected file | Verify OEE file contains rows with 樓層 = 'F5' |
| "A data loading task is already in progress" popup | Buttons clicked too quickly | Wait for current task to complete, then proceed |
| AOI Pass Rate = 0% with 0 Pass / 0 Fail | Wrong folder selected (no matching images) | Verify folder contains images named with "all pass" or "fail" |
| xls file shows `[WARN] xlrd failed` then proceeds | File is HTML-encoded `.xls` (common from web exports) | Normal — fallback is automatic; data should still load |
| `[ERROR] No valid data` for OEE | All files failed to parse | Obtain fresh export from the source system |
| Application crashes (Traceback in terminal) | Unexpected runtime error | Screenshot the terminal; restart application; report to IT |

---

## 14. End-of-Day Procedure

### Step 1 — Take Screenshot of Dashboard

Before closing, press `PrtSc` or use Snipping Tool (`Win + Shift + S`) to capture the full dashboard for the daily report.

### Step 2 — Note Key Metrics

Record the following in your daily log / report:

| Metric | Value Today |
|---|---|
| Total AGV Tasks | ___ |
| Busiest Station | ___ |
| AOI Pass Rate | __% |
| OEE F4 Average | __% |
| OEE F5 Average | __% |
| Any anomalies | Yes / No — describe |

### Step 3 — Close the Application

Press `Alt + F4` or close the window using the X button.  
Then close the terminal window.

### Step 4 — Archive Data Files

Move processed data files to the archive folder according to your site's data retention policy.

---

## 15. Data File Management Rules

### OEE Files
- Naming convention: `OEE_Report_YYYYMMDD.xls` (or `.xlsx`)
- Store in: `\\server\shared\OEE\YYYY\MM\`
- Retention: 12 months minimum

### AGV Log Files
- Naming convention: `LogYYYYMMDDHH.txt` (auto-generated by AGV server)
- Store in: `\\server\shared\AGV_Logs\YYYY\MM\DD\`
- Retention: 6 months minimum

### AOI Image Files
- Folder naming convention: `YYYYMMDD_BatchID\`
- Store in: `\\server\shared\AOI\YYYY\MM\`
- Retention: 3 months minimum (or per quality audit requirements)

> ⚠️ **Never delete raw log or image files** without sign-off from the Quality Manager.

---

*End of Document — SOP-SFD-001-EN v1.0*
