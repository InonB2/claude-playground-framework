# cc_server_watchdog.ps1
# ============================================================================
# Heartbeat watchdog for Andy's C&C Dashboard server (cc_server.js).
#
# Runs every 2 minutes via Task Scheduler (AndyCCServerWatchdog).
# Probes http://127.0.0.1:3000/health. If it fails, launches cc_server.js.
#
# Idempotent: if the server is already up, this script is a no-op.
# Mirrors the pattern of telegram_listener_watchdog.ps1.
# ============================================================================

$ErrorActionPreference = "SilentlyContinue"

$Root       = "D:\Claude Playground"
$Script     = Join-Path $Root "scripts\cc_server.js"
$LogFile    = Join-Path $Root "scratchpad\cc_server_watchdog.log"
$NodeExe    = "C:\Program Files\nodejs\node.exe"
$HealthUrl  = "http://127.0.0.1:3000/health"

function Write-Log([string]$msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $LogFile -Value "$ts $msg" -Encoding UTF8
}

function Test-ServerAlive {
    try {
        $r = Invoke-WebRequest -Uri $HealthUrl -TimeoutSec 5 -UseBasicParsing
        return ($r.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Start-CCServer {
    Write-Log "Health probe failed. Starting cc_server.js."
    if (-not (Test-Path $NodeExe)) {
        Write-Log "FATAL: node.exe not found at $NodeExe"
        return
    }
    if (-not (Test-Path $Script)) {
        Write-Log "FATAL: cc_server.js not found at $Script"
        return
    }
    try {
        Start-Process -FilePath $NodeExe `
                      -ArgumentList "`"$Script`"" `
                      -WorkingDirectory $Root `
                      -WindowStyle Hidden `
                      -RedirectStandardOutput (Join-Path $Root "scratchpad\cc_server.log") `
                      -RedirectStandardError  (Join-Path $Root "scratchpad\cc_server_err.log")
        Write-Log "cc_server.js launch issued."
    } catch {
        Write-Log "Launch failed: $_"
    }
}

# --- Main ---
if (Test-ServerAlive) {
    exit 0   # Healthy — silent exit
}

Write-Log "Heartbeat probe failed."
Start-CCServer

# Confirm it came up within 30 seconds
$confirmed = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 2
    if (Test-ServerAlive) {
        $confirmed = $true
        break
    }
}

if ($confirmed) {
    Write-Log "cc_server confirmed up at $HealthUrl."
} else {
    Write-Log "WARNING: cc_server did not come up within 30s after launch."
}
