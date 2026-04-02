import sys
import os
import re
import math
import time
import warnings
import io
from collections import defaultdict

# --- Suppress Qt EUDC font warning (harmless, Windows-only) ---
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts.warning=false")
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QPushButton, QFileDialog,
                             QLabel, QFrame, QComboBox, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Tắt hoàn toàn cảnh báo rác
warnings.filterwarnings("ignore")

# ==========================================
# LOGGING HELPER – coloured terminal output
# ==========================================
_COLORS = {
    "INFO" : "\033[96m",   # Cyan
    "OK"   : "\033[92m",   # Green
    "WARN" : "\033[93m",   # Yellow
    "ERROR": "\033[91m",   # Red
    "RESET": "\033[0m",
    "DIM"  : "\033[2m",
    "BOLD" : "\033[1m",
}

def log(level: str, tag: str, msg: str) -> None:
    """Print a timestamped, coloured log line to the terminal."""
    c      = _COLORS.get(level.upper(), "")
    reset  = _COLORS["RESET"]
    dim    = _COLORS["DIM"]
    bold   = _COLORS["BOLD"]
    ts     = time.strftime("%H:%M:%S")
    prefix = f"{dim}[{ts}]{reset} {bold}{c}[{level.upper():5s}]{reset}"
    tag_s  = f"{c}[{tag}]{reset}"
    print(f"{prefix} {tag_s} {msg}", flush=True)

# ==========================================
# 1. CẤU HÌNH TRẠM (STATIONS CONFIG)
# ==========================================
SYSTEM_IP = "10.177.117.1"
SYSTEM_PORT = "8000"

STATIONS = [
    {"name": "PATH",            "down": "1033, 1030, 1027", "up": "263, 1052"},
    {"name": "R650",            "down": "1205",              "up": "1200"},
    {"name": "R770",            "down": "1063",              "up": "1065"},
    {"name": "R370",            "down": "175",               "up": "1061"},
    {"name": "ICX-8100",        "down": "1039",              "up": "1041"},
    {"name": "UX7",             "down": "1037",              "up": "1067"},
    {"name": "4C",              "down": "991",               "up": "989"},
    {"name": "4D-Revlon1-3",    "down": "987",               "up": "798"},
    {"name": "4E-Revlon2-4",    "down": "805",               "up": "802"},
    {"name": "4J",              "down": "972",               "up": "971"},
    {"name": "4K",              "down": "970",               "up": "969"},
    {"name": "4L",              "down": "1263",              "up": "1260"},
    {"name": "4M",              "down": "1257",              "up": "1254"},
    {"name": "4N",              "down": "1251",              "up": "1248"},
    {"name": "4P",              "down": "1245",              "up": "1242"},
    {"name": "4A-LP48-NEW",     "down": "1751",              "up": "1749"},
    {"name": "4B-LP8-NEW",      "down": "1747",              "up": "1744"},
    {"name": "4C-NEW",          "down": "1723",              "up": "1724"},
    {"name": "4D-Revlon1-3-NEW","down": "1725",              "up": "1726"},
    {"name": "4E-Revlon2-4-NEW","down": "1727",              "up": "1728"},
]

# Build point → station name lookup (done once at startup)
POINT_MAP: dict[str, str] = {}
for st in STATIONS:
    for p in st['down'].split(','):
        POINT_MAP[p.strip()] = st['name']
    for p in st['up'].split(','):
        POINT_MAP[p.strip()] = st['name']

# Pre-compiled regex patterns – compiled once, reused everywhere
TIME_PATTERN  = re.compile(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}):\d{2}:\d{2}')
POINT_PATTERN = re.compile(r'"point":\s*"?(\d+)"?,\s*"action":\s*"?([a-zA-Z]+)"?')

# Image extensions recognised as AOI results
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}


# ==========================================
# 2. LUỒNG XỬ LÝ DỮ LIỆU ĐA NHIỆM
# ==========================================

