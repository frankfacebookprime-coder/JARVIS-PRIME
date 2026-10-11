"""OpenAI-compatible HTTP client. Never execute responses as commands."""
import json
import urllib.error
import urllib.parse
import urllib.request

def validate_url(url):
    parsed = urllib.parse.urlsplit(url.strip())
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("La URL de API no puede contener credenciales, consultas o fragmentos.")
    if parsed.scheme == "https" and parsed.hostname:
        return url.rstrip("/")
    if parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}:
        return url.rstrip("/")
    raise ValueError("Usa HTTPS o HTTP solo para localhost.")

def request_json(base_url, key, endpoint, payload=None, timeout=30):
    base = validate_url(base_url)
    if not key:
        raise ValueError("Falta la clave API.")
    headers = {"Authorization": "Bearer " + key, "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        base + endpoint, headers=headers,
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        method="GET" if payload is None else "POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("HTTP " + str(exc.code) + ": revisa API, clave, modelo o saldo.") from None
    except urllib.error.URLError as exc:
        raise RuntimeError("No se pudo conectar al servidor: " + str(exc.reason)[:130]) from None
    if not isinstance(result, dict):
        raise RuntimeError("El proveedor devolvió una respuesta inesperada.")
    return result

def fetch_models(base_url, key):
    result = request_json(base_url, key, "/models")
    models = result.get("data", [])
    if not isinstance(models, list):
        raise ValueError("El proveedor no devolvió una lista de modelos.")
    return sorted({m["id"] for m in models if isinstance(m, dict) and isinstance(m.get("id"), str)})

def complete(base_url, key, model, messages):
    if not model.strip():
        raise ValueError("Selecciona un modelo.")
    result = request_json(base_url, key, "/chat/completions",
                          {"model": model.strip(), "messages": messages}, timeout=60)
    choices = result.get("choices") or []
    if not choices:
        raise RuntimeError("El proveedor no devolvió una respuesta de chat.")
    value = choices[0].get("message", {}).get("content", "")
    return value if isinstance(value, str) else str(value)
