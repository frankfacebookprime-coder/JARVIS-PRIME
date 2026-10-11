"""Safe window discovery and foreground focus with optional pywinauto.

Never clicks buttons, types passwords, runs arbitrary commands or closes processes.
"""
import re
import sys

def window_request(text):
    from .windows_apps import normalize
    value = normalize(text)
    if value in ("que ventanas tengo abiertas", "muestra ventanas abiertas", "lista ventanas abiertas",
                 "ver ventanas abiertas", "que ventanas estan abiertas"):
        return ("list", "")
    match = re.fullmatch(r"(?:cambia a|enfoca|activa|trae al frente|muestra la ventana de) (?:la ventana de )?(.{2,80})", value)
    if match:
        return ("focus", match.group(1).strip())
    return None

def visible_windows():
    if sys.platform != "win32":
        return []
    try:
        from pywinauto import Desktop
        return [(w.window_text().strip(), w) for w in Desktop(backend="uia").windows(visible_only=True)
                if w.window_text().strip()]
    except (ImportError, OSError, RuntimeError):
        return []

def handle_windows(text):
    action = window_request(text)
    if action is None:
        return None
    if sys.platform != "win32":
        return "Las ventanas solo se pueden controlar en Windows."
    try:
        from pywinauto import Desktop
    except ImportError:
        return "Instala pywinauto para consultar y enfocar ventanas."
    windows = visible_windows()
    if action[0] == "list":
        titles = sorted({name for name, _ in windows})
        return "Ventanas visibles:\n" + "\n".join("• " + title[:110] for title in titles[:35]) if titles else "No encontré ventanas visibles."
    query = action[1]
    from .windows_apps import normalize
    matches = [(name, window) for name, window in windows if query in normalize(name)]
    if not matches:
        return "No encontré una ventana abierta con ese nombre."
    if len(matches) > 1:
        return "Hay varias ventanas posibles; especifica el título:\n" + "\n".join(name for name, _ in matches[:8])
    name, window = matches[0]
    try:
        window.set_focus()
        return "Ventana enfocada: " + name[:120]
    except (OSError, RuntimeError, Exception) as exc:
        return "No pude enfocar la ventana: " + str(exc)[:140]
