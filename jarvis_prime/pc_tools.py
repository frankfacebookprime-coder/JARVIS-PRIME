"""Restricted explicit desktop actions. No arbitrary shell commands or AI tool execution."""
import re
import sys

def parse(text):
    from .windows_apps import normalize
    value = normalize(text)
    if value in ("copiar seleccion", "copia lo seleccionado", "pegar portapapeles", "seleccionar todo", "guardar documento"):
        return {"copiar seleccion":"ctrl+c", "copia lo seleccionado":"ctrl+c",
                "pegar portapapeles":"ctrl+v", "seleccionar todo":"ctrl+a", "guardar documento":"ctrl+s"}[value]
    return None
def execute(text):
    key = parse(text)
    if key is None:
        return None
    if sys.platform != "win32":
        return "Los atajos requieren Windows."
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = .1
        pyautogui.hotkey(*key.split("+"))
        return "Atajo enviado a la ventana activa: " + key
    except ImportError:
        return "Instala pyautogui para utilizar atajos seguros."
    except Exception as exc:
        return "No pude enviar el atajo: " + str(exc)[:140]
