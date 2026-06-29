# -*- coding: utf-8 -*-
"""
本地服務器啟動台 / Local Server Launcher
把專案資料夾匯入、一鍵啟動本地服務器,每個專案一格、各自一塊黑底 console 看日誌。
Import project folders, start local dev servers with one click, each in its own card with a live log.

跑法 / Run:  pythonw server_launcher.py   （或雙擊 啟動.vbs / or double-click 啟動.vbs）
"""
import sys
import os
import json
import re
import socket
import subprocess
import webbrowser

from PySide6.QtCore import Qt, QProcess, QProcessEnvironment, QSettings, QLocale
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QPlainTextEdit, QScrollArea, QFrame, QFileDialog,
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox, QSizePolicy,
)

# Windows：開子程序時不要彈出獨立的黑色 console 視窗（日誌走管線進格子裡）
CREATE_NO_WINDOW = 0x08000000
# 打包成 .exe(PyInstaller)時,__file__ 會指到暫存解壓目錄,
# 要改用 exe 自己的位置,projects.json 才會存在 exe 旁邊、下次還在。
if getattr(sys, "frozen", False):
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "projects.json")
KOFI_URL = "https://ko-fi.com/kuanming"
BASE_PORT = 8182          # 預設第一個 port,之後自動往上找空的
GRID_COLS = 2             # 一排幾格

# dev server 啟動時通常會在 console 印出真正的網址(Next 預設 3000、Vite 5173…),
# 跟我們設定的 port 不一定一樣。從 console 抓 localhost 網址,開瀏覽器才不會開錯。
LOCAL_URL_RE = re.compile(r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::(\d+))?", re.I)

# ───────────────────────── 多語系 / i18n ─────────────────────────
STRINGS = {
    "zh": {
        "app_title": "本地服務器啟動台",
        "support": "☕ 支持作者",
        "support_tip": "請我喝杯咖啡,支持工具持續開發",
        "lang_switch": "EN",
        "start_all": "▶ 全部啟動",
        "stop_all": "■ 全部停止",
        "import": "＋ 匯入專案資料夾",
        "hint_empty": "按「＋ 匯入專案資料夾」加入你的第一個專案。",
        "btn_start": "▶ 啟動",
        "btn_stop": "■ 停止",
        "tip_open": "在瀏覽器開啟",
        "tip_edit": "編輯",
        "tip_remove": "移除",
        "clear": "🧹 清空",
        "st_stopped": "已停止",
        "st_error": "發生錯誤",
        "st_running": "執行中 · {url}",
        "log_start": "» 啟動:{cmd}\n  工作目錄:{d}\n",
        "log_no_dir": "» 資料夾不存在:{d}\n",
        "log_stopping": "» 停止中…\n",
        "log_stopped": "» 已停止\n",
        "log_done_ok": "» 程序正常結束\n",
        "log_done_err": "» 程序異常結束(code {code})\n",
        "log_fail": "» 啟動失敗:指令無法執行(檢查指令是否正確、python 在不在 PATH)\n",
        "dlg_edit": "編輯專案",
        "f_name": "名稱",
        "f_dir": "資料夾",
        "f_port": "Port",
        "f_command": "啟動指令",
        "browse": "瀏覽…",
        "dlg_tip": "指令裡可用 {port}、{dir} 代換。例:python -m http.server {port}",
        "choose_dir": "選擇專案資料夾",
        "rm_title": "移除",
        "rm_confirm": "「{name}」還在執行,移除會先停掉它,確定?",
        "close_title": "關閉",
        "close_confirm": "還有 {n} 個服務器在跑,關掉視窗會一起停掉。確定關閉?",
    },
    "en": {
        "app_title": "Local Server Launcher",
        "support": "☕ Support",
        "support_tip": "Buy me a coffee to support development",
        "lang_switch": "中文",
        "start_all": "▶ Start All",
        "stop_all": "■ Stop All",
        "import": "＋ Import Project Folder",
        "hint_empty": "Click “＋ Import Project Folder” to add your first project.",
        "btn_start": "▶ Start",
        "btn_stop": "■ Stop",
        "tip_open": "Open in browser",
        "tip_edit": "Edit",
        "tip_remove": "Remove",
        "clear": "🧹 Clear",
        "st_stopped": "Stopped",
        "st_error": "Error",
        "st_running": "Running · {url}",
        "log_start": "» Start: {cmd}\n  Working dir: {d}\n",
        "log_no_dir": "» Folder not found: {d}\n",
        "log_stopping": "» Stopping…\n",
        "log_stopped": "» Stopped\n",
        "log_done_ok": "» Process exited normally\n",
        "log_done_err": "» Process exited abnormally (code {code})\n",
        "log_fail": "» Failed to start: command could not run (check the command, and that python is on PATH)\n",
        "dlg_edit": "Edit Project",
        "f_name": "Name",
        "f_dir": "Folder",
        "f_port": "Port",
        "f_command": "Command",
        "browse": "Browse…",
        "dlg_tip": "You can use {port} and {dir} in the command. e.g. python -m http.server {port}",
        "choose_dir": "Choose project folder",
        "rm_title": "Remove",
        "rm_confirm": "“{name}” is still running; removing will stop it first. Continue?",
        "close_title": "Close",
        "close_confirm": "{n} server(s) still running; closing the window will stop them. Close anyway?",
    },
}
_LANG = "zh"


