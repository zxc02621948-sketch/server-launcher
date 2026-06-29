<a id="top"></a>

# Local Server Launcher · 本地服務器啟動台

🌐 **English** · [繁體中文 ↓](#繁體中文)

> Vibe-coding a bunch of small sites/apps with AI, but tired of opening a terminal, typing commands,
> remembering ports, and opening the browser by hand every time? This tiny GUI makes it one click:
> import a folder → ▶ Start → 🌐 Open. Native window, no config files.

![Local Server Launcher screenshot](demo/screenshot.png)

## ⬇️ Get it

**🤖 Recommended (for AI devs): hand the repo URL to your AI** (Claude Code / Cursor / Cline — any agent that can run commands) **and let it install for you** — no download, and **no security warnings at all**. See **Method A** below.

**💾 Or: download the Windows build (portable, no Python needed)**

[![Download for Windows](https://img.shields.io/badge/Download-Windows_.exe-2ea44f?style=for-the-badge&logo=windows)](https://github.com/zxc02621948-sketch/server-launcher/releases/latest/download/server-launcher.exe)

> On first launch, Windows SmartScreen may say "unrecognized publisher" → click **More info → Run anyway** (normal for an unsigned hobby app — it's not a virus; the project is open source and the code is public). Don't want the warning at all? Use the **AI install** method above.

## Who it's for
- People building sites / small apps with AI who **aren't comfortable with the terminal**
- Anyone juggling several projects who wants **one place to start/stop and watch logs**
- People who'd rather **click than memorize commands**

## Features
- 📁 Import any project folder — **auto-detects the start command** (Next / Vite / Django / Flask / static)
- ▶️ One card per project: independent **start / stop**, each with its own live console
- 🌐 One-click **open in browser** — **auto-grabs the real URL from the output**, so it never opens the wrong port
- 🧹 Clear logs, ✎ edit (name / folder / port / command), 🗑 remove
- ⏯️ **Start all / Stop all**
- 🪟 Native window (PySide6), dark theme
- 🌍 **Bilingual UI (English / 中文)** — auto-detects your system language, with a one-click toggle

## Install & Run

### 🤖 Method A (recommended for AI devs): let your AI install it
Using Claude Code / Cursor / Cline, or another agent that can run commands? Paste this and it'll install and launch it for you — **no download, no SmartScreen**:

```text
Install and run this tool for me: https://github.com/zxc02621948-sketch/server-launcher
It's a Python + PySide6 desktop GUI. Clone it, run `pip install -r requirements.txt`,
then start it with `pythonw server_launcher.py`. Requires Python 3.10+.
```

> The repo includes an `AGENTS.md`, so coding agents pick up the exact steps — usually "URL + that prompt" just works.

### 💾 Method B: download the .exe (portable, no Python)
👉 **[Download server-launcher.exe](https://github.com/zxc02621948-sketch/server-launcher/releases/latest/download/server-launcher.exe)** — double-click to run.
> First launch shows SmartScreen → More info → Run anyway (not a virus; source is public). The `Source code (zip/tar.gz)` on the releases page is for developers; regular users can ignore it.

### 🧑‍💻 Method C: run from Python yourself
```bash
pip install -r requirements.txt        # installs PySide6
pythonw server_launcher.py             # start (Windows: or double-click 啟動.vbs)
```
To see logs/errors, double-click `偵錯.bat`. To build your own .exe, double-click `build.bat` (output in `dist\server-launcher.exe`).

## Usage
1. **＋ Import Project Folder** → pick a folder; a port is assigned and the start command auto-detected
2. Per card: **▶ Start** / **🌐** open in browser / **■ Stop** (kills child processes too)
3. **✎** edit, **🗑** remove, **🧹** clear logs
4. **▶ Start All / ■ Stop All**

> Tip: npm / Next / Vite take a few seconds to boot — **wait until the console prints `http://localhost:xxxx` (shown in the status bar) before clicking 🌐.**

## Auto-detection rules
| If the folder has | Detected command |
|---|---|
| `package.json` | `npm run dev` (falls back to `npm start`) |
| `manage.py` | `python manage.py runserver {port}` (Django) |
| `app.py` | `python app.py` (Flask / generic Python) |
| `main.py` | `python main.py` |
| anything else | `python -u -m http.server {port}` (static) |

`{port}` and `{dir}` in the command are substituted per card; commands run via `cmd /c`, so anything you can type in a terminal works.

## Honest comparison
Strong free tools already exist — [mprocs](https://github.com/pvolok/mprocs) (terminal TUI) and [PM2](https://github.com/unitech/pm2) (Node process manager). **They're more powerful, but they're terminal/CLI tools with config files.** This one is positioned differently: **a click-to-use GUI for people who aren't into the terminal** — especially folks building with AI today. If you're comfortable on the CLI, mprocs / PM2 may suit you better.

## Requirements
- Windows (uses `taskkill` for stop and `pythonw` for no-console; other OSes run with minor tweaks)
- Python 3.10+ and PySide6 (not needed if you use the .exe)

## ☕ Support
This tool is free and open source. If it saves you some hassle, consider buying me a coffee:
👉 https://ko-fi.com/kuanming

## License
MIT — see [LICENSE](LICENSE).

---

## 繁體中文

🌐 [English ↑](#top) · **繁體中文**

> 用 AI 生了一堆小網站 / 小工具,但每次要打開來看,還得開終端機、打指令、記 port、再手動開瀏覽器?
> 這個小工具把它變成**點一下就好**:匯入資料夾 → 按 ▶ 啟動 → 按 🌐 開瀏覽器。原生視窗、中文介面、零設定檔。

### ⬇️ 取得方式

**🤖 最推薦(AI 開發者):把這個 repo 網址丟給你的 AI**(Claude Code / Cursor / Cline 等能執行指令的 AI)**叫它幫你裝** —— 連下載都免、**也不會跳任何安全警告**。詳見下方〈安裝與執行〉**方法 A**。

**💾 或:直接下載 Windows 版(免安裝、不需 Python)**

[![Download for Windows](https://img.shields.io/badge/Download-Windows_.exe-2ea44f?style=for-the-badge&logo=windows)](https://github.com/zxc02621948-sketch/server-launcher/releases/latest/download/server-launcher.exe)

> 第一次開啟會跳 SmartScreen「無法辨識的發行者」→ 點 **「其他資訊 → 仍要執行」** 即可(未簽章小工具的正常現象,不是病毒;本工具開源、程式碼公開可檢視)。不想看到警告?用上面的 **AI 安裝法**就沒有。

### 這是給誰用的
- 用 AI 寫網站 / 小 app,但**不熟終端機**的人
- 同時在弄好幾個專案,想要一個地方**一鍵啟停、各自看日誌**
- 偏好**圖形介面**勝過記指令的人

### 功能
- 📁 匯入任何專案資料夾,**自動偵測啟動指令**(Next / Vite / Django / Flask / 靜態檔…)
- ▶️ 每個專案一張卡,獨立 **啟動 / 停止**,各自一塊黑底 console 看即時日誌
- 🌐 一鍵**在瀏覽器開啟** —— 會**自動從輸出抓真實網址**,不會開錯 port
- 🧹 清日誌、✎ 編輯(名稱 / 資料夾 / port / 指令)、🗑 移除
- ⏯️ **全部啟動 / 全部停止**
- 🪟 原生視窗(PySide6)、深色主題、**中英雙語**(依系統語言自動切換,工具列也有「中 / EN」鈕可手動切)

### 安裝與執行

#### 🤖 方法 A(最推薦給 AI 開發者):叫你的 AI 幫你裝
你在用 Claude Code / Cursor / Cline 這類**能執行指令的 AI**?把下面這段複製給它,它就會幫你裝好並啟動 —— **不用下載 exe、不會跳 SmartScreen**:

```text
幫我安裝並執行這個工具:https://github.com/zxc02621948-sketch/server-launcher
它是 Python + PySide6 的桌面 GUI,請 clone 下來、執行 pip install -r requirements.txt,
再用 pythonw server_launcher.py 啟動。需要 Python 3.10+。
```

> 倉庫裡有 `AGENTS.md`,coding agent 會自動讀到安裝步驟,所以通常「丟網址 + 上面那句」就會成功。

#### 💾 方法 B:直接下載 .exe(免安裝、不用 Python)
👉 **[點此下載 server-launcher.exe](https://github.com/zxc02621948-sketch/server-launcher/releases/latest/download/server-launcher.exe)** —— 雙擊就能用。
> 第一次開會跳 SmartScreen → 點「其他資訊 → 仍要執行」(不是病毒,開源可檢視)。下載頁的 `Source code (zip/tar.gz)` 一般使用者不用理它。

#### 🧑‍💻 方法 C:自己用 Python 跑
```bash
pip install -r requirements.txt        # 安裝 PySide6
pythonw server_launcher.py             # 啟動(Windows 可改雙擊 啟動.vbs)
```
出問題想看錯誤訊息 → 雙擊 `偵錯.bat`。自己打包成 exe → 雙擊 `build.bat`(成品在 `dist\server-launcher.exe`)。

### 怎麼用
1. **＋ 匯入專案資料夾** → 選資料夾,自動配 port 並偵測啟動指令
2. 每格 **▶ 啟動** / **🌐** 開瀏覽器 / **■ 停止**(連子程序一起關)
3. **✎** 編輯、**🗑** 移除、**🧹** 清日誌
4. **▶ 全部啟動 / ■ 全部停止**

> 小提醒:npm / Next / Vite 啟動要幾秒,**等 console 印出 `http://localhost:xxxx`(狀態列顯示該網址)再按 🌐**。

### 自動偵測規則
| 資料夾裡有 | 偵測到的指令 |
|---|---|
| `package.json` | `npm run dev`(沒 dev 就 `npm start`) |
| `manage.py` | `python manage.py runserver {port}`(Django) |
| `app.py` | `python app.py`(Flask / 一般 python) |
| `main.py` | `python main.py` |
| 其餘 | `python -u -m http.server {port}`(靜態檔) |

指令裡的 `{port}`、`{dir}` 會代換成該格的 port 與資料夾;用 `cmd /c` 執行,終端打得出來的都能跑。

### 跟其他工具的差別
已經有很強的免費工具,如 [mprocs](https://github.com/pvolok/mprocs)(終端 TUI)、[PM2](https://github.com/unitech/pm2)(Node 程序管理)。
**它們更強大,但都是終端 / CLI / 要寫設定檔。** 這個工具的定位不同:**給不熟終端機的人一個點一點就好的圖形介面**。如果你習慣 CLI,mprocs / PM2 可能更適合你。

### 需求
- Windows(stop 用 `taskkill`、無黑窗用 `pythonw`;其他平台可跑但這兩塊需微調)
- Python 3.10+ 與 PySide6(用 .exe 則免)

### ☕ 支持作者
這個工具是免費且開源的。如果它幫你省了麻煩,歡迎請我喝杯咖啡:
👉 https://ko-fi.com/kuanming

### 授權
MIT — 詳見 [LICENSE](LICENSE)。
