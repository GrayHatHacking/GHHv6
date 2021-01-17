
Write-Host "Disabling Telemetry..."
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Type DWord -Value 0
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Type DWord -Value 0
Set-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Type DWord -Value 0

Write-Host "Disabling Telemetry services..." 
Get-Service -Name "diagnosticshub.standardcollector.service" | Set-Service -StartupType Disabled | Stop-Service # Microsoft (R) Diagnostics Hub Standard Collector Service
Get-Service -Name "DiagTrack" | Set-Service -StartupType Disabled | Stop-Service # Diagnostics Tracking Service

Write-Host "Installing Chocolatey"
Set-ExecutionPolicy Bypass -Scope Process -Force; 
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))


Write-Host "Starting SendWindowsIsReady"
C:\ProgramData\Amazon\EC2-Windows\Launch\Scripts\SendWindowsIsReady.ps1 -Schedule
Write-Host "Starting InitliazeInstance"
C:\ProgramData\Amazon\EC2-Windows\Launch\Scripts\InitializeInstance.ps1 -Schedule
Write-Host "performing Sysprep"
C:\ProgramData\Amazon\EC2-Windows\Launch\Scripts\SysprepInstance.ps1 -NoShutdown
Write-Host "SYSPREP Finished..."
