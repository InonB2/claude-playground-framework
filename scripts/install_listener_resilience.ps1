# install_listener_resilience.ps1
# ============================================================================
# Idempotent installer for Telegram listener resilience.
#
# What it does:
#   1. Reconfigures the existing AndyTelegramListener scheduled task:
#        - allow start on battery
#        - do not stop on battery transition
#        - restart task if it fails (up to 99 retries, 1-min interval)
#        - run with highest privileges, hidden
#   2. Creates/refreshes AndyTelegramListenerWatchdog scheduled task:
#        - trigger: at logon AND every 2 minutes indefinitely
#        - runs telegram_listener_watchdog.ps1
#        - allow start on battery
#
# Safe to run repeatedly. No duplicate tasks. No duplicate processes (the
# listener has its own singleton port guard).
# ============================================================================

$ErrorActionPreference = "Stop"

$Root           = "D:\Claude Playground"
$ListenerScript = Join-Path $Root "scripts\telegram_listener.py"
$WatchdogScript = Join-Path $Root "scripts\telegram_listener_watchdog.ps1"
# Pin to Python 3.11 store-app pythonw — that's where python-telegram-bot lives.
# The bare WindowsApps\pythonw.exe symlink resolves to Python 3.14, which lacks
# the telegram module and would crash silently.
$PythonW        = "C:\Users\Inon Baasov\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\pythonw.exe"

$ListenerTaskName = "AndyTelegramListener"
$WatchdogTaskName = "AndyTelegramListenerWatchdog"

Write-Host "=== Installing listener resilience (idempotent) ==="

# --- 1. Reconfigure listener task power policy + restart-on-failure --------
Write-Host ""
Write-Host "[1/3] Reconfiguring $ListenerTaskName power & restart policy..."

$listenerTask = Get-ScheduledTask -TaskName $ListenerTaskName -ErrorAction SilentlyContinue
if (-not $listenerTask) {
    Write-Host "  Listener task missing — creating it."
    $action  = New-ScheduledTaskAction `
        -Execute $PythonW `
        -Argument "`"$ListenerScript`"" `
        -WorkingDirectory $Root
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERNAME"
    Register-ScheduledTask -TaskName $ListenerTaskName -Action $action -Trigger $trigger -Force | Out-Null
    $listenerTask = Get-ScheduledTask -TaskName $ListenerTaskName
}

# Settings: allow battery, don't stop on battery, restart on failure
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 99 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew

Set-ScheduledTask -TaskName $ListenerTaskName -Settings $settings | Out-Null
Write-Host "  Listener task settings updated."

# --- 2. Create/refresh watchdog task (every 2 minutes) ---------------------
Write-Host ""
Write-Host "[2/3] Creating/refreshing $WatchdogTaskName (every 2 min)..."

$wdAction  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$WatchdogScript`""

# Two triggers: at logon, and a repeating 2-minute trigger.
$wdTrigger1 = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERNAME"
$wdTrigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
                -RepetitionInterval (New-TimeSpan -Minutes 2)

$wdSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# Register-ScheduledTask with -Force replaces an existing definition cleanly.
Register-ScheduledTask -TaskName $WatchdogTaskName `
                       -Action $wdAction `
                       -Trigger @($wdTrigger1, $wdTrigger2) `
                       -Settings $wdSettings `
                       -Force | Out-Null
Write-Host "  Watchdog task registered."

# --- 3. Kick the watchdog once now so the listener comes up immediately ----
Write-Host ""
Write-Host "[3/3] Running watchdog once to bring the listener up..."
Start-ScheduledTask -TaskName $WatchdogTaskName
Start-Sleep -Seconds 5

# --- Summary --------------------------------------------------------------
Write-Host ""
Write-Host "=== Done. Verification: ==="
Get-ScheduledTask -TaskName $ListenerTaskName | Select-Object TaskName,State | Format-Table
Get-ScheduledTask -TaskName $WatchdogTaskName | Select-Object TaskName,State | Format-Table
Write-Host "Watchdog log tail:"
$wdLog = Join-Path $Root "scratchpad\telegram_listener_watchdog.log"
if (Test-Path $wdLog) { Get-Content $wdLog -Tail 10 }
