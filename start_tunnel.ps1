# WarRemnantsVoice - Cloudflare Tunnel Runner with Auto-URL Extraction
$Host.UI.RawUI.WindowTitle = "[WarRemnantsVoice] - Cloudflare Tunnel (Active)"

Clear-Host
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "   🎖️  WARREMNANTSVOICE - CLOUDFLARE PUBLIC TUNNEL" -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "Dang ket noi may chu Cloudflare, vui long cho trong giay lat..." -ForegroundColor Gray
Write-Host ""

$cloudflaredPath = Join-Path $PSScriptRoot "cloudflared.exe"

if (-not (Test-Path $cloudflaredPath)) {
    Write-Host "[LOI] Khong tim thay cloudflared.exe trong thu muc du an!" -ForegroundColor Red
    pause
    exit
}

$logFile = Join-Path $PSScriptRoot "tunnel_output.log"
if (Test-Path $logFile) { Remove-Item $logFile -Force }

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $cloudflaredPath
$psi.Arguments = "tunnel --url http://localhost:5173"
$psi.RedirectStandardError = $true
$psi.RedirectStandardOutput = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$process = [System.Diagnostics.Process]::Start($psi)

$urlFound = $false
$tunnelUrl = ""

while (-not $process.HasExited) {
    $line = $process.StandardError.ReadLine()
    if ($null -ne $line) {
        Add-Content -Path $logFile -Value $line
        
        # CHU Y: Bat subdomain trycloudflare.com NHUNG PHAI KHAC 'api'
        if ($line -match "https://([a-zA-Z0-9\-]+)\.trycloudflare\.com" -and $matches[1] -ne "api") {
            $tunnelUrl = "https://$($matches[1]).trycloudflare.com"
            $urlFound = $true
            
            Clear-Host
            Write-Host "====================================================================" -ForegroundColor Green
            Write-Host "  🎉 DUONG LINK CONG KHAI CHO DIEN THOAI DA SAN SANG!" -ForegroundColor Green
            Write-Host "====================================================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "  👉 DUONG LINK DUNG CUA BAN LA: " -NoNewline -ForegroundColor White
            Write-Host " $tunnelUrl " -ForegroundColor Black -BackgroundColor Yellow
            Write-Host ""
            Write-Host "====================================================================" -ForegroundColor Green
            Write-Host "  [1] Link nay da duoc TU DONG COPY vao Clipboard (bo nho tam)." -ForegroundColor Cyan
            Write-Host "  [2] Mo trang http://localhost:5173/qr-stands va dan vao (Ctrl+V)." -ForegroundColor Cyan
            Write-Host "  [3] Cam dien thoai 4G/5G bat Camera / Zalo quet ma QR de nghe!" -ForegroundColor Cyan
            Write-Host "====================================================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "  * CUA SO NAY DANG DUY TRI KET NOI - KHONG DUOC TAT CUA SO NAY! *" -ForegroundColor Yellow
            Write-Host "  (Nhan Ctrl+C de dung khi ket thuc buoi demo)" -ForegroundColor Gray
            Write-Host "--------------------------------------------------------------------" -ForegroundColor DarkGray
            
            try {
                Set-Clipboard -Value $tunnelUrl
            } catch {}
        }
        
        if ($urlFound) {
            if ($line -match "Registered tunnel connection" -or $line -match "error" -or $line -match "fail") {
                Write-Host ">> $line" -ForegroundColor DarkGray
            }
        } else {
            # Hien thi tien trinh dang ket noi
            if ($line -match "INF" -and -not ($line -match "precheck")) {
                Write-Host ">> $line" -ForegroundColor DarkGray
            }
        }
    }
}
