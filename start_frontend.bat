@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Frontend React Vite (Port 5173)
echo ==========================================================
echo  🌐 KHOI DONG FRONTEND REACT + VITE (PORT 5173)
echo ==========================================================
cd /d "%~dp0services\frontend"

if not exist "node_modules" (
    echo [INFO] Dang cai dat thu vien Frontend...
    npm install
)

echo.
echo [INFO] Dang chay Vite Dev Server tai http://localhost:5173
echo ==========================================================
npm run dev
pause
