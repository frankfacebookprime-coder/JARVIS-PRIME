"""On-demand screenshot capture only; never starts background screen monitoring."""
from pathlib import Path
from datetime import datetime
import sys
from .config import FOLDER

def capture(confirmed=False):
    if not confirmed:
        return "La captura de pantalla requiere aprobación explícita desde la interfaz."
    if sys.platform != "win32":
        return "La captura está disponible en Windows."
    try:
        import pyautogui
        target = FOLDER / "captures"
        target.mkdir(parents=True, exist_ok=True)
        filename = target / ("captura-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")
        pyautogui.screenshot().save(filename)
        return "Captura guardada localmente: " + str(filename)
    except ImportError:
        return "Instala pyautogui para habilitar capturas."
    except Exception as exc:
        return "No pude realizar la captura: " + str(exc)[:140]
