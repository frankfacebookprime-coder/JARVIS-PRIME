"""Read-only Windows diagnostics with no destructive operations."""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def system_summary():
    if sys.platform != "win32":
        return "El diagnóstico está disponible en Windows."
    drive = Path(os.environ.get("SystemDrive", "C:") + "\\")
    total, used, free = shutil.disk_usage(drive)
    gib = 1024 ** 3
    return ("Equipo: " + platform.node() +
            "\\nWindows: " + platform.platform() +
            "\\nAlmacenamiento libre: " + f"{free / gib:.1f}" + " GB de " +
            f"{total / gib:.1f}" + " GB. No se cambió ninguna configuración.")

def running_processes():
    if sys.platform != "win32":
        return "Esta función está disponible en Windows."
    result = subprocess.run(["tasklist.exe", "/FO", "CSV", "/NH"], capture_output=True,
                            text=True, timeout=15, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode != 0:
        return "No pude consultar los procesos de Windows."
    import csv, io
    rows = list(csv.reader(io.StringIO(result.stdout)))
    names = sorted({row[0] for row in rows if row})
    return "Procesos activos (nombres):\\n" + "\\n".join(names[:80])
