"""Spanish speech input/output. Uses offline Windows SAPI when possible."""
import subprocess
import sys
from .neural_voice import speak_neural

def speak(text):
    if not text or not text.strip():
        return
    try:
        if speak_neural(text):
            return
    except Exception:
        # Missing/incompatible model must never silence JARVIS.
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
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=seconds, phrase_time_limit=15)
        return recognizer.recognize_google(audio, language="es-GT")
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        raise RuntimeError("El reconocimiento necesita Internet: " + str(exc)) from exc
    except (OSError, AttributeError) as exc:
        raise RuntimeError("Revisa PyAudio y los permisos del micrófono: " + str(exc)) from exc
