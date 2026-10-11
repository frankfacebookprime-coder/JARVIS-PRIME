# JARVIS PRIME v1.0 — Arquitectura modular futurista para Windows

Asistente modular y extensible. **Ahora puedes conectar tu IA directamente desde el panel**, sin editar archivos manualmente.

## Versión 1.0 — Nuevas funciones integradas

Esta versión amplía el asistente existente; no requiere migrar tu memoria ni claves.

- **Voz multinivel:** Piper local, Edge TTS opcional por Internet y SAPI de respaldo. En el panel, **Configurar voz** permite cambiar motor, voz, velocidad y longitud de lectura. Por defecto usa Piper si está disponible; si no, intenta Edge si sus dependencias están instaladas; finalmente SAPI.
- **Piper optimizado:** se conserva el modelo cargado entre respuestas para reducir tiempos posteriores.
- **Control local:** comandos de aplicación/navegador, enfocar ventanas, más atajos explícitos «copiar selección», «pegar portapapeles», «seleccionar todo», «guardar documento».
- **Second Brain SQLite:** «guarda en second brain mi proyecto» y «busca en second brain proyecto». Memoria local consultable, sin enviar notas automáticamente a ningún servicio remoto.
- **Guardian:** «deten jarvis» pausa nuevas operaciones de Windows; «reanuda jarvis» vuelve a permitirlas. Operaciones sensibles se bloquean por defecto. El registro de auditoría almacena solamente categoría y resultado, no contenidos de las órdenes.
- **Monitor:** «monitor del sistema», CPU, RAM y disco, con psutil opcional.
- **Diagnóstico:** «diagnostico completo» muestra dependencias disponibles, sin publicar credenciales.
- **Habilidades:** «lista habilidades» muestra módulos disponibles, con registro estático.
- **Visión con consentimiento:** «mira mi pantalla» informa que se necesita aprobación. La función de captura local está implementada como `vision.capture(confirmed=True)` para integraciones futuras con confirmación explícita; **todavía no se analiza la captura con IA**.
- **Planificador:** `agent_planner.py` contiene una base restringida para detectar dos pasos, pero **no ejecuta aún cadenas de tareas**.
- **Interfaz:** menú de la esfera para diagnóstico, monitor y parada; panel de preferencias de voz.
- **Instalador:** intenta agregar dependencias opcionales `psutil`, `pyautogui`, `edge-tts` y `playsound3`. Piper requiere modelo independiente y licencia revisada.

### Límites honestos de la versión 1.0

No están implementados todavía una automatización general de navegador, la comprensión visual de capturas, conversación VAD de baja latencia, integración de Telegram/móvil, reproducción de voz interrumpible, planes de muchos pasos, agentes autónomos, permisos granulares por aplicación, ni selector multimodelo por costo. No se afirma que estas funciones estén terminadas. Son módulos que requieren implementación y pruebas de seguridad adicionales.

### Notas de seguridad

Los resultados de IA **nunca** se interpretan como código o instrucciones ejecutables. Los nuevos atajos afectan la ventana que esté activa en ese momento; verifica el foco antes de utilizarlos. Las capturas permanecen en el perfil del usuario si se realizan; no se comparten automáticamente.

## Novedades v0.7: proyectos open source

Se estudiaron estas herramientas, sin copiar código ajeno directamente:

