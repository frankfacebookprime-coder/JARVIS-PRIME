$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "JARVIS PRIME v0.7 - Instalador" -ForegroundColor Cyan
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -m venv .venv
} else {
    & python -m venv .venv
}
if ($LASTEXITCODE -ne 0) { throw "Necesitas Python 3.10 o superior." }
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!(Test-Path ".env") -and (Test-Path ".env.example")) { Copy-Item ".env.example" ".env" }
Write-Host "Instalando módulos de voz..." -ForegroundColor Cyan
& $python -m pip install --disable-pip-version-check pyttsx3 SpeechRecognition
if ($LASTEXITCODE -ne 0) {
    Write-Warning "No se pudieron instalar todos los módulos de voz. El chat sigue disponible."
}
& $python -m pip install --disable-pip-version-check PyAudio
if ($LASTEXITCODE -ne 0) {
    Write-Warning "PyAudio no se pudo instalar. La entrada de micrófono requerirá una corrección manual."
}
Write-Host "Código preparado. Abre .\start.ps1 para ejecutar." -ForegroundColor Green

Write-Host "Instalando automatización de ventanas (opcional)..." -ForegroundColor Cyan
& $python -m pip install --disable-pip-version-check pywinauto
if ($LASTEXITCODE -ne 0) { Write-Warning "pywinauto no disponible; JARVIS seguirá abriendo aplicaciones normalmente." }
Write-Host "Piper neural TTS es opcional: ejecuta .venv\Scripts\python.exe -m pip install piper-tts" -ForegroundColor Yellow
Write-Host "Para activar Piper también debes instalar un modelo de voz español con licencia compatible." -ForegroundColor Yellow
