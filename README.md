# 本地服務器啟動台 · Local Server Launcher

> 用 AI 生了一堆小網站 / 小工具,但每次要打開來看,還得開終端機、打指令、記 port、再手動開瀏覽器?
> 這個小工具把它變成**點一下就好**:匯入資料夾 → 按 ▶ 啟動 → 按 🌐 開瀏覽器。原生視窗、中文介面、零設定檔。

> Vibe-coding a bunch of little sites/apps with AI but tired of opening a terminal, typing commands,
> remembering ports, and opening the browser by hand every time? This tiny GUI makes it one click:
> import a folder → ▶ Start → 🌐 Open. Native window, no config files.

<!-- 截圖放這:把主畫面截圖存成 demo/screenshot.png 取消下面註解 -->
<!-- ![screenshot](demo/screenshot.png) -->

## 這是給誰用的 / Who it's for
- 用 AI 寫網站 / 小 app,但**不熟終端機**的人
- 同時在弄好幾個專案,想要一個地方**一鍵啟停、各自看日誌**
- 偏好**圖形介面**勝過記指令的人

## 功能 / Features
- 📁 匯入任何專案資料夾,**自動偵測啟動指令**(Next / Vite / Django / Flask / 靜態檔…)
- ▶️ 每個專案一張卡,獨立 **啟動 / 停止**,各自一塊黑底 console 看即時日誌
- 🌐 一鍵**在瀏覽器開啟** —— 會**自動從輸出抓真實網址**,不會開錯 port
- 🧹 清日誌、✎ 編輯(名稱 / 資料夾 / port / 指令)、🗑 移除
- ⏯️ **全部啟動 / 全部停止**
- 🪟 原生視窗(PySide6)、深色主題、繁體中文

## 安裝與執行 / Install & Run

### A. 不懂程式的人 — 直接用 .exe
到 [Releases](../../releases) 下載 `server-launcher.exe`,**雙擊就能用**,不用裝 Python。
> 還沒有 Release 的話,請作者用下面的 `build.bat` 打包後上傳。

### B. 有 Python 的人
```bash
pip install -r requirements.txt        # 安裝 PySide6
pythonw server_launcher.py             # 啟動(Windows 可改雙擊 啟動.vbs)
```
出問題想看錯誤訊息 → 雙擊 `偵錯.bat`(會留 console)。

### 自己打包成 .exe
雙擊 `build.bat`(會自動裝 PyInstaller 並打包),成品在 `dist\server-launcher.exe`。

## 怎麼用 / Usage
1. **＋ 匯入專案資料夾** → 選資料夾,自動配 port 並偵測啟動指令
2. 每格 **▶ 啟動** / **🌐** 開瀏覽器 / **■ 停止**(連子程序一起關)
3. **✎** 編輯、**🗑** 移除、**🧹** 清日誌
4. **▶ 全部啟動 / ■ 全部停止**

> 小提醒:npm / Next / Vite 啟動要幾秒,**等 console 印出 `http://localhost:xxxx`(狀態列顯示該網址)再按 🌐**。

## 自動偵測規則
| 資料夾裡有 | 偵測到的指令 |
|---|---|
| `package.json` | `npm run dev`(沒 dev 就 `npm start`) |
| `manage.py` | `python manage.py runserver {port}`(Django) |
| `app.py` | `python app.py`(Flask / 一般 python) |
| `main.py` | `python main.py` |
| 其餘 | `python -u -m http.server {port}`(靜態檔) |

指令裡的 `{port}`、`{dir}` 會代換成該格的 port 與資料夾;用 `cmd /c` 執行,終端打得出來的都能跑。

## 跟其他工具的差別 / Honest comparison
已經有很強的免費工具,如 [mprocs](https://github.com/pvolok/mprocs)(終端 TUI)、[PM2](https://github.com/unitech/pm2)(Node 程序管理)。
**它們更強大,但都是終端 / CLI / 要寫設定檔。** 這個工具的定位不同:**給不熟終端機的人一個點一點就好的圖形介面**。如果你習慣 CLI,mprocs / PM2 可能更適合你。

## 需求 / Requirements
- Windows(stop 用 `taskkill`、無黑窗用 `pythonw`;其他平台可跑但這兩塊需微調)
- Python 3.10+ 與 PySide6(用 .exe 則免)

## ☕ 支持作者 / Support
這個工具是免費且開源的。如果它幫你省了麻煩,歡迎請我喝杯咖啡:
👉 https://ko-fi.com/kuanming

## 授權 / License
MIT — 詳見 [LICENSE](LICENSE)。
