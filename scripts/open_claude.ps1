Set-Location "D:\Claude Playground"
$env:CI = "true"
$env:PATH += ";C:\Users\Inon Baasov\AppData\Roaming\npm"
python "D:\Claude Playground\scripts\buildar_notify.py" update "Andy remote session started — resuming paused tasks. Use /continue to check in."
claude -c
