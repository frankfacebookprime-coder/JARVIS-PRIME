"""Dependency diagnostics without network calls or secret exposure."""
import importlib.util
import sys
from .config import load_settings
from .neural_voice import piper_model
def report():
    settings = load_settings()
    packages = ("piper", "pywinauto", "pyautogui", "psutil", "speech_recognition", "pyaudio", "edge_tts")
    lines = ["Autodiagnóstico JARVIS PRIME", "Python: "+sys.version.split()[0],
             "IA configurada: "+("sí" if settings.get("model") else "no"),
             "Piper modelo: "+("detectado" if piper_model() else "sin configurar")]
    for package in packages:
        try: found = importlib.util.find_spec(package) is not None
        except (ImportError, ValueError): found = False
        lines.append(package+": "+("disponible" if found else "no instalado"))
    return "\n".join(lines)
