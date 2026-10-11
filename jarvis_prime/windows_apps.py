"""Windows app discovery. Never run commands from the model as shell strings."""
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ALIASES = {
    "word": "Microsoft Word", "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint", "chrome": "Google Chrome",
    "edge": "Microsoft Edge", "paint": "Paint",
    "explorador": "Explorador de archivos", "explorador de archivos": "Explorador de archivos",
    "configuracion": "Configuración", "ajustes": "Configuración",
    "calculadora": "Calculadora", "bloc de notas": "Bloc de notas",
    "notepad": "Bloc de notas", "terminal": "Terminal",
}
BUILTINS = {
    "calculadora": ["calc.exe"], "bloc de notas": ["notepad.exe"],
    "explorador de archivos": ["explorer.exe"], "paint": ["mspaint.exe"],
    "configuracion": ["explorer.exe", "ms-settings:"],
}
BLOCK = ("cmd", "powershell", "terminal", "regedit", "registro", "administrador de tareas",
         "task manager", "símbolo del sistema", "simbolo del sistema", "wscript", "cscript")

def normalize(text):
    s = unicodedata.normalize("NFKD", text.casefold())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())

def clean_name(name):
    n = normalize(name)
    return normalize(ALIASES.get(n, name))

def extract_open(text):
    n = normalize(text)
    n = re.sub(r"^(?:oye |jarvis |hey jarvis |por favor |puedes |podrias |quiero que |necesito que )+", "", n)
    m = re.fullmatch(r"(?:abre|abrir|abreme|inicia|iniciar|ejecuta|ejecutar|lanza|pon|abre por favor) (?:la |el |los |las |programa |aplicacion |app )*(.{2,90})", n)
    if not m:
        return None
    name = re.sub(r" por favor$", "", m.group(1)).strip()
    return clean_name(name) if name else None

def discover_shortcuts():
    """Enumerate actual Start Menu shortcuts for both user and machine."""
    if sys.platform != "win32":
        return {}
    roots = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    ]
    found = {}
    for root in roots:
        if not root.is_dir():
            continue
        for extension in ("*.lnk", "*.url"):
            for path in root.rglob(extension):
                name = normalize(path.stem)
                if name:
                    found.setdefault(name, str(path))
    return found

def match_app(name, available=None):
    """Exact first; conservative unique partial match second."""
    normalized = clean_name(name)
    if not normalized or normalized in BLOCK or any(x in normalized for x in ("powershell", "terminal", "command prompt")):
        return None
    if normalized in BUILTINS:
        return ("builtin", BUILTINS[normalized])
    available = discover_shortcuts() if available is None else available
    if normalized in available:
        return ("shortcut", available[normalized])
    for desired in list(dict.fromkeys([normalize(ALIASES.get(normalized, normalized)), normalized] + [k for k,v in ALIASES.items() if normalize(v) == normalized])):
        candidates = [(title, path) for title, path in available.items()
                      if title == desired or title.startswith(desired + " ") or desired.startswith(title + " ")]
        if len(candidates) == 1:
            return ("shortcut", candidates[0][1])
    return None

def get_start_apps():
    """Lookup Windows UWP/registered Start apps, using fixed read-only command."""
    if sys.platform != "win32":
        return {}
    command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
               "Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=12,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode != 0 or not result.stdout.strip():
            return {}
        import json
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
        return {normalize(x["Name"]): x["AppID"] for x in data
                if isinstance(x, dict) and isinstance(x.get("Name"), str)
                and isinstance(x.get("AppID"), str) and x["AppID"]}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {}

def launch_app(name, available=None):
    if sys.platform != "win32":
        return "Abrir aplicaciones requiere Windows."
    result = match_app(name, available)
    if result is None and available is None and clean_name(name) not in BLOCK:
        entries = get_start_apps()
        normalized = clean_name(name)
        options = [(key, value) for key, value in entries.items()
                   if key == normalized or key.startswith(normalized + " ") or
                   any(normalize(v) == normalized and key == alias for alias, v in ALIASES.items())]
        if len(options) == 1:
            result = ("startapp", options[0][1])
    if result is None:
        return ("No encontré '" + name + "' en aplicaciones instaladas o accesos del menú Inicio. "
                "No ejecuté ningún comando. Puedes crear un acceso directo en el menú Inicio.")
    kind, target = result
    try:
        if kind == "builtin":
            subprocess.Popen(target, shell=False)
        elif kind == "startapp":
            subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + target], shell=False)
        else:
            os.startfile(target)
        return "Windows recibió la orden de abrir: " + name + "."
    except OSError as exc:
        return "No se pudo abrir " + name + ": " + str(exc)

def list_apps():
    found = discover_shortcuts()
    return sorted(set(found) | set(BUILTINS) | set(get_start_apps()))
