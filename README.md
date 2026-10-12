# JARVIS PRIME v1.3 — Panel único integrado y activación corregida

Asistente modular y extensible. **Ahora puedes conectar tu IA directamente desde el panel**, sin editar archivos manualmente.

## v1.3: cambios para mejorar el uso real

- **Una sola interfaz**: la esfera flotante sigue en el escritorio; al abrir JARVIS aparece el Command Center con una esfera animada integrada. El chat y la información generada se muestran **dentro del mismo panel**, alternándose en el área central sin abrir ventanas nuevas. La siguiente orden retira la vista informativa anterior.
- **Activación mejorada**: Vosk examina resultados parciales para responder antes a «Jarvis». El doble aplauso requiere **dos golpes separados con silencio intermedio**, con umbral de ruido adaptativo. Es un detector experimental que puede necesitar calibración en el equipo y con el micrófono reales.
- **Entrega del micrófono**: antes de escuchar la orden, JARVIS deja salir al detector ambiental, reduciendo conflictos entre las dos bibliotecas de grabación.
- **Estado visible**: la esfera muestra mensajes breves de arranque/errores de activación, no solamente la animación.
- **Sonidos renovados**: tonos sintetizados menos agudos, más cortos y suaves, con reproducción serializada para evitar superposición. Los sonidos pueden desactivarse.
- **Modo BOTH sin modelo**: cuando falta la carpeta Vosk en ejecución, el doble aplauso puede seguir funcionando y se informa del problema. Para reconocer palabras se requiere un modelo Vosk válido y cargable.
- **Panel de información**: se mantiene visible o se oculta según el temporizador configurado. «Cierra la información» vuelve al chat. No crea ventanas Knowledge Display adicionales.
- **Pruebas**: se verifican dos impulsos separados, no contar un aplauso prolongado dos veces y detección de palabra por límites de palabra.

### Para actualizar sin repetir problemas

Cierra todas las instancias antiguas de JARVIS y verifica que DeepSeek Harness instale desde `main` la última revisión (no un ZIP o copia anterior). Vuelve a ejecutar `install.ps1`, manteniendo `%USERPROFILE%\\.jarvis-prime` sin borrarla. Para activar `wake` o `both` configura una carpeta **real** de modelo español Vosk en «Activación de voz». En `clap` no necesitas Vosk. Si no responde a aplausos, prueba primero `clap` en una habitación silenciosa con dos palmadas cortas espaciadas aproximadamente 0,3–0,6 s; consulta los mensajes de Activación del panel. El micrófono ambiental consume recursos solo en modos activos y las frases después de activarlo siguen usando reconocimiento remoto según la configuración actual.

La validación de GitHub Actions confirma pruebas automatizadas de código, **no** prueba acústica, interfaz gráfica o dispositivos físicos. Haz esas pruebas en Windows antes de considerar la activación confiable.

## Novedades v1.2 — Activación ambiental opcional

La activación **está desactivada por defecto** hasta seleccionarla desde la nueva opción **Activación de voz** del Command Center o desde el menú contextual de la esfera.

**Modos seleccionables:**
- `click`: un clic activa el micrófono como siempre; es la opción por defecto.
- `clap`: detectar dos aplausos separados aproximadamente entre 0,18 y 0,8 segundos; se requiere `numpy` y `sounddevice`. Puede haber falsos positivos con sonidos secos y golpes fuertes.
- `wake`: escuchar una frase clave como «jarvis» mediante reconocimiento **local Vosk**. Requiere `vosk`, `numpy`, `sounddevice` y un modelo de español compatible guardado en el PC.
- `both`: permitir doble aplauso o palabra clave usando el mismo micrófono y flujo de detección.

Tras activarse, suena un efecto y JARVIS inicia **otra escucha de la instrucción**. Ejemplo: «Jarvis» [efecto de activación] «Abre Word». Las frases con la palabra clave no son necesariamente órdenes completas; espera al sonido.

### Modelo Vosk para activar por voz

1. Instala las dependencias con `install.ps1`.
2. Descarga el modelo español adecuado desde el catálogo oficial de Vosk: https://alphacephei.com/vosk/models (revisa licencia, tamaño y requisitos).
3. Descomprime el modelo en una carpeta fija del usuario, preferiblemente `%USERPROFILE%\\.jarvis-prime\\models\\vosk-es`.
4. Abre el panel → **Activación de voz**, selecciona `wake` o `both`, escribe la palabra clave y la ruta a la carpeta descomprimida. Guarda.
5. Si falla el modelo o micrófono, JARVIS debe mostrar error y seguirá funcionando por clic.

**Privacidad:** en los modos ambientales el micrófono permanece abierto para detectar sonido, pero la detección de aplausos y la palabra clave se realizan localmente; no se guarda audio ni se manda a servicios remotos. Después de activarse, la orden se transcribe con el proveedor de voz existente (Google Speech Recognition), que **sí envía el audio de esa frase a Internet**. No se activa el micrófono ambiental de forma oculta ni en modo `click`. La escucha ambiental puede gastar CPU, especialmente Vosk.

### Nuevo panel informativo

- **Una sola ventana reutilizable** para resultados de IA con encabezados tecnológicos, tarjetas numeradas, acentos luminosos y bloques organizados.
- Al comenzar una solicitud nueva, se oculta el resultado anterior; el siguiente resultado reemplaza el contenido.
- «Cierra la información» oculta el panel de conocimientos; «Oculta el panel» oculta el Command Center.
- En **Activación de voz** existe el control de permanencia: `0` segundos lo mantiene abierto hasta nueva orden; otro valor cierra el resultado después de ese tiempo.
- Sonidos sintéticos PCM renovados para escuchar, activación, panel, finalización y cierre. Pueden desactivarse desde el panel.

**Limitaciones:** el detector de aplausos es heurístico y requiere calibración en tu micrófono; no está garantizado que reconozca todos los aplausos ni que distinga golpes similares. Vosk puede no reconocer adecuadamente palabras personalizadas o nombres; prueba una frase clara. Las pruebas de GitHub Actions no sustituyen verificación de audio y pantalla en Windows.

## Novedades v1.1

- **Tareas locales de dos pasos**: «abre Word y luego abre Chrome», o «abre Word después abre Chrome». Solo se admiten pasos de los tipos ya autorizados (aplicaciones, navegador, ventanas, consulta local y panel). El segundo paso se cancela cuando el primero comunica un error. *No es un agente autónomo general; abrir una app no demuestra que haya aparecido visualmente.*
- **Captura con consentimiento real**: «mira mi pantalla» y botón «Capturar pantalla» solicitan autorización explícita por cada captura. La imagen se guarda en `%USERPROFILE%\\.jarvis-prime\\captures`, solo en el equipo. **No se analiza ni se envía automáticamente a la nube**.
- **Esfera conectada a la captura**: las solicitudes por voz abren el panel y muestran la misma confirmación.
- **Fin de frase ajustable**: el reconocimiento usa umbral de pausa configurable (0,5–2,5 s), escucha hasta 25 s por frase y permite ajustar la pausa desde «Configurar voz». Sigue utilizando Google Speech Recognition por Internet para transcribir, no VAD completamente offline.
- **Pruebas**: casos para secuencias válidas, bloqueo de secuencias sensibles, interrupción por errores y consentimiento de captura.

Estas funciones conservan la prohibición de ejecutar código libre devuelto por modelos de lenguaje. El botón de parada bloquea nuevas acciones locales del motor; no deshace una acción ya enviada al sistema operativo. Para probar voz, ventanas y pantalla es necesario ejecutar JARVIS en un equipo Windows real.

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
