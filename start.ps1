$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv\Scripts\pythonw.exe"
if (!(Test-Path $python)) { throw "Ejecuta primero .\install.ps1" }
Start-Process -FilePath $python -ArgumentList "-m jarvis_prime" -WorkingDirectory $PSScriptRoot