def t(key, **kw):
    s = STRINGS.get(_LANG, STRINGS["zh"]).get(key) or STRINGS["zh"].get(key, key)
    return s.format(**kw) if kw else s


def set_lang(code):
    global _LANG
    _LANG = code if code in STRINGS else "zh"


def detect_lang():
    """先看有沒有存過偏好,沒有就依系統語言自動選。"""
    saved = QSettings("KuanmingTools", "ServerLauncher").value("lang")
    if saved in ("zh", "en"):
        return saved
    return "zh" if QLocale.system().name().startswith("zh") else "en"

# ───────────────────────── 外觀(深色主題) ─────────────────────────
QSS = """
QMainWindow, QWidget#root { background:#1b1b22; }
QLabel { color:#e6e6ea; }
QLabel#title { font-size:18px; font-weight:700; }
QLabel#hint { color:#8a8a96; font-size:12px; }
QLabel#name { font-size:14px; font-weight:700; }
QLabel#path { color:#8a8a96; font-size:11px; }
QLabel#status { color:#9a9aa6; font-size:11px; }
QLabel#dot { font-size:15px; }

QFrame#card {
    background:#26262e; border:1px solid #34343e; border-radius:12px;
}
QPlainTextEdit#console {
    background:#0c0c0e; color:#cfcfd2; border:1px solid #333; border-radius:8px;
    selection-background-color:#3a3a50;
}
QScrollArea { border:none; }

QPushButton {
    background:#3a3a46; color:#e6e6ea; border:none; border-radius:8px;
    padding:6px 12px; font-size:13px;
}
QPushButton:hover { background:#45454f; }
QPushButton:pressed { background:#2f2f38; }
QPushButton#icon { padding:6px 9px; background:transparent; font-size:14px; }
QPushButton#icon:hover { background:#3a3a46; }
QPushButton#primary { background:#4f8cff; font-weight:600; }
QPushButton#primary:hover { background:#5f97ff; }

QLineEdit {
    background:#1b1b22; color:#e6e6ea; border:1px solid #3a3a46;
    border-radius:6px; padding:6px;
}
QDialog { background:#26262e; }
"""

RUN_BTN_RUNNING = "background:#e0533a;"   # ■ 停止(紅)
RUN_BTN_STOPPED = "background:#33a35a;"   # ▶ 啟動(綠)


