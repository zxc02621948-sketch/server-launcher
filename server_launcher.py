# -*- coding: utf-8 -*-
"""
本地服務器啟動台 — 把專案資料夾匯入、一鍵啟動本地服務器,
每個專案一格、各自一塊黑底 console 看日誌。原生視窗,不開瀏覽器。

跑法:  pythonw server_launcher.py   （或直接點 啟動.bat）
"""
import sys
import os
import json
import re
import socket
import subprocess
import webbrowser

from PySide6.QtCore import Qt, QProcess, QProcessEnvironment
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

        self.run_btn = QPushButton("▶ 啟動")
        self.run_btn.clicked.connect(self.toggle_run)
        head.addWidget(self.run_btn)
        for txt, fn, tip in [("🌐", self.open_browser, "在瀏覽器開啟"),
                             ("✎", self.edit, "編輯"),
                             ("🗑", self.remove, "移除")]:
            b = QPushButton(txt); b.setObjectName("icon"); b.setToolTip(tip)
            b.clicked.connect(fn)
            head.addWidget(b)
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
        self.status_lbl = QLabel("已停止"); self.status_lbl.setObjectName("status")
        clr = QPushButton("🧹 清空"); clr.setObjectName("icon")
        clr.clicked.connect(lambda: self.console.clear())
        foot.addWidget(self.status_lbl, 1)
        foot.addWidget(clr)
        outer.addLayout(foot)

    # ---- 啟動 / 停止 ----
    def is_running(self):
        return self.proc.state() != QProcess.NotRunning

    def toggle_run(self):
        self.stop() if self.is_running() else self.start()

    def start(self):
        d = self.cfg["dir"]
        if not os.path.isdir(d):
            self.append(f"» 資料夾不存在:{d}\n")
            self._set_status("error")
            return
        cmd = (self.cfg["command"]
               .replace("{port}", str(self.cfg["port"]))
               .replace("{dir}", d))
        self._stopping = False
        self.detected_url = None
        self.append(f"» 啟動:{cmd}\n  工作目錄:{d}\n")
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
        self.append("» 停止中…\n")
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
                self.status_lbl.setText(f"執行中 · {self.detected_url}")

    def _on_finished(self, code, _status):
        if self._stopping:
            self.append("» 已停止\n"); self._set_status("stopped")
        elif code == 0:
            self.append("» 程序正常結束\n"); self._set_status("stopped")
        else:
            self.append(f"» 程序異常結束(code {code})\n"); self._set_status("error")
        self._stopping = False

    def _on_error(self, err):
        if err == QProcess.FailedToStart:
            self.append("» 啟動失敗:指令無法執行(檢查指令是否正確、python 在不在 PATH)\n")
            self._set_status("error")

    # ---- 狀態顯示 ----
    def _set_status(self, state):
        if state == "running":
            self.dot.setStyleSheet("color:#3ddc84;")
            self.status_lbl.setText(f"執行中 · http://localhost:{self.cfg['port']}")
            self.run_btn.setText("■ 停止")
            self.run_btn.setStyleSheet(RUN_BTN_RUNNING)
        else:
            self.dot.setStyleSheet("color:#ff5c5c;" if state == "error" else "color:#777;")
            self.status_lbl.setText("發生錯誤" if state == "error" else "已停止")
            self.run_btn.setText("▶ 啟動")
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
            if QMessageBox.question(self, "移除", f"「{self.cfg['name']}」還在執行,移除會先停掉它,確定?") \
                    != QMessageBox.Yes:
                return
            self.stop()
        self.dash.remove_card(self)


# ───────────────────────── 編輯對話框 ─────────────────────────
class EditDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.setWindowTitle("編輯專案")
        self.setMinimumWidth(480)
        form = QFormLayout(self)

        self.name = QLineEdit(cfg["name"])
        self.port = QLineEdit(str(cfg["port"]))
        self.command = QLineEdit(cfg["command"])

        dir_row = QHBoxLayout()
        self.dir = QLineEdit(cfg["dir"])
        browse = QPushButton("瀏覽…"); browse.clicked.connect(self._browse)
        dir_row.addWidget(self.dir, 1); dir_row.addWidget(browse)
        dir_wrap = QWidget(); dir_wrap.setLayout(dir_row)

        form.addRow("名稱", self.name)
        form.addRow("資料夾", dir_wrap)
        form.addRow("Port", self.port)
        form.addRow("啟動指令", self.command)
        tip = QLabel("指令裡可用 {port}、{dir} 代換。例:python -m http.server {port}")
        tip.setObjectName("hint")
        form.addRow("", tip)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "選擇專案資料夾", self.dir.text() or HERE)
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
        self.setWindowTitle("本地服務器啟動台")
        self.resize(1140, 800)

        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(16, 14, 16, 14)
        main.setSpacing(12)

        # 工具列
        bar = QHBoxLayout()
        title = QLabel("本地服務器啟動台"); title.setObjectName("title")
        bar.addWidget(title)
        bar.addStretch(1)
        add = QPushButton("＋ 匯入專案資料夾"); add.setObjectName("primary")
        add.clicked.connect(self.import_project)
        start_all = QPushButton("▶ 全部啟動"); start_all.clicked.connect(self.start_all)
        stop_all = QPushButton("■ 全部停止"); stop_all.clicked.connect(self.stop_all)
        support = QPushButton("☕ 支持作者")
        support.setToolTip("請我喝杯咖啡,支持工具持續開發")
        support.clicked.connect(lambda: webbrowser.open(KOFI_URL))
        for b in (support, start_all, stop_all, add):
            bar.addWidget(b)
        main.addLayout(bar)

        self.hint = QLabel("按「＋ 匯入專案資料夾」加入你的第一個專案。")
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
        self.load_config()

    # ---- 專案增刪 ----
    def import_project(self):
        d = QFileDialog.getExistingDirectory(self, "選擇專案資料夾", HERE)
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
                self, "關閉",
                f"還有 {len(running)} 個服務器在跑,關掉視窗會一起停掉。確定關閉?")
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
    win = Dashboard()
    win.show()
    # 開起來就跳到最前面(從 .vbs/背景啟動時,預設可能被壓在其它視窗下)
    win.setWindowState((win.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
    win.raise_()
    win.activateWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
