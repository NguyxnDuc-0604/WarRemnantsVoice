@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Trinh Truy Van SQL truc tiep
cd /d "%~dp0"

set "PY_CMD=python"
if exist "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PY_CMD=C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe"
)

"%PY_CMD%" truy_van_sql.py
pause
