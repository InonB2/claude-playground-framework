# telegram_listener_watchdog.ps1
# ============================================================================
# Heartbeat watchdog for Andy's Telegram listener.
#
# Runs every 2 minutes via Task Scheduler (AndyTelegramListenerWatchdog).
# Decides "is the listener alive?" by probing the singleton TCP port the
# listener binds to (127.0.0.1:50917). If nothing answers, launches the
# listener via pythonw.exe so it stays headless.
#
# Why probe a port instead of grepping process lists?
#   - Definition of "alive" matches the listener's own singleton guard:
#     if no one holds the port, no one is polling Telegram.
#   - Avoids false-positives from unrelated python.exe processes (whatsapp
#     bridge, scratch scripts, etc.) and false-negatives when the process
#     name changes.
#
# Idempotent: if the listener is already up, this script is a no-op.
# ============================================================================

$ErrorActionPreference = "Stop"

$Root        = "D:\Claude Playground"
$ScriptPath  = Join-Path $Root "scripts\telegram_listener.py"
$LogFile     = Join-Path $Root "scratchpad\telegram_listener_watchdog.log"
# IMPORTANT: must be the Python 3.11 store-app pythonw — that's where
# python-telegram-bot is installed. The bare WindowsApps\pythonw.exe symlink
# currently points at Python 3.14, which silently exits with ModuleNotFoundError.
$PythonW     = "C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe"
$Port        = 50917

function Write-Log([string]$msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Add-Content -Path $LogFile -Value "$ts $msg" -Encoding UTF8
}

function Test-ListenerAlive {
    # The listener binds IPv4 127.0.0.1:$Port and accepts+closes.
    # Force AF_INET so we don't accidentally hit the IPv6 loopback (which is
    # NOT bound, so dual-stack resolution would falsely report "down").
    $client = $null
    try {
        $client = New-Object System.Net.Sockets.TcpClient([System.Net.Sockets.AddressFamily]::InterNetwork)
        $ip     = [System.Net.IPAddress]::Loopback   # 127.0.0.1, IPv4
        $async  = $client.BeginConnect($ip, $Port, $null, $null)
        $ok     = $async.AsyncWaitHandle.WaitOne(1500, $false)
        if ($ok -and $client.Connected) {
            $client.EndConnect($async) | Out-Null
            return $true
        }
        return $false
    } catch {
        return $false
    } finally {
        if ($client) { $client.Close() }
    }
}

function Start-Listener {
    Write-Log "Listener not responding on port $Port. Starting via pythonw.exe."
    if (-not (Test-Path $PythonW)) {
        Write-Log "FATAL: pythonw.exe not found at $PythonW"
        return
    }
    if (-not (Test-Path $ScriptPath)) {
        Write-Log "FATAL: listener script not found at $ScriptPath"
        return
    }
    try {
        Start-Process -FilePath $PythonW `
                      -ArgumentList "`"$ScriptPath`"" `
                      -WorkingDirectory $Root `
                      -WindowStyle Hidden
        Write-Log "Listener launch issued."
    } catch {
        Write-Log "Launch failed: $_"
    }
}

# --- Main ---
if (Test-ListenerAlive) {
    # Quiet success — only log every 30 ticks to keep file small (~1h cadence).
    # Skip noise log entirely; alive case is the common path.
    exit 0
}

Write-Log "Heartbeat probe failed."
Start-Listener

# Confirm it came up within 20 seconds. If not, log loud.
$confirmed = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 2
    if (Test-ListenerAlive) {
        $confirmed = $true
        break
    }
}
if ($confirmed) {
    Write-Log "Listener confirmed up on port $Port."
} else {
    Write-Log "WARNING: Listener did not come up within 20s after launch."
}
