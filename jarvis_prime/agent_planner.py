"""Two-step allowlisted task runner. Never execute model-generated instructions."""
import re
from .windows_apps import normalize

SPLIT = re.compile(r"\s+(?:y\s+luego|despu[eé]s)\s+", re.IGNORECASE)
SAFE_KINDS = frozenset(("app", "browser", "windows", "local", "panel"))

def plan(text):
    parts = SPLIT.split(text.strip(), maxsplit=1)
    return [part.strip() for part in parts] if len(parts) == 2 and all(part.strip() for part in parts) else []

def allowed(steps):
    from .intent_router import classify
    from .guardian import is_sensitive
    return (len(steps) == 2 and all(not is_sensitive(step) for step in steps)
            and all(classify(step).kind in SAFE_KINDS for step in steps))

def run_steps(steps, execute_step):
    """Stop after first failure or emergency-stop; never run an unsafe step."""
    from .guardian import STOP
    if not allowed(steps):
        return "No ejecutaré una secuencia que incluya acciones desconocidas o sensibles."
    result = []
    for index, step in enumerate(steps, 1):
        if STOP.is_set():
            result.append("Secuencia detenida por seguridad.")
            break
        intent, answer = execute_step(step)
        result.append(f"Paso {index}: {answer}")
        # A launch request may succeed without proving the window appeared.
        failure = ("no pude", "no encontre", "no encontré", "requiere", "detenida", "no se", "error")
        if any(normalize(answer).startswith(prefix) for prefix in failure):
            result.append("Los pasos siguientes no se ejecutaron.")
            break
    return "\n".join(result)
