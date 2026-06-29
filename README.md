# Local Server Launcher · 本地服務器啟動台

🌐 **English** | [繁體中文](README.zh-TW.md)

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
