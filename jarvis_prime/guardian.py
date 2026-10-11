"""Explicit-action guardrails, audit history and emergency stop."""
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from .config import FOLDER

STOP = threading.Event()
AUDIT = FOLDER / "audit.jsonl"
SENSITIVE = ("borra", "elimina", "formatea", "compra", "paga", "publica", "envia", "instala", "desinstala", "ejecuta powershell", "cmd")
def is_sensitive(text):
    from .windows_apps import normalize
    return any(term in normalize(text) for term in SENSITIVE)
def authorize(text, approved=False):
    if STOP.is_set():
        return False, "Ejecución detenida. Usa 'reanuda jarvis' para volver a habilitar herramientas."
    if is_sensitive(text) and not approved:
        return False, "Esta acción requiere confirmación y un módulo autorizado; no la ejecutaré automáticamente."
    return True, ""
def audit(action, outcome):
    try:
        FOLDER.mkdir(parents=True, exist_ok=True)
        # Never log arbitrary user content or API credentials: only action identifiers.
        record = {"time": datetime.now(timezone.utc).isoformat(),
                  "action": str(action)[:64], "outcome": str(outcome)[:80]}
        with AUDIT.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
def emergency_stop():
    STOP.set()
    audit("stop", "active")
    return "Herramientas pausadas. Ninguna nueva acción local será ejecutada."
def resume():
    STOP.clear()
    audit("resume", "ready")
    return "Herramientas habilitadas de nuevo."
