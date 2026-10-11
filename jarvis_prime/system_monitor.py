"""Read-only telemetry, with standard-library fallback."""
import os
import shutil
import sys
from .config import FOLDER
def snapshot():
    result = ["Monitor JARVIS · solo lectura"]
    try:
        import psutil
        mem = psutil.virtual_memory()
        result.append("CPU: "+str(psutil.cpu_percent(interval=.1))+"%")
        result.append("RAM: "+str(mem.percent)+"%")
        result.append("Procesos: "+str(len(psutil.pids())))
    except ImportError:
        result.append("Instala psutil para ver CPU y RAM.")
    total, used, free = shutil.disk_usage(FOLDER.anchor or os.path.expanduser("~"))
    result.append("Disco libre: "+str(round(free/(1024**3),1))+" GB")
    return "\n".join(result)
