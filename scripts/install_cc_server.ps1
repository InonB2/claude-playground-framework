# install_cc_server.ps1
# Idempotent installer for Andy C&C Dashboard server resilience.
# Does NOT require admin elevation.
#
# What it creates:
#   - Startup shortcut: AndyCCServer.lnk    (runs cc_server.js at logon)
#   - Startup shortcut: AndyCCServerWatchdog.lnk (runs watchdog at logon)
#   - Scheduled Task:   AndyCCServerWatchdog (repeats every 2 min via schtasks)
#
# USAGE: powershell -ExecutionPolicy Bypass -File scripts\install_cc_server.ps1

$ErrorActionPreference = "Stop"

$Root           = "D:\Claude Playground"
$ServerScript   = Join-Path $Root "scripts\cc_server.js"
$WatchdogScript = Join-Path $Root "scripts\cc_server_watchdog.ps1"
$LaunchVbs      = Join-Path $Root "scripts\cc_server_launch.vbs"
$WatchdogVbs    = Join-Path $Root "scripts\cc_watchdog_launch.vbs"
$NodeExe        = "C:\Program Files\nodejs\node.exe"
$HealthUrl      = "http://127.0.0.1:3000/health"
$StartupFolder  = [Environment]::GetFolderPath("Startup")

Write-Host ""
Write-Host "=== Andy C&C Server Installer ==="
Write-Host ""

# --- 0. Prerequisites --------------------------------------------------------
if (-not (Test-Path $NodeExe)) {
    Write-Host "[ERROR] node.exe not found at $NodeExe" -ForegroundColor Red; exit 1
}
if (-not (Test-Path $ServerScript)) {
    Write-Host "[ERROR] cc_server.js not found at $ServerScript" -ForegroundColor Red; exit 1
}
Write-Host "[OK] Prerequisites found."

# --- 1. Kill old process on port 3000 ----------------------------------------
Write-Host ""
Write-Host "[1/5] Clearing port 3000..."
try {
    $conns = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $conns) {
        $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Stopping PID $($proc.Id) ($($proc.Name))..."
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
    Write-Host "  Port 3000 cleared."
} catch {
    Write-Host "  (Nothing to clear on port 3000 - continuing.)"
}

# --- 2. Create Startup shortcuts (logon auto-start) --------------------------
Write-Host ""
Write-Host "[2/5] Creating Startup folder shortcuts..."

$shell = New-Object -ComObject WScript.Shell

# Server shortcut
$s1 = $shell.CreateShortcut((Join-Path $StartupFolder "AndyCCServer.lnk"))
$s1.TargetPath = "C:\Windows\System32\wscript.exe"
$s1.Arguments = '"' + $LaunchVbs + '"'
$s1.WorkingDirectory = $Root
$s1.Description = "Andy C&C Dashboard Server"
$s1.Save()
Write-Host "  Created: $StartupFolder\AndyCCServer.lnk"

# Watchdog shortcut
$s2 = $shell.CreateShortcut((Join-Path $StartupFolder "AndyCCServerWatchdog.lnk"))
$s2.TargetPath = "C:\Windows\System32\wscript.exe"
$s2.Arguments = '"' + $WatchdogVbs + '"'
$s2.WorkingDirectory = $Root
$s2.Description = "Andy C&C Watchdog"
$s2.Save()
Write-Host "  Created: $StartupFolder\AndyCCServerWatchdog.lnk"

# --- 3. Register repeating watchdog task via schtasks (no admin needed) ------
Write-Host ""
Write-Host "[3/5] Registering AndyCCServerWatchdog scheduled task (every 2 min)..."
$wdArg = 'wscript.exe "' + $WatchdogVbs + '"'
$r = & schtasks /Create /F /TN "AndyCCServerWatchdog" /TR $wdArg /SC MINUTE /MO 2 /RU "$env:USERNAME" 2>&1
Write-Host "  $r"

# --- 4. Start the server now --------------------------------------------------
Write-Host ""
Write-Host "[4/5] Starting cc_server.js now..."
$proc = Start-Process -FilePath $NodeExe `
    -ArgumentList ('"' + $ServerScript + '"') `
    -WorkingDirectory $Root `
    -WindowStyle Hidden `
    -PassThru
Write-Host "  Started PID $($proc.Id)"
Start-Sleep -Seconds 4

# --- 5. Verify /health --------------------------------------------------------
Write-Host ""
Write-Host "[5/5] Verifying /health endpoint..."
$ok = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $res = Invoke-WebRequest -Uri $HealthUrl -TimeoutSec 5 -UseBasicParsing
        if ($res.StatusCode -eq 200) {
            $ok = $true
            Write-Host "  /health OK: $($res.Content)" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
}
if (-not $ok) {
    Write-Host "  [WARN] /health did not respond. Check scratchpad\cc_server_err.log" -ForegroundColor Yellow
}

# --- Summary ------------------------------------------------------------------
Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard:   http://localhost:3000/"
Write-Host "Health:      http://localhost:3000/health"
Write-Host "Restart URL: http://localhost:3000/restart"
Write-Host ""
Write-Host "From phone/remote: http://[PC-IP]:3000/restart"
Write-Host "Find PC IP: run ipconfig, look for Wi-Fi IPv4 Address."
Write-Host ""
Write-Host "Watchdog log: $Root\scratchpad\cc_server_watchdog.log"
Write-Host ""
