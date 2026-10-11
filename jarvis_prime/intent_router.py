"""Conservative command router. No arbitrary system commands from LLM output."""
import re
from dataclasses import dataclass
from .windows_apps import extract_open, normalize
from .browser import browser_action
from .window_control import window_request

@dataclass(frozen=True)
class Intent:
    kind: str
    visual: bool = False

def classify(text):
    n = normalize(text)
    if not n:
        return Intent("empty")
    if n in {"abre el panel", "abre panel", "jarvis abre el panel", "muestra el panel",
             "jarvis muestra el panel", "open panel", "abrir panel", "abrir el panel"}:
        return Intent("panel")
    if n.startswith(("recuerda ",)) or n in ("que recuerdas", "ver memoria",
            "estado de mi computadora", "estado del sistema", "informacion de mi pc",
            "diagnostico basico", "ver procesos", "que procesos estan abiertos",
            "mostrar procesos", "muestrame aplicaciones", "lista de aplicaciones",
            "que aplicaciones tengo", "ver aplicaciones"):
        return Intent("local")
    # Important: "investiga" and "explícame" are information requests,
    # not automatic Google/browser actions.
    if re.match(r"^(?:jarvis )?(?:investiga|explica|explicame|dime|que es|como funciona|cuales son|resume|resumeme|hazme un resumen)\b", n):
        return Intent("ai", True)
    if window_request(text) is not None:
        return Intent("windows")
    if browser_action(text) is not None:
        return Intent("browser")
    if extract_open(text) is not None:
        return Intent("app")
    return Intent("ai", True)

def information_title(prompt):
    n = prompt.strip()
    n = re.sub(r"^(?:jarvis[, ]+)?(?:investiga|explica|explícame|qué es|que es|dime sobre|háblame de|hablame de)\s+", "", n, flags=re.I)
    n = re.sub(r"\s+(?:y )?(?:muéstramelo|muestramelo|muéstrame|muestrame)(?: en el panel)?[.?!]*$", "", n, flags=re.I)
    return (n[:90].strip(" ?.!") or "Resultado de JARVIS").capitalize()
