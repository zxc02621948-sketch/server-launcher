@echo off
rem ── 一鍵打包成單一 .exe（不需要使用者裝 Python）──
rem 跑完後，成品在 dist\server-launcher.exe，直接雙擊就能用。
chcp 65001 >nul
echo [1/2] 安裝打包需要的套件...
python -m pip install --upgrade pyinstaller PySide6
echo [2/2] 開始打包...
pyinstaller --noconfirm --windowed --onefile --name "server-launcher" server_launcher.py
echo.
echo 完成！成品在  dist\server-launcher.exe
pause
