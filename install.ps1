$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "JARVIS PRIME v1.2 - Instalador" -ForegroundColor Cyan
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

Write-Host "Dependencias opcionales de JARVIS PRIME 1.0..." -ForegroundColor Cyan
& $python -m pip install --disable-pip-version-check psutil pyautogui edge-tts playsound3
if ($LASTEXITCODE -ne 0) { Write-Warning "Alguna mejora opcional no se instaló; JARVIS conserva funciones básicas." }

Write-Host "Instalando detección opcional de doble aplauso y palabra clave..." -ForegroundColor Cyan
& $python -m pip install --disable-pip-version-check numpy sounddevice
if ($LASTEXITCODE -ne 0) { Write-Warning "No se instaló escucha ambiental; el clic seguirá funcionando." }
& $python -m pip install --disable-pip-version-check vosk
if ($LASTEXITCODE -ne 0) { Write-Warning "Vosk no disponible; el doble aplauso y el clic pueden seguir funcionando." }
Write-Host "Para palabra clave se necesita un modelo de Vosk en español descargado por separado y su carpeta configurada desde el panel." -ForegroundColor Yellow
