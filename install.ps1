$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -m venv .venv
} else {
    & python -m venv .venv
}
if ($LASTEXITCODE -ne 0) { throw "Instala Python 3.10 o superior." }
if (!(Test-Path ".env")) { Copy-Item ".env.example" ".env" }
Write-Host "Instalado. Ejecuta .\start.ps1" -ForegroundColor Cyan
