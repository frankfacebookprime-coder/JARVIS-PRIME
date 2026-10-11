# JARVIS PRIME v0.4 — Command Center, navegador y voz

Asistente modular y extensible. **Ahora puedes conectar tu IA directamente desde el panel**, sin editar archivos manualmente.

## Instalación (Windows 10/11, Python 3.10+)

1. Descarga **Code → Download ZIP** (o clona el repositorio) y descomprime en una carpeta fija.
2. Abre PowerShell en esa carpeta.
3. Ejecuta `powershell -ExecutionPolicy Bypass -File .\install.ps1`.
4. Ejecuta `powershell -ExecutionPolicy Bypass -File .\start.ps1`.

### Conectar una IA
1. Pulsa **CONFIGURAR IA**.
2. Escoge **OpenRouter**, **OpenAI**, **DeepSeek** o **Personalizado / OmniRouter**.
3. Pega la API Key (para servicios locales que no requieran autenticación, usa la clave ficticia que admita tu servidor).
4. Pulsa **BUSCAR MODELOS**, selecciona uno o escribe el ID manualmente.
5. Pulsa **PROBAR API** y luego **GUARDAR Y USAR ESTA IA**.

**Nota:** el botón de detectar modelos requiere que el proveedor exponga `GET /models`. Si no existe, escribe manualmente el modelo. La prueba real utiliza `POST /chat/completions` y puede consumir créditos.

### Navegador con lenguaje natural (nuevo v0.4)
- `puedes abrir YouTube en Google` abre https://www.youtube.com/ en el navegador predeterminado.
- `abre YouTube`, `abre Google`, `abre Gmail`, `abre GitHub`.
- `busca gatos en Google` hace una búsqueda web.
- La intención web se procesa **antes** de buscar una app instalada. La apertura se solicita al sistema operativo, pero debe verificarse visualmente en el equipo.

### Nuevo panel
- Barra lateral, accesos rápidos a YouTube, Google, Word y Chrome.
- HUD circular animado, área central de conversación y estado de IA.
- Botón HABLAR y casilla de voz (activada por defecto). Si falla audio, el chat de texto continúa funcionando.

### Windows: abrir aplicaciones con lenguaje natural
Escribe `abre Word`, `abre Chrome`, `abre Excel`, `abre la calculadora` o `abre el bloc de notas`.
JARVIS busca los accesos instalados del menú Inicio y las aplicaciones registradas en Windows (Get-StartApps).
También puedes pulsar **APLICACIONES** para consultar aplicaciones detectadas.\n\nDiagnósticos de solo lectura: \`estado de mi computadora\` y \`ver procesos\`. Estos comandos no hacen cambios en el sistema.
No ejecuta comandos arbitrarios ni instala programas automáticamente. Si hay nombres ambiguos o una aplicación no está instalada, informa del fallo.
El mensaje «Windows recibió la orden» significa que se inició el lanzamiento; no confirma que la ventana esté visible.

### Voz española (opcional)
Botón **HABLAR** para una frase por pulsación y casilla **Leer respuestas** para síntesis de voz.
Al ejecutar `install.ps1` se intenta instalar `pyttsx3`, `SpeechRecognition` y `PyAudio` automáticamente.\nLa salida de voz utiliza primero el sintetizador integrado de Windows (SAPI); se utiliza `pyttsx3` como alternativa.

Nota: PyAudio puede necesitar correcciones manuales en ciertas versiones de Python. El reconocimiento por defecto usa Google Speech Recognition y envía audio al servicio externo: requiere Internet. No es una solución sin conexión ni escucha permanente; el sintetizador usa las voces instaladas en Windows, cuya calidad depende del equipo.

### Funciones actuales
- Interfaz oscura con **HUD circular animado**, chat y centro de configuración.
- API OpenAI-compatible con selección de proveedor y modelo.
- API Key almacenada cifrada con **Windows DPAPI**, vinculada al usuario de Windows, en `%USERPROFILE%\.jarvis-prime\api.key.dpapi`; no se sube a GitHub.
- Preferencias locales en `%USERPROFILE%\.jarvis-prime\settings.json`.
- Memoria SQLite persistente en `%USERPROFILE%\.jarvis-prime\memory.sqlite3`.
- Inicio de apps instaladas desde lenguaje natural y lista de aplicaciones registradas.
- Voz opcional de pulsar para hablar y respuestas habladas.
- Memoria: `recuerda comprar leche`, `qué recuerdas`.
- Chat y pruebas de red sin bloquear la interfaz.
- El asistente **no ejecuta código arbitrario** generado por la IA.

### Actualizar sin perder datos
1. **Cierra JARVIS PRIME**.
2. Haz copia de seguridad de la carpeta de instalación y de `%USERPROFILE%\.jarvis-prime` antes de actualizar.
3. Reemplaza el código por la última versión de `main` o ejecuta `git pull --ff-only` si utilizaste git.
4. Ejecuta nuevamente `install.ps1` y después `start.ps1`.
5. Comprueba la memoria y la conexión desde **CONFIGURAR IA**.

No copies contraseñas ni claves a conversaciones, tickets o capturas. No subas `.env` a GitHub.

## Arquitectura
- `jarvis_prime/app.py`: interfaz Tkinter (UI thread + cola para tareas asíncronas).
- `jarvis_prime/config.py`: preferencias locales + protección DPAPI de credenciales.
- `jarvis_prime/network.py`: validación de URLs, conexión y descubrimiento de modelos.
- `jarvis_prime/core.py`: memoria, comandos explícitos y router básico.

## Pruebas
`python -m unittest discover -s tests -v`

La prueba automática de Windows está en GitHub Actions. El funcionamiento visual, voz, el lanzamiento de Word y la integración con proveedores reales requieren pruebas en un equipo Windows con las apps instaladas.

## Próximos módulos
Voz en español (PTT/VAD/STT/TTS), HUD circular animado, sesiones de chat, manejo seguro de ventanas/archivos, n8n y plugins, autodiagnóstico, actualizador con rollback.

El código de esta versión es propio. Antes de integrar componentes de terceros revisaremos sus licencias.
