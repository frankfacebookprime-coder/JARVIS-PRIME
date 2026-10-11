"""JARVIS PRIME desktop UI, standard-library-only, safe UI-thread updates."""
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from .core import init_db, respond
from .config import load_key, load_settings, save_key, save_settings
from .network import fetch_models, complete, validate_url
from .windows_apps import list_apps
from .voice import speak, listen_once
import math

BG = "#080f1d"
PANEL = "#101e31"
PANEL2 = "#162b42"
FG = "#e9f7ff"
ACCENT = "#49d9f2"
MUTED = "#9ab5ca"
PRESETS = {
    "OpenRouter": "https://openrouter.ai/api/v1",
    "OpenAI": "https://api.openai.com/v1",
    "DeepSeek": "https://api.deepseek.com",
    "Personalizado / OmniRouter": "",
}

def load_legacy_env():
    env = Path(__file__).resolve().parents[1] / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, val = line.split("=", 1)
                if key.strip() in {"JARVIS_API_KEY", "JARVIS_API_BASE", "JARVIS_MODEL"}:
                    os.environ.setdefault(key.strip(), val.strip().strip('"'))

class Desktop:
    def __init__(self):
        load_legacy_env()
        init_db()
        self.root = tk.Tk()
        self.root.title("JARVIS PRIME | Control Center v0.3")
        self.root.geometry("1160x760")
        self.root.minsize(740, 530)
        self.root.configure(bg=BG)
        self.results = queue.Queue()
        self.busy = False
        self.models = []
        self.voice_enabled = tk.BooleanVar(value=False)
        self.hud_phase = 0
        self.settings = load_settings()
        self.build()
        self.root.after(90, self.drain)
        self.root.after(60, self.animate_hud)

    def label(self, parent, text, size=10, fg=FG, bold=False, **opts):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=fg,
                        font=("Segoe UI", size, "bold" if bold else "normal"), **opts)

    def button(self, parent, text, command, color=ACCENT):
        return tk.Button(parent, text=text, command=command, bg=color, fg=BG,
                         activebackground="#91f2ff", relief="flat",
                         font=("Segoe UI", 10, "bold"), padx=15, pady=8, cursor="hand2")

    def build(self):
        top = tk.Frame(self.root, bg=PANEL, padx=22, pady=18)
        top.pack(fill="x")
        tk.Label(top, text="◉  JARVIS PRIME", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 23, "bold")).pack(side="left")
        self.button(top, "⚙  CONFIGURAR IA", self.settings_window).pack(side="right")
        self.label(self.root, "CENTRO DE CONTROL  /  ACCIONES WINDOWS  /  VOZ  /  INTELIGENCIA", 10, MUTED).pack(anchor="w", padx=25, pady=(14, 8))
        self.hud = tk.Canvas(self.root, bg=BG, height=140, highlightthickness=0)
        self.hud.pack(fill="x", padx=25)
        self.hud.bind("<Configure>", lambda event: self.draw_hud())
        statusbar = tk.Frame(self.root, bg=BG)
        statusbar.pack(fill="x", padx=24)
        self.status = self.label(statusbar, "", 10, ACCENT)
        self.status.pack(side="left")
        self.update_status()
        self.button(statusbar, "NUEVO CHAT", self.clear_chat, PANEL2).pack(side="right")
        self.button(statusbar, "APLICACIONES", self.show_apps, PANEL2).pack(side="right", padx=8)
        self.button(statusbar, "🎙  HABLAR", self.listen_voice, PANEL2).pack(side="right", padx=8)
        tk.Checkbutton(statusbar, text="Leer respuestas", variable=self.voice_enabled,
                       bg=BG, fg=MUTED, selectcolor=PANEL2, activebackground=BG).pack(side="right", padx=8)
        self.output = tk.Text(self.root, bg=PANEL, fg=FG, insertbackground=FG,
                              font=("Segoe UI", 12), wrap="word", relief="flat",
                              padx=24, pady=20, state="disabled", spacing3=8)
        self.output.pack(fill="both", expand=True, padx=24, pady=16)
        self.add("SISTEMA", "JARVIS PRIME 0.3 preparado. Prueba: abre Word · abre Chrome · abre calculadora · qué aplicaciones tengo.\\nUsa HABLAR para dictar una orden (requiere activar las dependencias de voz).")
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill="x", padx=24, pady=(0, 24))
        self.entry = tk.Entry(bottom, bg=PANEL2, fg=FG, insertbackground=FG,
                              relief="flat", font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=14)
        self.entry.bind("<Return>", self.send)
        self.send_button = self.button(bottom, "ENVIAR  ↗", self.send)
        self.send_button.pack(side="right", padx=(9, 0), fill="y")
        self.entry.focus_set()

    def draw_hud(self):
        self.hud.delete("all")
        w = self.hud.winfo_width()
        if w < 200:
            w = 1000
        x, y = w / 2, 68
        phase = self.hud_phase
        for radius, stroke, speed in [(55, "#1d5670", 0.9), (44, "#2b9ab8", -1.3), (30, "#50dff5", 2.1)]:
            self.hud.create_oval(x-radius, y-radius, x+radius, y+radius, outline=stroke, width=2)
            angle = (phase * speed) % 360
            self.hud.create_arc(x-radius, y-radius, x+radius, y+radius,
                                start=angle, extent=75, style="arc", outline="#a2f8ff", width=3)
        self.hud.create_text(x, y, text="J", fill="#d4faff", font=("Segoe UI", 27, "bold"))
        self.hud.create_text(x-135, y, text="SISTEMA ACTIVO", fill=ACCENT, font=("Consolas", 10, "bold"))
        self.hud.create_text(x+145, y, text="CONTROL WINDOWS", fill=ACCENT, font=("Consolas", 10, "bold"))

    def animate_hud(self):
        self.hud_phase = (self.hud_phase + 2) % 360
        self.draw_hud()
        self.root.after(60, self.animate_hud)

    def show_apps(self):
        def done(value, error):
            self.add("APLICACIONES", "Error: " + error if error else
                     ("Instaladas en Inicio:\\n" + "\\n".join(value[:80]) if value else "Sin accesos detectados."))
        self.worker(list_apps, done)

    def listen_voice(self):
        self.add("VOZ", "Escuchando una frase en español…")
        def done(value, error):
            if error:
                self.add("VOZ", "No pude escuchar: " + error)
            elif value:
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
                self.send()
            else:
                self.add("VOZ", "No pude comprender la frase.")
        self.worker(listen_once, done)

    def add(self, who, message):
        self.output.configure(state="normal")
        self.output.insert("end", who + "\n", "name")
        self.output.insert("end", str(message) + "\n\n")
        self.output.tag_configure("name", foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear_chat(self):
        if self.busy:
            return
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.add("SISTEMA", "Nuevo chat. Las notas de memoria se conservan.")

    def update_status(self):
        s = load_settings()
        self.status.configure(text="●  " + (s["provider"] + " · " + s["model"] if s.get("model") else "MODO LOCAL · IA SIN CONFIGURAR"))

    def worker(self, func, callback):
        def run():
            try:
                value = func()
                self.results.put((callback, value, None))
            except Exception as exc:
                self.results.put((callback, None, str(exc)[:320]))
        threading.Thread(target=run, daemon=True).start()

    def drain(self):
        try:
            while True:
                callback, value, err = self.results.get_nowait()
                callback(value, err)
        except queue.Empty:
            pass
        self.root.after(90, self.drain)

    def send(self, event=None):
        msg = self.entry.get().strip()
        if not msg or self.busy:
            return
        self.entry.delete(0, "end")
        self.add("TÚ", msg)
        self.busy = True
        self.send_button.configure(state="disabled", text="PENSANDO…")
        def done(answer, error):
            message = "Error: " + error if error else answer
            self.add("JARVIS", message)
            if self.voice_enabled.get() and not error and answer:
                self.worker(lambda: speak(str(answer)), lambda value, issue: self.add("VOZ", "Error de voz: " + issue) if issue else None)
            self.busy = False
            self.send_button.configure(state="normal", text="ENVIAR  ↗")
        self.worker(lambda: respond(msg), done)

    def settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("JARVIS PRIME | Conectar IA")
        win.geometry("650x620")
        win.minsize(550, 570)
        win.configure(bg=PANEL)
        win.transient(self.root)
        settings = load_settings()
        provider = tk.StringVar(value=settings["provider"])
        url = tk.StringVar(value=settings["base_url"])
        model = tk.StringVar(value=settings["model"])
        key = tk.StringVar(value="")
        show = tk.BooleanVar(value=False)
        self.label(win, "CONECTAR TU INTELIGENCIA ARTIFICIAL", 16, ACCENT, True).pack(anchor="w", padx=26, pady=(22, 12))
        self.label(win, "Proveedor", 10, MUTED).pack(anchor="w", padx=26)
        preset = ttk.Combobox(win, textvariable=provider, values=list(PRESETS), state="readonly")
        preset.pack(fill="x", padx=26, pady=(4, 11), ipady=5)
        self.label(win, "URL base (OpenAI-compatible)", 10, MUTED).pack(anchor="w", padx=26)
        tk.Entry(win, textvariable=url, font=("Segoe UI", 11), bg=PANEL2, fg=FG, insertbackground=FG, relief="flat").pack(fill="x", padx=26, pady=(4, 11), ipady=9)
        self.label(win, "Clave API (deja en blanco para conservar la guardada)", 10, MUTED).pack(anchor="w", padx=26)
        row = tk.Frame(win, bg=PANEL)
        row.pack(fill="x", padx=26, pady=(4, 11))
        key_entry = tk.Entry(row, textvariable=key, show="•", font=("Segoe UI", 11), bg=PANEL2, fg=FG, insertbackground=FG, relief="flat")
        key_entry.pack(side="left", fill="x", expand=True, ipady=9)
        def toggle():
            key_entry.configure(show="" if show.get() else "•")
        tk.Checkbutton(row, text="Mostrar", variable=show, command=toggle, bg=PANEL, fg=FG,
                       selectcolor=PANEL2, activebackground=PANEL).pack(side="right")
        self.label(win, "Modelo (selecciona o escribe el ID exacto)", 10, MUTED).pack(anchor="w", padx=26)
        selector = ttk.Combobox(win, textvariable=model, values=[], state="normal")
        selector.pack(fill="x", padx=26, pady=(4, 12), ipady=5)
        info = tk.StringVar(value="Tu clave se protege con Windows DPAPI en tu perfil local.")
        self.label(win, "La detección de modelos depende del proveedor.", 9, MUTED).pack(anchor="w", padx=26)
        self.label(win, "", 9, ACCENT, wraplength=580, textvariable=info).pack(anchor="w", padx=26, pady=12)
        def changed(*_):
            chosen = provider.get()
            if PRESETS.get(chosen):
                url.set(PRESETS[chosen])
        preset.bind("<<ComboboxSelected>>", changed)
        def credentials():
            candidate = key.get().strip()
            return candidate or load_key()
        def discover():
            try:
                endpoint = validate_url(url.get())
                secret = credentials()
            except Exception as exc:
                info.set(str(exc))
                return
            info.set("Consultando modelos disponibles…")
            def done(values, error):
                if not win.winfo_exists():
                    return
                if error:
                    info.set("No se pudo detectar: " + error + " Puedes escribir el modelo manualmente.")
                else:
                    selector.configure(values=values)
                    info.set(str(len(values)) + " modelos encontrados. Selecciona uno.")
                    if values and model.get() not in values:
                        model.set(values[0])
            self.worker(lambda: fetch_models(endpoint, secret), done)
        def test():
            try:
                endpoint = validate_url(url.get())
                secret = credentials()
                chosen = model.get().strip()
                if not chosen:
                    raise ValueError("Elige un modelo.")
            except Exception as exc:
                info.set(str(exc))
                return
            info.set("Probando respuesta real del modelo…")
            def done(answer, error):
                if win.winfo_exists():
                    info.set("Error: " + error if error else "Conexión correcta ✓ Respuesta: " + answer[:180])
            self.worker(lambda: complete(endpoint, secret, chosen, [{"role": "user", "content": "Responde únicamente OK"}]), done)
        def save():
            try:
                endpoint = validate_url(url.get())
                chosen = model.get().strip()
                if not chosen:
                    raise ValueError("Elige un modelo.")
                if key.get().strip():
                    save_key(key.get().strip())
                if not load_key():
                    raise ValueError("Introduce tu API Key.")
                save_settings({"provider": provider.get(), "base_url": endpoint, "model": chosen})
            except Exception as exc:
                messagebox.showerror("Configuración", str(exc), parent=win)
                return
            self.update_status()
            win.destroy()
            self.add("SISTEMA", "Proveedor guardado: " + provider.get() + " · " + chosen)
        actions = tk.Frame(win, bg=PANEL)
        actions.pack(fill="x", padx=26, pady=(12, 8))
        self.button(actions, "BUSCAR MODELOS", discover, "#8daac4").pack(side="left", padx=(0, 8))
        self.button(actions, "PROBAR API", test, "#8daac4").pack(side="left")
        self.button(win, "GUARDAR Y USAR ESTA IA", save).pack(fill="x", padx=26, pady=12)
        win.bind("<Escape>", lambda event: win.destroy())

def main():
    Desktop().root.mainloop()

if __name__ == "__main__":
    main()