- [Piper TTS](https://github.com/rhasspy/piper) para voz neuronal local en español. La integración es **opcional** y usa primero Piper si se instaló y configuró un modelo; de lo contrario utiliza la voz de Windows. Los modelos de voz tienen **licencias propias**, que debes revisar antes de descargarlos y distribuirlos.
- [pywinauto](https://github.com/pywinauto/pywinauto) (BSD-3-Clause) para detectar ventanas y enfocar una ventana concreta. Se instala desde el instalador; no permite ejecutar comandos arbitrarios.
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) como referencia para futuras mejoras del panel. **No se ha migrado la interfaz a esta biblioteca**. La esfera sí incorpora anillos con colores reactivos según su estado.

### Activar voz neuronal Piper en Windows

1. Ejecuta `.venv\\Scripts\\python.exe -m pip install piper-tts` en la carpeta del proyecto.
2. Obtén de un repositorio confiable un modelo compatible de Piper en español, revisa la licencia específica de la voz y coloca **ambos archivos** `.onnx` y `.onnx.json` en `%USERPROFILE%\\.jarvis-prime\\voices`.
3. Usa el nombre predeterminado `es_MX-ald-medium.onnx` y `es_MX-ald-medium.onnx.json`, **o** configura la variable de entorno `JARVIS_PIPER_MODEL` con la ruta completa de tu modelo.
4. Reinicia JARVIS. Si Piper no está disponible o falla, JARVIS usa Windows SAPI como alternativa.

La voz neuronal puede usar CPU y consumir más memoria que SAPI. No se descarga ningún modelo automáticamente y la calidad depende de la voz escogida.

### Nuevas órdenes de control de ventanas

- «Qué ventanas tengo abiertas»: lista los títulos de ventanas visibles.
- «Cambia a Chrome»: enfoca la ventana cuando existe una sola coincidencia.
- «Enfoca Word»: cambia el foco si el nombre coincide sin ambigüedad.

Si hay varias ventanas coincidentes, JARVIS pide especificar el título. No escribe, hace clic, cierra programas ni borra archivos por estas órdenes.

## Modo flotante (v0.6)

JARVIS ahora inicia como **una esfera circular flotante y animada** sobre Windows, en lugar de abrir el panel completo. Es una ventana sin bordes y siempre visible. En Windows se intenta aplicar transparencia al exterior del círculo.

- **Un clic** sobre la esfera: activa una sesión de voz en español.
- **Arrastrar** la esfera: mueve JARVIS a otra posición de la pantalla.
- **Doble clic**: abre u oculta el panel completo.
- **Clic derecho**: menú con **Abrir panel**, **Hablar con JARVIS**, **Ocultar panel** y **Salir**.
- **Orden de voz:** «Jarvis, abre el panel» abre el Command Center solo cuando se solicita.
- **Cerrar el panel** con la X lo oculta; la esfera permanece funcionando. La opción **Salir** en la esfera cierra toda la aplicación.

La escucha **no está siempre encendida**: debes activar una sesión mediante un clic o el menú, por privacidad y para evitar capturas accidentales. La voz usa las dependencias y permisos documentados más abajo.

Si necesitas abrir únicamente el panel clásico para diagnosticar, desde PowerShell puedes ejecutar:
`.venv\\Scripts\\python.exe -m jarvis_prime.app`.

Al actualizar, **no borres** `%USERPROFILE%\\.jarvis-prime`: allí se guardan la memoria, las claves de API y preferencias.

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

### IA y panel de información (v0.6)
- **Órdenes** («abre Word», «abre YouTube», «ver procesos») se resuelven con herramientas locales verificables, no con instrucciones generadas por el modelo.
- **Consultas** («qué es Linux», «investiga Wim Hof y muéstramelo») se envían a la API de IA configurada y abren automáticamente un panel de información legible, con encabezado y tarjetas.
- El texto generado por la IA es solamente contenido visual; **no se ejecuta como código**.
- La esfera reproduce efectos cortos sintetizados para escuchar, respuesta y apertura del panel en Windows.
- La voz continúa siendo **por pulsación**, no escucha continua ni activación con palabra clave.

### Panel avanzado (opcional)
- Panel oculto por defecto y accesible desde la esfera. Barra lateral, accesos rápidos a YouTube, Google, Word y Chrome.
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
- `jarvis_prime/floating.py`: esfera flotante transparente, animación, arrastre, menú y voz.\n- `jarvis_prime/app.py`: panel completo opcional (UI thread + cola para tareas asíncronas).
- `jarvis_prime/config.py`: preferencias locales + protección DPAPI de credenciales.
- `jarvis_prime/network.py`: validación de URLs, conexión y descubrimiento de modelos.
- `jarvis_prime/core.py`: memoria, comandos explícitos y router básico.

## Pruebas
`python -m unittest discover -s tests -v`

La prueba automática de Windows está en GitHub Actions. El funcionamiento visual, voz, el lanzamiento de Word y la integración con proveedores reales requieren pruebas en un equipo Windows con las apps instaladas.

## Limitaciones actuales
- La clasificación de intención está basada en reglas conservadoras; no comprende todavía cualquier instrucción ambigua o compleja.
- El panel organiza párrafos y listas del modelo; no inventa datos, fuentes ni gráficos.
- La verificación real del audio, transparencia y visualización requiere ejecutar en Windows.

## Próximos módulos
Voz en español (PTT/VAD/STT/TTS), HUD circular animado, sesiones de chat, manejo seguro de ventanas/archivos, n8n y plugins, autodiagnóstico, actualizador con rollback.

El código específico de integración de esta versión es propio. Las dependencias externas conservan sus licencias respectivas; los modelos de voz deben revisarse individualmente.
