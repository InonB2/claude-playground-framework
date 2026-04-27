# GitHub Auto-Sync Script — PowerShell
# Commits any changes and pushes to GitHub
# Run manually: powershell -ExecutionPolicy Bypass -File "D:\Claude Playground\scripts\github_sync.ps1"
# Auto-run: configured via Windows Task Scheduler (see bottom of this file)

$repoPath = "D:\Claude Playground"
$logFile  = "$repoPath\logs\github_sync.log"

if (-not (Test-Path "$repoPath\logs")) { New-Item -ItemType Directory -Path "$repoPath\logs" | Out-Null }

function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
    Add-Content -Path $logFile -Value $line
    Write-Host $line
}

Set-Location $repoPath

# Check for any changes
$status = git status --porcelain 2>&1
if ($status) {
    Log "Changes detected — staging all files"
    git add -A
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "Auto-sync: $timestamp" 2>&1 | ForEach-Object { Log $_ }
} else {
    Log "No local changes to commit"
}

# Always push (catches commits not yet pushed)
Log "Pushing to GitHub..."
$pushResult = git push origin master 2>&1
$pushResult | ForEach-Object { Log $_ }

if ($LASTEXITCODE -eq 0) {
    Log "Sync complete — OK"
} else {
    Log "Push FAILED — check credentials or network"
    exit 1
}

# --- Task Scheduler setup (run once to register auto-sync) ---
# To install as a daily task at 9:00 AM, run this block manually once:
#
# $action  = New-ScheduledTaskAction -Execute "powershell.exe" `
#              -Argument '-ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\Claude Playground\scripts\github_sync.ps1"'
# $trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
# $settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable -StartWhenAvailable
# Register-ScheduledTask -TaskName "Claude-Playground-GitHub-Sync" -Action $action -Trigger $trigger `
#   -Settings $settings -RunLevel Highest -Force
