# JARVIS PRIME v0.1

Asistente modular de escritorio para Windows. Primera versión funcional escrita desde cero.

## Instalación
Requiere Windows 10/11 y Python 3.10 o superior.

1. Descarga el ZIP desde **Code > Download ZIP** y descomprímelo.
2. Abre PowerShell en la carpeta del proyecto.
3. Ejecuta `powershell -ExecutionPolicy Bypass -File .\install.ps1`.
4. Ejecuta `powershell -ExecutionPolicy Bypass -File .\start.ps1`.

Para activar conversación con IA, edita el archivo local `.env` con tu clave, URL de API compatible con OpenAI y modelo. **Nunca publiques .env.**

## Funciones disponibles
- HUD oscuro de escritorio y chat no bloqueante.
- Memoria SQLite persistente: `recuerda comprar leche`, `qué recuerdas`.
- Comandos permitidos: `abrir calculadora`, `abrir bloc de notas`.
- Chat con un proveedor externo compatible con OpenAI (opcional).
- Sin ejecución arbitraria de código ni comandos por parte de la IA.

## Arquitectura
`jarvis_prime/app.py` (interfaz) → `jarvis_prime/core.py` (acciones permitidas, SQLite, API).

## Próximas fases
Voz española (PTT, VAD, STT/TTS), HUD animado, acciones Windows con confirmación, n8n, plugins y diagnóstico.

## Pruebas
`python -m unittest discover -s tests -v`

El código es nuevo; las licencias de terceros se revisarán antes de incorporar componentes externos.
