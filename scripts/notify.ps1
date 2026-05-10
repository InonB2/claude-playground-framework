# notify.ps1 - Windows Toast Notification for Andy AI Team
# Usage:
#   powershell -ExecutionPolicy Bypass -File notify.ps1 -Title "Andy" -Message "Task complete"
#   powershell -ExecutionPolicy Bypass -File notify.ps1 -Title "Andy" -Message "Waiting for input" -Type "input"
#
# Types: "info" (default), "input" (waiting), "done" (task complete), "error"
# Runs via Windows PowerShell 5.1 for WinRT support, falls back to Windows.Forms balloon

param(
    [string]$Title   = "Andy AI",
    [string]$Message = "Notification",
    [ValidateSet("info","input","done","error")]
    [string]$Type    = "info"
)

# --- Resolve display title ---
$displayTitle = switch ($Type) {
    "input" { "Andy AI - Waiting for You" }
    "done"  { "Task Complete" }
    "error" { "Error" }
    default { "Andy AI" }
}
if ($Title -ne "Andy AI") { $displayTitle = $Title }

# --- Method 1: WinRT Toast via Windows PowerShell 5.1 ---
function Send-WinRTToast {
    param(
        [string]$ToastTitle,
        [string]$ToastMessage
    )

    $ps5 = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    if (-not (Test-Path $ps5)) { return $false }

    # Build the inner script as a temp file to avoid quoting issues
    $tempScript = [System.IO.Path]::GetTempFileName() + ".ps1"
    $inner = @'
try {
    [Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime] | Out-Null

    $appId = "Andy.AI.Agent"
    $templateType = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($templateType)
    $toastXml = [xml] $template.GetXml()

    $titleNode = $toastXml.GetElementsByTagName("text")[0]
    $bodyNode  = $toastXml.GetElementsByTagName("text")[1]
    $titleNode.AppendChild($toastXml.CreateTextNode($env:TOAST_TITLE)) | Out-Null
    $bodyNode.AppendChild($toastXml.CreateTextNode($env:TOAST_MESSAGE)) | Out-Null

    $xmlDoc = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xmlDoc.LoadXml($toastXml.OuterXml)
    $toast    = [Windows.UI.Notifications.ToastNotification]::new($xmlDoc)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId)
    $notifier.Show($toast)
    exit 0
} catch {
    Write-Host "WinRT error: $_"
    exit 1
}
'@
    Set-Content -Path $tempScript -Value $inner -Encoding UTF8

    $env:TOAST_TITLE   = $ToastTitle
    $env:TOAST_MESSAGE = $ToastMessage

    & $ps5 -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File $tempScript
    $result = ($LASTEXITCODE -eq 0)

    Remove-Item $tempScript -ErrorAction SilentlyContinue
    Remove-Item Env:\TOAST_TITLE   -ErrorAction SilentlyContinue
    Remove-Item Env:\TOAST_MESSAGE -ErrorAction SilentlyContinue

    return $result
}

# --- Method 2: Windows.Forms balloon tip (fallback) ---
function Send-BalloonTip {
    param(
        [string]$BalloonTitle,
        [string]$BalloonMessage
    )

    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        Add-Type -AssemblyName System.Drawing       -ErrorAction Stop

        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon              = [System.Drawing.SystemIcons]::Information
        $notify.Visible           = $true
        $notify.BalloonTipTitle   = $BalloonTitle
        $notify.BalloonTipText    = $BalloonMessage
        $notify.BalloonTipIcon    = [System.Windows.Forms.ToolTipIcon]::Info
        $notify.ShowBalloonTip(8000)
        Start-Sleep -Milliseconds 500
        $notify.Dispose()
        return $true
    } catch {
        Write-Warning "BalloonTip failed: $_"
        return $false
    }
}

# --- Attempt delivery ---
$sent = Send-WinRTToast -ToastTitle $displayTitle -ToastMessage $Message

if (-not $sent) {
    Write-Host "WinRT unavailable, falling back to BalloonTip..."
    $sent = Send-BalloonTip -BalloonTitle $displayTitle -BalloonMessage $Message
}

if ($sent) {
    Write-Host "[OK] Notification sent: [$Type] $displayTitle - $Message"
    exit 0
} else {
    Write-Warning "[FAIL] Could not deliver notification. Check PowerShell environment."
    exit 1
}