class DataWorker(QThread):
    oee_data_ready  = pyqtSignal(object)   # pd.DataFrame
    agv_data_ready  = pyqtSignal(dict)
    aoi_data_ready  = pyqtSignal(int, int)
    task_error      = pyqtSignal(str, str)  # (task, message) – NEW signal for errors

    def __init__(self):
        super().__init__()
        self.task       = ""
        self.file_paths = []

    def run(self):
        if self.task == "OEE":
            self._process_oee()
        elif self.task == "LOGS":
            self._process_logs()
        elif self.task == "AOI":
            self._process_aoi()

    # ------------------------------------------------------------------
    # OEE processing – reads .csv / .xls / .xlsx, concats, normalises
    # ------------------------------------------------------------------
    def _process_oee(self):
        log("INFO", "OEE", f"Starting OEE processing – {len(self.file_paths)} file(s) selected")
        t0      = time.time()
        df_list = []
        for path in self.file_paths:
            fname = os.path.basename(path)
            try:
                ext = os.path.splitext(path)[1].lower()
                log("INFO", "OEE", f"Reading file: {fname}  (format: {ext})")

                if ext == '.csv':
                    df = pd.read_csv(path)
                    log("OK", "OEE", f"CSV loaded – {len(df)} rows")

                elif ext == '.xls':
                    # Some systems export HTML disguised as .xls.
                    # xlrd prints the sector-size warning directly to stderr
                    # (not via warnings module), so we redirect stderr.
                    try:
                        _old_stderr = sys.stderr
                        sys.stderr   = io.StringIO()   # swallow xlrd chatter
                        try:
                            df = pd.read_excel(path, engine='xlrd')
                            log("OK", "OEE", f"XLS loaded via xlrd – {len(df)} rows")
                        finally:
                            sys.stderr = _old_stderr   # always restore
                    except Exception:
                        log("WARN", "OEE", f"xlrd failed for '{fname}', trying HTML table fallback…")
                        try:
                            tables = pd.read_html(path)
                            df = tables[0] if tables else pd.DataFrame()
                            log("OK", "OEE", f"HTML fallback succeeded – {len(df)} rows")
                        except Exception as html_err:
                            log("ERROR", "OEE", f"Cannot read '{fname}': {html_err}")
                            continue

                else:  # .xlsx and others
                    df = pd.read_excel(path, engine='openpyxl')
                    log("OK", "OEE", f"XLSX loaded via openpyxl – {len(df)} rows")

                if not df.empty:
                    df_list.append(df)
                else:
                    log("WARN", "OEE", f"'{fname}' is empty – skipped")

            except Exception as e:
                log("ERROR", "OEE", f"Error reading '{fname}': {e}")

        if not df_list:
            log("ERROR", "OEE", "No valid data could be read from any selected file")
            self.task_error.emit("OEE", "No valid data could be read from the selected files.")
            return

        try:
            log("INFO", "OEE", f"Merging {len(df_list)} dataframe(s)…")
            df = pd.concat(df_list, ignore_index=True)
            log("INFO", "OEE", f"Total rows after merge: {len(df)}  |  Columns: {list(df.columns[:8])}")

            df.columns = [str(c).strip() for c in df.columns]

            # Normalise key columns
            for col in ['樓層', '綫', '日']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    log("INFO", "OEE", f"Normalised column '{col}' – unique values: {sorted(df[col].dropna().unique()[:10].tolist())}")

            # Robust OEE numeric conversion: strip %, spaces, then coerce
            if 'OEE' in df.columns:
                df['OEE_Num'] = (
                    df['OEE']
                    .astype(str)
                    .str.replace(r'[%\s]', '', regex=True)
                    .pipe(pd.to_numeric, errors='coerce')
                )
                valid = df['OEE_Num'].notna().sum()
                log("OK", "OEE", f"OEE numeric conversion done – {valid}/{len(df)} valid rows")
            else:
                log("WARN", "OEE", "Column 'OEE' not found – OEE charts will be empty")

            log("OK", "OEE", f"Processing complete in {time.time() - t0:.2f}s – emitting data to UI")
            self.oee_data_ready.emit(df)
        except Exception as e:
            log("ERROR", "OEE", f"Failed during merge/normalise: {e}")
            self.task_error.emit("OEE", str(e))

    # ------------------------------------------------------------------
    # AGV log processing – line-by-line, pure streaming, no DataFrame
    # ------------------------------------------------------------------
    def _process_logs(self):
        log("INFO", "AGV", f"Starting AGV log processing – {len(self.file_paths)} file(s) selected")
        try:
            start_t        = time.time()
            station_counts = defaultdict(int)
            action_counts  = defaultdict(int)
            timeline_counts= defaultdict(int)
            total_tasks    = 0

            for path in self.file_paths:
                fname      = os.path.basename(path)
                file_tasks = 0
                log("INFO", "AGV", f"Scanning: {fname}")
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if '"points":' not in line:
                            continue
                        t_match = TIME_PATTERN.search(line)
                        if not t_match:
                            continue
                        hour_key = f"{t_match.group(2)}:00"
                        for p_id, act in POINT_PATTERN.findall(line):
                            name = POINT_MAP.get(p_id, f"Unknown({p_id})")
                            total_tasks                  += 1
                            file_tasks                   += 1
                            station_counts[name]         += 1
                            action_counts[act.upper()]   += 1
                            timeline_counts[hour_key]    += 1
                log("OK", "AGV", f"  → {fname}: {file_tasks} task records found")

            elapsed = time.time() - start_t
            top3    = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            log("OK", "AGV", f"Total tasks: {total_tasks}  |  Elapsed: {elapsed:.2f}s")
            log("INFO", "AGV", f"Top stations: {top3}")
            log("INFO", "AGV", f"Action breakdown: {dict(action_counts)}")
            log("INFO", "AGV", f"Hourly buckets: {len(timeline_counts)} hour(s) – emitting to UI")

            self.agv_data_ready.emit({
                "stations": dict(station_counts),
                "actions" : dict(action_counts),
                "timeline": dict(sorted(timeline_counts.items())),
                "total"   : total_tasks,
                "p_time"  : elapsed,
            })
        except Exception as e:
            log("ERROR", "AGV", f"Unexpected error: {e}")
            self.task_error.emit("LOGS", str(e))

    # ------------------------------------------------------------------
    # AOI folder scan – only count image files, max depth guard
    # ------------------------------------------------------------------
    def _process_aoi(self):
        log("INFO", "AOI", f"Starting AOI folder scan – {len(self.file_paths)} folder(s) selected")
        t0 = time.time()
        try:
            p_c = f_c = skipped = 0
            for folder in self.file_paths:
                log("INFO", "AOI", f"Walking folder: {folder}")
                folder_p = folder_f = 0
                for root, dirs, files in os.walk(folder):
                    # Compute depth relative to the chosen folder
                    rel_depth = root.replace(folder, '').count(os.sep)
                    if rel_depth > 5:          # safety cap – don't recurse endlessly
                        log("WARN", "AOI", f"Depth limit reached at: {root}  – skipping subtree")
                        dirs.clear()
                        continue

                    img_files = [f for f in files
                                 if os.path.splitext(f)[1].lower() in IMAGE_EXTS]
                    non_img   = len(files) - len(img_files)
                    if non_img:
                        log("INFO", "AOI", f"  {os.path.relpath(root, folder) or '.'}: "
                                           f"{len(img_files)} image(s), {non_img} non-image file(s) skipped")

                    for file in img_files:
                        name_lower = file.lower()
                        if "all pass" in name_lower:
                            p_c      += 1
                            folder_p += 1
                        elif "fail" in name_lower:
                            f_c      += 1
                            folder_f += 1
                        else:
                            skipped  += 1   # image but keyword not matched

                total_folder = folder_p + folder_f
                rate_folder  = (folder_p / total_folder * 100) if total_folder else 0
                log("OK", "AOI",
                    f"Folder summary → Pass: {folder_p} | Fail: {folder_f} | "
                    f"Pass rate: {rate_folder:.1f}% | Unclassified images: {skipped}")

            elapsed = time.time() - t0
            total   = p_c + f_c
            rate    = (p_c / total * 100) if total else 0
            log("OK",   "AOI", f"Grand total → Pass: {p_c} | Fail: {f_c} | Pass rate: {rate:.1f}%")
            log("INFO", "AOI", f"Scan complete in {elapsed:.2f}s – emitting to UI")
            self.aoi_data_ready.emit(p_c, f_c)
        except Exception as e:
            log("ERROR", "AOI", f"Unexpected error: {e}")
            self.task_error.emit("AOI", str(e))


# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================

class SmartFactoryDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Factory Dashboard - Cyberpunk Edition")
        self.setGeometry(50, 50, 1366, 768)

        # Colour palette
        self.bg_dark    = "#0B0E14"
        self.panel_dark = "#151A25"
        self.text_light = "#E2E8F0"
        self.text_muted = "#94A3B8"
        self.accent_neon= "#00E5FF"
        self.accent_gold= "#FFEA00"
        self.bar_color  = "#2979FF"

        self.setStyleSheet(
            f"background-color: {self.bg_dark}; color: {self.text_light}; font-family: 'Segoe UI', Arial;")

        self.oee_df = None

        # One persistent worker – we guard against re-launching while running
        self.worker = DataWorker()
        self.worker.oee_data_ready.connect(self.handle_oee_ready)
        self.worker.agv_data_ready.connect(self.update_agv)
        self.worker.aoi_data_ready.connect(self.update_aoi)
        self.worker.task_error.connect(self._on_worker_error)   # NEW

        self.init_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout(central)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(20)

        # ── CONTROL PANEL ──────────────────────────────────────────────
        ctrl_panel = self.create_panel()
        l = QVBoxLayout(ctrl_panel)

        lbl_title = QLabel("⚙️ DATA CONTROL")
        lbl_title.setStyleSheet(
            f"color: {self.accent_neon}; font-size: 16px; font-weight: bold;")
        l.addWidget(lbl_title)

        self.btn_l = self.create_button("📜 Load AGV Logs",   "#0288D1", "#0277BD")
        self.btn_o = self.create_button("📊 Load OEE File",   "#7B1FA2", "#6A1B9A")
        self.btn_a = self.create_button("🖼️ Select AOI Folder","#F57C00", "#EF6C00")

        self.combo = QComboBox()
        self.combo.addItem("📅 Date Filter (All)")
        self.combo.setStyleSheet(f"""
            QComboBox {{ background-color: #1E293B; color: {self.text_light};
                         border: 1px solid #334155; padding: 8px; border-radius: 5px; font-weight: bold; }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self.combo.currentTextChanged.connect(self.filter_oee)

        self.btn_l.clicked.connect(lambda: self.start_task("LOGS"))
        self.btn_o.clicked.connect(lambda: self.start_task("OEE"))
        self.btn_a.clicked.connect(lambda: self.start_task("AOI"))

        for w in [self.btn_l, self.btn_o, self.combo, self.btn_a]:
            l.addWidget(w)
        l.addStretch()
        grid.addWidget(ctrl_panel, 0, 0)

        # ── KPI CARDS ──────────────────────────────────────────────────
        self.agv_kpi = self.create_kpi_card("🔄 TOTAL AGV TASKS", self.accent_neon)
        grid.addWidget(self.agv_kpi, 0, 1)
        self.aoi_kpi = self.create_kpi_card("🖼️ AOI PASS RATE",   "#00E676")
        grid.addWidget(self.aoi_kpi, 0, 2)

        # ── CHARTS (row 1) ─────────────────────────────────────────────
        self.f_st, self.ax_st, self.can_st = self.create_chart()
        grid.addWidget(self.can_st, 1, 0)
        self.f_ac, self.ax_ac, self.can_ac = self.create_chart()
        grid.addWidget(self.can_ac, 1, 1)
        self.f_tm, self.ax_tm, self.can_tm = self.create_chart()
        grid.addWidget(self.can_tm, 1, 2)

        # ── CHARTS (row 2) ─────────────────────────────────────────────
        self.f_f4, self.ax_f4, self.can_f4 = self.create_chart()
        grid.addWidget(self.can_f4, 2, 0)
        self.f_f5, self.ax_f5, self.can_f5 = self.create_chart()
        grid.addWidget(self.can_f5, 2, 1)
        self.f_pi, self.ax_pi, self.can_pi = self.create_chart()
        grid.addWidget(self.can_pi, 2, 2)

        for i in range(3):
            grid.setRowStretch(i, 1 if i == 0 else 2)

    # ------------------------------------------------------------------
    # Widget factory helpers
    # ------------------------------------------------------------------
    def create_panel(self):
        p = QFrame()
        p.setStyleSheet(
            f"background-color: {self.panel_dark}; border-radius: 10px; border: 1px solid #1E293B;")
        return p

    def create_button(self, t, c, h_c):
        b = QPushButton(t)
        b.setStyleSheet(f"""
            QPushButton {{ background-color: {c}; color: white; padding: 12px;
                           border-radius: 6px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {h_c}; }}
            QPushButton:disabled {{ background-color: #37474F; color: #78909C; }}
        """)
        b.setCursor(Qt.PointingHandCursor)
        return b

    def create_kpi_card(self, title, val_color):
        p = self.create_panel()
        l = QVBoxLayout(p)
        lbl_t = QLabel(f"<b>{title}</b>", alignment=Qt.AlignCenter)
        lbl_t.setStyleSheet(
            f"color: {self.text_muted}; font-size: 14px; letter-spacing: 1px;")
        lbl_v = QLabel("0", alignment=Qt.AlignCenter)
        lbl_v.setStyleSheet(
            f"font-size: 42px; color: {val_color}; font-weight: 900;")
        lbl_s = QLabel("Ready", alignment=Qt.AlignCenter)
        lbl_s.setStyleSheet(f"color: {self.text_muted}; font-style: italic;")
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        l.addWidget(lbl_s)
        p.val, p.sub = lbl_v, lbl_s
        return p

    def create_chart(self):
        f   = Figure()
        f.patch.set_facecolor(self.panel_dark)
        can = FigureCanvas(f)
        can.setStyleSheet(
            f"background-color: {self.panel_dark}; border-radius: 10px;")
        ax  = f.add_subplot(111)
        self._apply_base_style(ax)
        can.mpl_connect("motion_notify_event", self.on_hover)
        return f, ax, can

    def _apply_base_style(self, ax):
        ax.set_facecolor(self.panel_dark)
        ax.tick_params(colors=self.text_muted, labelsize=9)
        for s in ax.spines.values():
            s.set_edgecolor('#1E293B')
        # Tooltip annotation (hidden by default)
        an = ax.annotate(
            "", xy=(0, 0), xytext=(0, 20), textcoords="offset points",
            ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.6", fc="#0B0E14",
                      ec=self.accent_neon, lw=1.5, alpha=0.95),
            color="#FFFFFF", fontweight='bold')
        an.set_visible(False)
        ax.annot = an
        # Reset chart-type metadata
        ax.type    = None
        ax.labels  = []
        ax.values  = []
        ax.bars    = None
        ax.wedges  = None
        ax.line    = None

    # Convenience wrappers
    def _set_title(self, ax, title):
        ax.set_title(title, color=self.accent_neon,
                     fontweight='bold', fontsize=12, pad=15)

    def _format_x(self, ax, labels):
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha='right',
                           color=self.text_light, fontweight='500')

    # ------------------------------------------------------------------
    # Task dispatcher – guards against concurrent runs
    # ------------------------------------------------------------------
    def start_task(self, task):
        # Prevent launching a new task while the previous one is still running
        if self.worker.isRunning():
            QMessageBox.warning(self, "Busy",
                                "A data loading task is already in progress.\nPlease wait for it to finish.")
            return

        if task == "AOI":
            path  = QFileDialog.getExistingDirectory(self, "Select AOI Folder")
            paths = [path] if path else []
        else:
            filter_str = ("Log Files (*.log *.txt)"
                          if task == "LOGS"
                          else "Excel/CSV (*.xls *.xlsx *.csv)")
            paths, _ = QFileDialog.getOpenFileNames(
                self, f"Select {task} Files", "", filter_str)

        if not paths:
            return

        # Update UI to "loading" state
        if task == "LOGS":
            self.agv_kpi.val.setText("...")
            self.agv_kpi.sub.setText("Extracting Data…")
        elif task == "AOI":
            self.aoi_kpi.val.setText("...")
            self.aoi_kpi.sub.setText("Scanning Folder…")

        # Disable buttons while running
        for btn in [self.btn_l, self.btn_o, self.btn_a]:
            btn.setEnabled(False)
        self.worker.finished.connect(self._on_worker_done)

        self.worker.task       = task
        self.worker.file_paths = paths
        self.worker.start()

    def _on_worker_done(self):
        """Re-enable buttons once the worker thread finishes."""
        for btn in [self.btn_l, self.btn_o, self.btn_a]:
            btn.setEnabled(True)
        # Disconnect to avoid duplicate connections on next run
        try:
            self.worker.finished.disconnect(self._on_worker_done)
        except TypeError:
            pass

    def _on_worker_error(self, task: str, msg: str):
        """Surface worker errors to the user."""
        QMessageBox.critical(self, f"{task} Error", f"Failed to process {task} data:\n\n{msg}")
        # Reset loading indicator labels if needed
        if task == "LOGS":
            self.agv_kpi.val.setText("0")
            self.agv_kpi.sub.setText("Load failed")
        elif task == "AOI":
            self.aoi_kpi.val.setText("0")
            self.aoi_kpi.sub.setText("Load failed")

    # ------------------------------------------------------------------
    # OEE handlers
    # ------------------------------------------------------------------
    def handle_oee_ready(self, df):
        self.oee_df = df

        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItem("📅 Date Filter (All)")
        if '日' in df.columns:
            for d in sorted(df['日'].dropna().unique()):
                self.combo.addItem(str(d))
        self.combo.blockSignals(False)

        self.draw_oee(df)

    def filter_oee(self, txt):
        if self.oee_df is None:
            return
        if "All" in txt:
            self.draw_oee(self.oee_df)
        else:
            if '日' not in self.oee_df.columns:
                return
            subset = self.oee_df[self.oee_df['日'].astype(str) == txt]
            self.draw_oee(subset)

    def draw_oee(self, df):
        specs = [(self.ax_f4, self.f_f4, self.can_f4, 'F4', '#FF6D00'),
                 (self.ax_f5, self.f_f5, self.can_f5, 'F5', '#F9A825')]
        for ax, fig, can, floor, color in specs:
            ax.clear()
            self._apply_base_style(ax)
            if df is not None and not df.empty and 'OEE_Num' in df.columns and '樓層' in df.columns:
                sub = df[df['樓層'] == floor]
                if not sub.empty and '綫' in sub.columns:
                    avg    = sub.groupby('綫')['OEE_Num'].mean().dropna()
                    labels = list(avg.index)
                    if labels:
                        ax.bars = ax.bar(labels, avg.values, color=color,
                                         edgecolor="#FFE082", linewidth=1)
                        self._set_title(ax, f"OEE Performance - Floor {floor}")
                        ax.set_ylim(0, 105)
                        self._format_x(ax, labels)
                        ax.labels = labels
                        ax.type   = 'bar'
            fig.tight_layout(pad=1.5)
            can.draw()

    # ------------------------------------------------------------------
    # AGV handler
    # ------------------------------------------------------------------
    def update_agv(self, d):
        self.agv_kpi.val.setText(str(d['total']))

        filt = {k: v for k, v in d['stations'].items() if k != "PATH"}
        if filt:
            hot = max(filt, key=filt.get)
            self.agv_kpi.sub.setText(f"🔥 Busiest: {hot} | ⚡ {d['p_time']:.2f}s")
        else:
            self.agv_kpi.sub.setText(f"⚡ {d['p_time']:.2f}s")

        # Bar chart – Top 10 stations
        self.ax_st.clear()
        self._apply_base_style(self.ax_st)
        if filt:
            top = dict(sorted(filt.items(), key=lambda x: x[1], reverse=True)[:10])
            self.ax_st.bars  = self.ax_st.bar(
                list(top.keys()), list(top.values()),
                color=self.bar_color, edgecolor="#60A5FA", linewidth=1)
            self._set_title(self.ax_st, "Top Active Stations (AGV)")
            self._format_x(self.ax_st, list(top.keys()))
            self.ax_st.labels = list(top.keys())
            self.ax_st.type   = 'bar'
        self.f_st.tight_layout(pad=1.5)
        self.can_st.draw()

        # Pie chart – Action ratio
        self.ax_ac.clear()
        self._apply_base_style(self.ax_ac)
        act_vals = list(d['actions'].values())
        act_keys = list(d['actions'].keys())
        if act_vals and sum(act_vals) > 0:
            wedges, _, _ = self.ax_ac.pie(
                act_vals, labels=act_keys, autopct='%1.1f%%',
                colors=['#00E676', '#FF3D00'],
                textprops={'color': self.text_light, 'weight': 'bold'},
                wedgeprops={'edgecolor': self.panel_dark, 'linewidth': 2})
            self._set_title(self.ax_ac, "Action Ratio (UP/DOWN)")
            self.ax_ac.wedges = wedges
            self.ax_ac.labels = act_keys
            self.ax_ac.values = act_vals
            self.ax_ac.type   = 'pie'
        self.f_ac.tight_layout(pad=1.5)
        self.can_ac.draw()

        # Line chart – Hourly traffic
        self.ax_tm.clear()
        self._apply_base_style(self.ax_tm)
        if d['timeline']:
            h = list(d['timeline'].keys())
            c = list(d['timeline'].values())
            self.ax_tm.line = self.ax_tm.plot(
                h, c, marker='o', markersize=6,
                color="#D500F9", linewidth=2.5, picker=5)[0]
            self.ax_tm.fill_between(h, c, color="#D500F9", alpha=0.15)
            self._set_title(self.ax_tm, "Hourly Traffic Flow")
            self._format_x(self.ax_tm, h)
            self.ax_tm.labels = h
            self.ax_tm.values = c
            self.ax_tm.type   = 'line'
        self.f_tm.tight_layout(pad=1.5)
        self.can_tm.draw()

    # ------------------------------------------------------------------
    # AOI handler
    # ------------------------------------------------------------------
    def update_aoi(self, p, f):
        total = p + f
        rate  = (p / total * 100) if total > 0 else 0
        color = '#00E676' if rate >= 90 else '#FF3D00'
        self.aoi_kpi.val.setText(f"{rate:.1f}%")
        self.aoi_kpi.val.setStyleSheet(
            f"font-size: 42px; font-weight: 900; color: {color};")
        self.aoi_kpi.sub.setText(f"Pass: {p} | Fail: {f}")

        self.ax_pi.clear()
        self._apply_base_style(self.ax_pi)
        if total > 0:
            wedges, _, _ = self.ax_pi.pie(
                [p, f], labels=['PASS', 'FAIL'], autopct='%1.1f%%',
                colors=['#00E676', '#FF3D00'],
                textprops={'color': self.text_light, 'weight': 'bold'},
                wedgeprops={'edgecolor': self.panel_dark, 'linewidth': 2})
            self._set_title(self.ax_pi, "AOI Quality Details")
            self.ax_pi.wedges = wedges
            self.ax_pi.labels = ['PASS', 'FAIL']
            self.ax_pi.values = [p, f]
            self.ax_pi.type   = 'pie'
        self.f_pi.tight_layout(pad=1.5)
        self.can_pi.draw()

    # ------------------------------------------------------------------
    # Hover tooltip
    # ------------------------------------------------------------------
    def on_hover(self, event):
        ax = event.inaxes
        if ax is None or not hasattr(ax, 'annot'):
            return

        ann        = ax.annot
        chart_type = ax.type
        is_over    = False

        if chart_type == 'bar' and ax.bars is not None:
            for i, b in enumerate(ax.bars):
                if b.contains(event)[0]:
                    v     = b.get_height()
                    v_str = f"{int(v)}" if float(v).is_integer() else f"{float(v):.1f}"
                    ann.xy = (b.get_x() + b.get_width() / 2, v)
                    ann.set_text(f" {ax.labels[i]} \n Value: {v_str} ")
                    ann.set_visible(True)
                    is_over = True
                    break

        elif chart_type == 'pie' and ax.wedges:
            for i, w in enumerate(ax.wedges):
                if w.contains(event)[0]:
                    total = sum(ax.values)
                    pct   = (ax.values[i] / total * 100) if total > 0 else 0
                    theta = math.radians((w.theta1 + w.theta2) / 2.0)
                    r     = w.r * 0.6
                    ann.xy = (r * math.cos(theta) + w.center[0],
                              r * math.sin(theta) + w.center[1])
                    ann.set_text(f" {ax.labels[i]}: {ax.values[i]} \n ({pct:.1f}%) ")
                    ann.set_visible(True)
                    is_over = True
                    break

        elif chart_type == 'line' and ax.line is not None:
            cont, ind = ax.line.contains(event)
            if cont and len(ind.get("ind", [])) > 0:
                idx    = ind["ind"][0]
                ann.xy = (ax.line.get_xdata()[idx], ax.line.get_ydata()[idx])
                ann.set_text(f" {ax.labels[idx]} \n Flow: {ax.values[idx]} ")
                ann.set_visible(True)
                is_over = True

        if not is_over and ann.get_visible():
            ann.set_visible(False)

        event.canvas.draw_idle()


# ==========================================
# 4. ENTRY POINT
# ==========================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = SmartFactoryDashboard()
    w.showMaximized()
    sys.exit(app.exec_())
