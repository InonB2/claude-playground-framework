# set_static_ip.ps1 — Set Wi-Fi adapter to static IP for C&C server
# MUST be run as Administrator (right-click PowerShell → "Run as administrator")
# Then execute: powershell -ExecutionPolicy Bypass -File "D:\Claude Playground\scripts\set_static_ip.ps1"
#
# Target:  192.168.68.200 /24
# Gateway: 192.168.68.1
# DNS:     10.100.102.1, 192.168.68.1
# Adapter: Wi-Fi (InterfaceIndex 16)

$ErrorActionPreference = "Stop"
$AdapterName = "Wi-Fi"
$StaticIP    = "192.168.68.200"
$PrefixLen   = 24
$Gateway     = "192.168.68.1"
$DNS         = @("10.100.102.1", "192.168.68.1")

Write-Host "[set_static_ip] Starting network reconfiguration..." -ForegroundColor Cyan

# 1. Remove existing DHCP addresses and routes
Write-Host "[set_static_ip] Removing existing IP/routes..."
Remove-NetIPAddress  -InterfaceAlias $AdapterName -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
Remove-NetRoute      -InterfaceAlias $AdapterName -DestinationPrefix "0.0.0.0/0" -Confirm:$false -ErrorAction SilentlyContinue

# 2. Disable DHCP
Write-Host "[set_static_ip] Disabling DHCP..."
Set-NetIPInterface -InterfaceAlias $AdapterName -Dhcp Disabled

# 3. Set static IP
Write-Host "[set_static_ip] Setting static IP: $StaticIP/$PrefixLen gateway $Gateway..."
New-NetIPAddress -InterfaceAlias $AdapterName -IPAddress $StaticIP -PrefixLength $PrefixLen -DefaultGateway $Gateway

# 4. Set DNS
Write-Host "[set_static_ip] Setting DNS servers: $($DNS -join ', ')..."
Set-DnsClientServerAddress -InterfaceAlias $AdapterName -ServerAddresses $DNS

# 5. Verify
Write-Host "[set_static_ip] Verifying connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$ping = Test-Connection 8.8.8.8 -Count 2 -Quiet
if ($ping) {
    Write-Host "[set_static_ip] Internet connectivity: OK" -ForegroundColor Green
} else {
    Write-Host "[set_static_ip] WARNING: Internet connectivity check failed. Check gateway." -ForegroundColor Red
}

# 6. Test C&C server
try {
    $resp = Invoke-WebRequest "http://${StaticIP}:3000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "[set_static_ip] C&C /health: $($resp.StatusCode) OK" -ForegroundColor Green
} catch {
    Write-Host "[set_static_ip] C&C server not responding on $StaticIP:3000 (may need restart)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[set_static_ip] DONE. Fixed IP: $StaticIP" -ForegroundColor Green
Write-Host "[set_static_ip] C&C Dashboard: http://${StaticIP}:3000"
Write-Host "[set_static_ip] Health check:  http://${StaticIP}:3000/health"
Write-Host "[set_static_ip] Remote restart: http://${StaticIP}:3000/restart"

# 7. Update scratchpad record
$record = @"
Static IP: $StaticIP
Adapter:   $AdapterName (index 16)
Subnet:    /24 (255.255.255.0)
Gateway:   $Gateway
DNS:       $($DNS -join ', ')
Set on:    $(Get-Date -Format 'yyyy-MM-dd HH:mm')
C&C URL:   http://${StaticIP}:3000
Health:    http://${StaticIP}:3000/health
Restart:   http://${StaticIP}:3000/restart
"@
$record | Set-Content "D:\Claude Playground\scratchpad\cc_server_static_ip.txt" -Encoding UTF8
Write-Host "[set_static_ip] Saved to scratchpad/cc_server_static_ip.txt"
