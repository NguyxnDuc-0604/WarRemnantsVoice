@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Show Database Tables (PRD Part III)
echo ================================================================================
echo   🎖️ HE THONG BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH - KIEM TRA CO SO DU LIEU
echo ================================================================================
cd /d "%~dp0"

set "PY_CMD=python"
if exist "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" (
    set "PY_CMD=C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe"
)

"%PY_CMD%" show_database.py
echo.
pause
