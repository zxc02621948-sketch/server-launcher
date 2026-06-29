# AGENTS.md — 給 AI 助手的安裝指引 / Instructions for AI assistants

If a user asks you to install and run this tool, follow these steps.
如果使用者要你幫忙安裝並執行這個工具,照以下步驟做。

## What this is / 這是什麼
A Python + PySide6 **desktop GUI** that launches local dev servers (one card per project,
each with start/stop and a live log). Best on Windows (uses `taskkill` and `pythonw`);
other OSes run with minor tweaks.

## Install & run / 安裝與執行
1. Ensure **Python 3.10+** is available: `python --version`. If missing, install it first.
2. Clone the repo (skip if already inside it):
   ```
   git clone https://github.com/zxc02621948-sketch/server-launcher.git
   cd server-launcher
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start it:
   - Windows, no console window: `pythonw server_launcher.py` (or double-click `啟動.vbs`)
   - To watch logs / debug: `python server_launcher.py`

## Notes / 注意
- Everything lives in **`server_launcher.py`**. User config is saved to **`projects.json`** next to it.
- No build step is needed to run from source. `build.bat` is **only** for producing a standalone `.exe`.
- **Do not commit `projects.json`** — it holds the user's local project paths and is gitignored.
- The UI auto-detects system language (中文 / English) and has a 中/EN toggle in the toolbar.