def port_is_free(port):
    """實際試綁一下,被別的程式占用就回 False。
    用 0.0.0.0(跟 http.server 預設一致),Windows 上才驗得準;
    不設 SO_REUSEADDR——Windows 設了會讓「已占用」也回報成功。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return True
        except OSError:
            return False


def detect_command(folder):
    """匯入當下瞄一眼資料夾,猜一個合理的啟動指令(之後仍可按 ✎ 改)。"""
    try:
        names = set(os.listdir(folder))
    except Exception:
        return "python -u -m http.server {port}"

    if "package.json" in names:                       # Node / 前端框架
        scripts = {}
        try:
            with open(os.path.join(folder, "package.json"), encoding="utf-8") as f:
                scripts = (json.load(f) or {}).get("scripts", {}) or {}
        except Exception:
            pass
        if "dev" in scripts:
            return "npm run dev"
        if "start" in scripts:
            return "npm start"
        return "npm run dev"
    if "manage.py" in names:                           # Django
        return "python manage.py runserver {port}"
    if "app.py" in names:                              # Flask / 一般 python
        return "python app.py"
    if "main.py" in names:
        return "python main.py"
    return "python -u -m http.server {port}"           # 靜態檔(純前端)


# ───────────────────────── 一個專案 = 一張卡 ─────────────────────────
class ProjectCard(QFrame):
    def __init__(self, cfg, dashboard):
        super().__init__()
        self.cfg = cfg                  # {name, dir, command, port}
        self.dash = dashboard
        self._stopping = False          # 區分「使用者按停止」vs「程序自己掛掉」
        self.detected_url = None        # dev server 實際印出的網址(開瀏覽器用)
        self._state = "stopped"         # 記住目前狀態,切換語言時可重新套字串
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 一張卡一個 QProcess(可重複啟停)
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)   # stdout+stderr 都進同一塊
        self.proc.readyReadStandardOutput.connect(self._on_output)
        self.proc.finished.connect(self._on_finished)
        self.proc.errorOccurred.connect(self._on_error)
        # 讓 python 子程序輸出即時流進來:stdout 接管線預設整塊緩衝,
        # 不設這個的話「Serving HTTP…」那種開頭訊息會卡住、體感像沒反應。
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        self.proc.setProcessEnvironment(env)
        if sys.platform == "win32":
            try:
                self.proc.setCreateProcessArgumentsModifier(
                    lambda a: setattr(a, "flags", a.flags | CREATE_NO_WINDOW)
                )
            except Exception:
                pass

        self._build_ui()
        self._set_status("stopped")

    # ---- 介面 ----
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(8)

        # 第一排:燈 + 名稱 ......... ▶  🌐  ✎  🗑
        head = QHBoxLayout()
        head.setSpacing(8)
        self.dot = QLabel("●"); self.dot.setObjectName("dot")
        self.name_lbl = QLabel(self.cfg["name"]); self.name_lbl.setObjectName("name")
        head.addWidget(self.dot)
        head.addWidget(self.name_lbl)
        head.addStretch(1)

        self.run_btn = QPushButton(t("btn_start"))
        self.run_btn.clicked.connect(self.toggle_run)
        head.addWidget(self.run_btn)
        self.icon_btns = {}
        for key, txt, fn in [("tip_open", "🌐", self.open_browser),
                             ("tip_edit", "✎", self.edit),
                             ("tip_remove", "🗑", self.remove)]:
            b = QPushButton(txt); b.setObjectName("icon"); b.setToolTip(t(key))
            b.clicked.connect(fn)
            head.addWidget(b)
            self.icon_btns[key] = b
        outer.addLayout(head)

        # 第二排:路徑 ......... :port
        sub = QHBoxLayout()
        self.path_lbl = QLabel(self.cfg["dir"]); self.path_lbl.setObjectName("path")
        self.path_lbl.setToolTip(self.cfg["dir"])
        self.port_lbl = QLabel(f":{self.cfg['port']}"); self.port_lbl.setObjectName("path")
        sub.addWidget(self.path_lbl, 1)
        sub.addWidget(self.port_lbl)
        outer.addLayout(sub)

        # 黑底 console
        self.console = QPlainTextEdit(); self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(5000)     # 日誌封頂,免吃記憶體
        self.console.setFont(QFont("Consolas", 10))
        self.console.setMinimumHeight(150)
        outer.addWidget(self.console, 1)

        # 底排:狀態文字 ......... 清空
        foot = QHBoxLayout()
        self.status_lbl = QLabel(t("st_stopped")); self.status_lbl.setObjectName("status")
        self.clr_btn = QPushButton(t("clear")); self.clr_btn.setObjectName("icon")
        self.clr_btn.clicked.connect(lambda: self.console.clear())
        foot.addWidget(self.status_lbl, 1)
        foot.addWidget(self.clr_btn)
        outer.addLayout(foot)

    def retranslate(self):
        """切換語言時重新套用這張卡上的所有固定字串。"""
        for key, b in self.icon_btns.items():
            b.setToolTip(t(key))
        self.clr_btn.setText(t("clear"))
        self._set_status(self._state)   # 同時更新狀態文字 + 啟動/停止鈕

    # ---- 啟動 / 停止 ----
    def is_running(self):
        return self.proc.state() != QProcess.NotRunning

    def toggle_run(self):
        self.stop() if self.is_running() else self.start()

    def start(self):
        d = self.cfg["dir"]
        if not os.path.isdir(d):
            self.append(t("log_no_dir", d=d))
            self._set_status("error")
            return
        cmd = (self.cfg["command"]
               .replace("{port}", str(self.cfg["port"]))
               .replace("{dir}", d))
        self._stopping = False
        self.detected_url = None
        self.append(t("log_start", cmd=cmd, d=d))
        self.proc.setWorkingDirectory(d)
        if sys.platform == "win32":
            self.proc.start("cmd", ["/c", cmd])     # 走 cmd /c → npm/flask/內建指令都能跑
        else:
            self.proc.start("sh", ["-c", cmd])
        self._set_status("running")

    def stop(self):
        if not self.is_running():
            self._set_status("stopped")
            return
        self._stopping = True
        self.append(t("log_stopping"))
        pid = int(self.proc.processId())
        if sys.platform == "win32" and pid:
            # /T 連子程序一起殺(npm 之類會 spawn 子程序)
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           creationflags=CREATE_NO_WINDOW, capture_output=True)
        else:
            self.proc.terminate()
        # 真正停掉會觸發 _on_finished

    # ---- QProcess 事件 ----
    def _on_output(self):
        data = bytes(self.proc.readAllStandardOutput()).decode("utf-8", "replace")
        if data:
            self.append(data)
            self._maybe_detect_url(data)

    def _maybe_detect_url(self, text):
        # dev server 第一次印出 localhost 網址時記下來,之後開瀏覽器就用這個真實網址
        if self.detected_url:
            return
        m = LOCAL_URL_RE.search(text)
        if m:
            port = m.group(1)
            self.detected_url = f"http://localhost:{port}" if port else "http://localhost"
            if self.is_running():
                self.status_lbl.setText(t("st_running", url=self.detected_url))

    def _on_finished(self, code, _status):
        if self._stopping:
            self.append(t("log_stopped")); self._set_status("stopped")
        elif code == 0:
            self.append(t("log_done_ok")); self._set_status("stopped")
        else:
            self.append(t("log_done_err", code=code)); self._set_status("error")
        self._stopping = False

    def _on_error(self, err):
        if err == QProcess.FailedToStart:
            self.append(t("log_fail"))
            self._set_status("error")

    # ---- 狀態顯示 ----
    def _set_status(self, state):
        self._state = state
        if state == "running":
            self.dot.setStyleSheet("color:#3ddc84;")
            url = self.detected_url or f"http://localhost:{self.cfg['port']}"
            self.status_lbl.setText(t("st_running", url=url))
            self.run_btn.setText(t("btn_stop"))
            self.run_btn.setStyleSheet(RUN_BTN_RUNNING)
        else:
            self.dot.setStyleSheet("color:#ff5c5c;" if state == "error" else "color:#777;")
            self.status_lbl.setText(t("st_error") if state == "error" else t("st_stopped"))
            self.run_btn.setText(t("btn_start"))
            self.run_btn.setStyleSheet(RUN_BTN_STOPPED)

    def append(self, text):
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(text)
        self.console.moveCursor(QTextCursor.End)

    # ---- 動作 ----
    def open_browser(self):
        # 優先用 dev server 自己印出來的真實網址;偵測不到才退回設定的 port
        url = self.detected_url or f"http://localhost:{self.cfg['port']}"
        webbrowser.open(url)

    def edit(self):
        dlg = EditDialog(self.cfg, self)
        if dlg.exec():
            self.cfg.update(dlg.values())
            self.name_lbl.setText(self.cfg["name"])
            self.path_lbl.setText(self.cfg["dir"])
            self.path_lbl.setToolTip(self.cfg["dir"])
            self.port_lbl.setText(f":{self.cfg['port']}")
            if not self.is_running():
                self._set_status("stopped")
            self.dash.save_config()

    def remove(self):
        if self.is_running():
            if QMessageBox.question(self, t("rm_title"), t("rm_confirm", name=self.cfg["name"])) \
                    != QMessageBox.Yes:
                return
            self.stop()
        self.dash.remove_card(self)


# ───────────────────────── 編輯對話框 ─────────────────────────
class EditDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("dlg_edit"))
        self.setMinimumWidth(480)
        form = QFormLayout(self)

        self.name = QLineEdit(cfg["name"])
        self.port = QLineEdit(str(cfg["port"]))
        self.command = QLineEdit(cfg["command"])

        dir_row = QHBoxLayout()
        self.dir = QLineEdit(cfg["dir"])
        browse = QPushButton(t("browse")); browse.clicked.connect(self._browse)
        dir_row.addWidget(self.dir, 1); dir_row.addWidget(browse)
        dir_wrap = QWidget(); dir_wrap.setLayout(dir_row)

        form.addRow(t("f_name"), self.name)
        form.addRow(t("f_dir"), dir_wrap)
        form.addRow(t("f_port"), self.port)
        form.addRow(t("f_command"), self.command)
        tip = QLabel(t("dlg_tip"))
        tip.setObjectName("hint")
        form.addRow("", tip)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, t("choose_dir"), self.dir.text() or HERE)
        if d:
            self.dir.setText(d)

    def values(self):
        try:
            port = int(self.port.text())
        except ValueError:
            port = BASE_PORT
        return {
            "name": self.name.text().strip() or os.path.basename(self.dir.text()),
            "dir": self.dir.text().strip(),
            "port": port,
            "command": self.command.text().strip() or "python -u -m http.server {port}",
        }


# ───────────────────────── 主視窗 ─────────────────────────
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.resize(1140, 800)

        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(16, 14, 16, 14)
        main.setSpacing(12)

        # 工具列
        bar = QHBoxLayout()
        self.title_lbl = QLabel(); self.title_lbl.setObjectName("title")
        bar.addWidget(self.title_lbl)
        bar.addStretch(1)
        self.add_btn = QPushButton(); self.add_btn.setObjectName("primary")
        self.add_btn.clicked.connect(self.import_project)
        self.start_all_btn = QPushButton(); self.start_all_btn.clicked.connect(self.start_all)
        self.stop_all_btn = QPushButton(); self.stop_all_btn.clicked.connect(self.stop_all)
        self.support_btn = QPushButton()
        self.support_btn.clicked.connect(lambda: webbrowser.open(KOFI_URL))
        self.lang_btn = QPushButton(); self.lang_btn.setObjectName("icon")
        self.lang_btn.clicked.connect(self.toggle_lang)
        for b in (self.support_btn, self.lang_btn, self.start_all_btn, self.stop_all_btn, self.add_btn):
            bar.addWidget(b)
        main.addLayout(bar)

        self.hint = QLabel()
        self.hint.setObjectName("hint")
        main.addWidget(self.hint)

        # 可捲動網格
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)
        for c in range(GRID_COLS):
            self.grid.setColumnStretch(c, 1)
        self.grid.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.grid_host)
        main.addWidget(self.scroll, 1)

        self.setStyleSheet(QSS)
        self.retranslate_ui()
        self.load_config()

    # ---- 語言 ----
    def toggle_lang(self):
        set_lang("en" if _LANG == "zh" else "zh")
        QSettings("KuanmingTools", "ServerLauncher").setValue("lang", _LANG)
        self.retranslate_ui()
        for c in self.cards:
            c.retranslate()

    def retranslate_ui(self):
        self.setWindowTitle(t("app_title"))
        self.title_lbl.setText(t("app_title"))
        self.add_btn.setText(t("import"))
        self.start_all_btn.setText(t("start_all"))
        self.stop_all_btn.setText(t("stop_all"))
        self.support_btn.setText(t("support"))
        self.support_btn.setToolTip(t("support_tip"))
        self.lang_btn.setText(t("lang_switch"))
        self.hint.setText(t("hint_empty"))

    # ---- 專案增刪 ----
    def import_project(self):
        d = QFileDialog.getExistingDirectory(self, t("choose_dir"), HERE)
        if not d:
            return
        cfg = {
            "name": os.path.basename(d) or d,
            "dir": d,
            "port": self.next_port(),
            "command": detect_command(d),
        }
        self.add_card(cfg)
        self.save_config()

    def add_card(self, cfg):
        card = ProjectCard(cfg, self)
        self.cards.append(card)
        self._relayout()

    def remove_card(self, card):
        self.cards.remove(card)
        card.setParent(None)
        card.deleteLater()
        self._relayout()
        self.save_config()

    def _relayout(self):
        while self.grid.count():
            self.grid.takeAt(0)
        for i, card in enumerate(self.cards):
            self.grid.addWidget(card, i // GRID_COLS, i % GRID_COLS)
        self.hint.setVisible(not self.cards)

    def next_port(self):
        used = {c.cfg["port"] for c in self.cards}
        p = BASE_PORT
        while p <= 65000 and (p in used or not port_is_free(p)):
            p += 1
        return p if p <= 65000 else BASE_PORT

    # ---- 全部啟停 ----
    def start_all(self):
        for c in self.cards:
            if not c.is_running():
                c.start()

    def stop_all(self):
        for c in self.cards:
            if c.is_running():
                c.stop()

    # ---- 存檔 / 讀檔 ----
    def save_config(self):
        try:
            with open(CONFIG, "w", encoding="utf-8") as f:
                json.dump([c.cfg for c in self.cards], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("save failed:", e)

    def load_config(self):
        try:
            with open(CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        except Exception as e:
            print("load failed:", e)
            return
        for cfg in data or []:
            # 逐筆容錯:某一筆壞掉/缺欄位就跳過該筆,不要連累其他專案載不出來
            try:
                d = (cfg.get("dir") or "").strip()
                if not d:
                    continue
                self.add_card({
                    "name": (cfg.get("name") or os.path.basename(d.rstrip("/\\")) or d),
                    "dir": d,
                    "port": int(cfg.get("port") or self.next_port()),
                    "command": (cfg.get("command") or detect_command(d)),
                })
            except Exception as e:
                print("skip bad entry:", cfg, e)

    def closeEvent(self, e):
        running = [c for c in self.cards if c.is_running()]
        if running:
            ans = QMessageBox.question(
                self, t("close_title"), t("close_confirm", n=len(running)))
            if ans != QMessageBox.Yes:
                e.ignore()
                return
            for c in running:
                c.stop()
        self.save_config()
        e.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    set_lang(detect_lang())          # 開啟時依系統語言/上次選擇決定介面語言
    win = Dashboard()
    win.show()
    # 開起來就跳到最前面(從 .vbs/背景啟動時,預設可能被壓在其它視窗下)
    win.setWindowState((win.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
    win.raise_()
    win.activateWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
