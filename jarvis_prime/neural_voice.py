"""Optional neural Spanish TTS using Piper; Windows SAPI remains fallback.

Piper is installed separately; voice models must be obtained under their own licenses.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import threading

_MODEL_CACHE = {}
_MODEL_LOCK = threading.Lock()

def piper_model():
    candidate = os.environ.get("JARVIS_PIPER_MODEL", "")
    if not candidate:
        candidate = str(Path.home() / ".jarvis-prime" / "voices" / "es_MX-ald-medium.onnx")
    model = Path(candidate).expanduser()
    return model if model.is_file() and model.with_suffix(model.suffix + ".json").is_file() else None

def available():
    if sys.platform != "win32":
        return False
    try:
        import piper  # noqa: F401
    except ImportError:
        return False
    return piper_model() is not None

def speak_neural(text):
    if not available():
        return False
    model = piper_model()
    from piper.voice import PiperVoice
    with _MODEL_LOCK:
        if str(model) not in _MODEL_CACHE:
            _MODEL_CACHE.clear()
            _MODEL_CACHE[str(model)] = PiperVoice.load(str(model))
        voice = _MODEL_CACHE[str(model)]
    import wave
    with tempfile.TemporaryDirectory(prefix="jarvis-tts-") as folder:
        filename = str(Path(folder) / "speech.wav")
        with wave.open(filename, "wb") as wave_file:
            voice.synthesize_wav(text[:1200], wave_file)
        import winsound
        winsound.PlaySound(filename, winsound.SND_FILENAME)
    return True
