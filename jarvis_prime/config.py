"""Local preferences and protected API credential store."""
import json
import os
from pathlib import Path

FOLDER = Path.home() / ".jarvis-prime"
SETTINGS = FOLDER / "settings.json"
DEFAULTS = {"provider": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "model": "", "timeout": 45}

def load_settings():
    data = DEFAULTS.copy()
    try:
        value = json.loads(SETTINGS.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            data.update({k: v for k, v in value.items() if k in DEFAULTS})
    except (FileNotFoundError, ValueError, OSError):
        pass
    return data

def save_settings(settings):
    FOLDER.mkdir(parents=True, exist_ok=True)
    data = {k: settings.get(k, value) for k, value in DEFAULTS.items()}
    tmp = SETTINGS.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, SETTINGS)

def save_key(key):
    """On Windows, protect API key with DPAPI (per Windows user)."""
    if os.name != "nt":
        raise RuntimeError("El almacenamiento seguro de claves requiere Windows.")
    import ctypes
    from ctypes import wintypes
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]
    def blob(raw):
        buf = ctypes.create_string_buffer(raw)
        return DATA_BLOB(len(raw), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte))), buf
    FOLDER.mkdir(parents=True, exist_ok=True)
    incoming, buf = blob(key.encode("utf-8"))
    outgoing = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(incoming), "JARVIS PRIME", None, None, None, 0, ctypes.byref(outgoing)):
        raise ctypes.WinError()
    try:
        encrypted = ctypes.string_at(outgoing.pbData, outgoing.cbData)
        (FOLDER / "api.key.dpapi").write_bytes(encrypted)
    finally:
        ctypes.windll.kernel32.LocalFree(outgoing.pbData)

def load_key():
    file = FOLDER / "api.key.dpapi"
    if not file.exists() or os.name != "nt":
        return os.getenv("JARVIS_API_KEY", "")
    import ctypes
    from ctypes import wintypes
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]
    raw = file.read_bytes()
    buf = ctypes.create_string_buffer(raw)
    incoming = DATA_BLOB(len(raw), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
    outgoing = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(incoming), None, None, None, None, 0, ctypes.byref(outgoing)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(outgoing.pbData, outgoing.cbData).decode("utf-8")
    finally:
        ctypes.windll.kernel32.LocalFree(outgoing.pbData)
