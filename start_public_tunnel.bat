@echo off
chcp 65001 >nul
title [WarRemnantsVoice] - Public Tunnel (Chia se dien thoai ngoai mang)
echo ====================================================================
echo  📱 TAO DUONG LINK CONG KHAI CHO DIEN THOAI (KHONG CHUNG MANG)
echo ====================================================================
echo  1. Cho phep nhieu dien thoai dung 4G/5G/WiFi khac truy cap cung luc
echo  2. Tu dong co HTTPS (Bat buoc de dien thoai mo duoc Camera quet QR)
echo ====================================================================
echo.

where cloudflared >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [CLOUDFLARE TUNNEL] Phat hien cloudflared da cai dat!
    echo Dang tao link HTTPS Cloudflare den http://localhost:5173 ...
    echo.
    cloudflared tunnel --url http://localhost:5173
    goto :end
)

where ngrok >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [NGROK] Phat hien ngrok da cai dat!
    echo Dang tao link HTTPS ngrok den port 5173...
    echo.
    ngrok http 5173
    goto :end
)

echo [LOCALTUNNEL] Khong tim thay cloudflared/ngrok, su dung LocalTunnel (qua npx Node.js co san)...
echo.
echo * Luu y: Lan dau mo tren dien thoai, trang se yeu cau nhap password.
echo   Password chinh la IP Public cua may ban (lay tai https://loca.lt/mytunnelpassword)
echo.
echo Dang khoi tao tunnel den port 5173...
call npx localtunnel --port 5173

:end
pause
