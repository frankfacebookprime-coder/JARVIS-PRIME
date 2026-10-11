"""Browser actions. Exact intent routing; no model-generated command execution."""
import re
import webbrowser
from urllib.parse import quote_plus, urlparse
from .windows_apps import normalize

SITES = {
    "youtube": "https://www.youtube.com/",
    "google": "https://www.google.com/",
    "gmail": "https://mail.google.com/",
    "github": "https://github.com/",
    "whatsapp": "https://web.whatsapp.com/",
    "facebook": "https://www.facebook.com/",
    "instagram": "https://www.instagram.com/",
    "chatgpt": "https://chatgpt.com/",
}
BROWSER_NAMES = ("google", "chrome", "navegador", "internet", "edge", "browser")

def browser_action(text):
    """Return (description, URL) only for clear navigation/search requests."""
    n = normalize(text)
    n = re.sub(r"^(?:(?:hey |oye )?jarvis |por favor |puedes |podrias |quiero que |necesito que )+", "", n)
    n = re.sub(r" por favor$", "", n)
    # 'abre youtube en google', 'entra a youtube desde chrome', etc.
    match = re.fullmatch(
        r"(?:abre|abrir|abreme|entra a|entrar a|visita|ir a|ve a|pon|ingresa a|abre la pagina de|abre el sitio de)"
        r" (?:la pagina de |el sitio de |la web de )?"
        r"(youtube|google|gmail|github|whatsapp|facebook|instagram|chatgpt)"
        r"(?: (?:en|desde|con|usando) (?:el |la )?(?:google chrome|google|chrome|edge|navegador|internet|browser))?", n)
    if match:
        name = match.group(1)
        return ("Abriendo " + name, SITES[name])
    # Search using search engine only when explicitly asked.
    match = re.fullmatch(r"(?:busca|buscar|buscame|investiga|haz una busqueda de|busca en google|buscar en google)"
                         r" (?:en google )?(.{2,160}?)(?: en google)?", n)
    if match:
        query = match.group(1).strip()
        return ("Buscando en Google: " + query, "https://www.google.com/search?q=" + quote_plus(query))
    # Explicit HTTPS URL typed by user, no scripting or non-HTTPS schemes.
    url_match = re.fullmatch(r"(?:abre|abrir|visita|entra a)\s+(https://[^\s]+)", text.strip(), re.IGNORECASE)
    if url_match:
        url = url_match.group(1)
        parts = urlparse(url)
        if parts.scheme == "https" and parts.hostname and not parts.username and not parts.password:
            return ("Abriendo enlace", url)
    return None

def open_browser(text, opener=None):
    action = browser_action(text)
    if not action:
        return None
    title, url = action
    open_fn = opener or webbrowser.open
    try:
        if open_fn(url, new=2):
            return title + ". Se envió al navegador."
        return "No pude confirmar que el navegador aceptara el enlace: " + url
    except Exception as exc:
        return "Error abriendo navegador: " + str(exc)[:180]
