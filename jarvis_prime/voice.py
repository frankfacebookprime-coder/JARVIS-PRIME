"""Spanish speech input/output. Uses offline Windows SAPI when possible."""
import subprocess
import sys
from .neural_voice import speak_neural
from .config import load_settings

def _speak_edge(text, options):
    """Optional cloud-connected Edge speech synthesis without a local heavyweight model."""
    import asyncio
    import tempfile
    from pathlib import Path
    import edge_tts
    from playsound3 import playsound
    voice = options.get("tts_voice") or "es-MX-DaliaNeural"
    # Whitelist locale/voice-id shape to avoid arbitrary parameters.
    import re
    if not re.fullmatch(r"[a-z]{2}-[A-Z]{2}-[A-Za-z]+Neural", voice):
        voice = "es-MX-DaliaNeural"
    with tempfile.TemporaryDirectory(prefix="jarvis-edge-") as temp:
        target = str(Path(temp) / "spoken.mp3")
        rate = max(-50, min(50, int(options.get("tts_rate", 0))))
        async def write():
            speech = edge_tts.Communicate(text, voice=voice, rate=f"{rate:+d}%")
            await speech.save(target)
        asyncio.run(write())
        playsound(target)
    return True

def speak(text):
    if not text or not text.strip():
        return
    options = load_settings()
    text = text[:max(60, min(int(options.get("voice_max_chars", 750)), 2000))]
    engine = options.get("tts_engine", "auto")
    if engine == "edge":
        try:
            if _speak_edge(text, options):
                return
        except Exception:
            pass
    try:
        if engine in ("auto", "piper") and speak_neural(text):
            return
    except Exception:
        # Missing/incompatible model must never silence JARVIS.
        pass
    if engine == "auto":
        try:
            if _speak_edge(text, options):
                return
        except Exception:
            pass
    if sys.platform == "win32":
        # Speech engine is built into Windows; no API key or audio upload needed.
        script = """Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'es-*' } | Select-Object -First 1
if ($v) { $s.SelectVoice($v.VoiceInfo.Name) }
$s.Rate = 0
$s.Speak([Console]::In.ReadToEnd())
"""
        try:
            result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                                    input=text[:1200], capture_output=True, text=True,
                                    timeout=70, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if result.returncode == 0:
                return
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError("La voz no está disponible. Ejecuta install.ps1 para instalar el motor opcional.") from exc
    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    voices = engine.getProperty("voices")
    spanish = next((v for v in voices if "spanish" in (str(v.name) + " " + str(v.id)).lower()
                    or "es-" in str(v.id).lower()), None)
    if spanish:
        engine.setProperty("voice", spanish.id)
    engine.say(text[:1200])
    engine.runAndWait()

def listen_once(seconds=6):
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise RuntimeError("Falta SpeechRecognition. Ejecuta install.ps1.") from exc
    recognizer = sr.Recognizer()
    options = load_settings()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = max(0.5, min(float(options.get("pause_threshold", 1.0)), 2.5))
    recognizer.non_speaking_duration = min(0.5, recognizer.pause_threshold / 2)
    timeout = max(3, min(int(options.get("listen_timeout", seconds)), 25))
    phrase_limit = max(5, min(int(options.get("phrase_time_limit", 25)), 60))
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        return recognizer.recognize_google(audio, language="es-GT")
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        raise RuntimeError("El reconocimiento necesita Internet: " + str(exc)) from exc
    except (OSError, AttributeError) as exc:
        raise RuntimeError("Revisa PyAudio y los permisos del micrófono: " + str(exc)) from exc
