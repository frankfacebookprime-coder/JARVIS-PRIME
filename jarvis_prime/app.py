"""JARVIS PRIME desktop UI, standard-library-only, safe UI-thread updates."""
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from .core import init_db, respond, execute
from .config import load_key, load_settings, save_key, save_settings
from .network import fetch_models, complete, validate_url
from .windows_apps import list_apps
from .voice import speak, listen_once
from .intent_router import information_title
from .panel_renderer import render
from .sound import play
from .vision import capture as capture_screen
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
    def __init__(self, window=None):
        load_legacy_env()
        init_db()
        self.root = window if window is not None else tk.Tk()
        self.root.title("JARVIS PRIME | COMMAND CENTER v1.2")
        self.root.geometry("1190x820")
        self.root.minsize(910, 660)
        self.root.configure(bg=BG)
        self.results = queue.Queue()
        self.busy = False
        self.models = []
        self.voice_enabled = tk.BooleanVar(value=True)
        self.hud_phase = 0
        self.settings = load_settings()
        self.knowledge_timeout_job = None
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
        self.root.configure(bg=BG)
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True)
        side = tk.Frame(shell, bg="#0e1b2b", width=220, padx=16, pady=24)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="◈  JARVIS", bg="#0e1b2b", fg="#65eaff",
                 font=("Segoe UI", 22, "bold"), anchor="w").pack(fill="x", pady=(2, 2))
        tk.Label(side, text="P R I M E   /   1.2", bg="#0e1b2b", fg="#7994ad",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", pady=(0, 35))
        def nav(title, call):
            b = tk.Button(side, text=title, anchor="w", command=call,
                          bg="#15293d", fg="#d5ebf7", activebackground="#1d4861",
                          activeforeground="white", relief="flat", bd=0, padx=13, pady=13,
                          cursor="hand2", font=("Segoe UI", 10))
            b.pack(fill="x", pady=5)
        nav("◉   Centro de control", lambda: self.entry.focus_set())
        nav("▤   Aplicaciones", self.show_apps)
        nav("◎   Nuevo chat", self.clear_chat)
        nav("⚙   Configurar IA", self.settings_window)
        nav("◈   Escuchar ahora", self.listen_voice)
        nav("♫   Configurar voz", self.voice_settings_window)
        nav("◈   Activación de voz", self.activation_settings_window)
        nav("◉   Cerrar información", self.dismiss_information)
        nav("◉   Diagnóstico", lambda: self.quick_command("diagnostico completo"))
        nav("▤   Monitor PC", lambda: self.quick_command("monitor del sistema"))
        nav("◉   Capturar pantalla", self.capture_with_consent)
        nav("■   Parar acciones", lambda: self.quick_command("deten jarvis"))
        tk.Frame(side, bg="#26425a", height=1).pack(fill="x", pady=(26, 16))
        tk.Label(side, text="ACCESOS RÁPIDOS", bg="#0e1b2b", fg="#7994ad",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
        for title, command in [("▶  YouTube", "abre youtube en google"),
                               ("◉  Google", "abre google"),
                               ("▣  Word", "abre word"),
                               ("◎  Chrome", "abre chrome")]:
            nav(title, lambda phrase=command: self.quick_command(phrase))
        tk.Label(side, text="Acciones locales verificables\nSin ejecutar código de la IA",
                 bg="#0e1b2b", fg="#718fa5", justify="left",
                 font=("Segoe UI", 9)).pack(side="bottom", anchor="w", pady=9)

        main = tk.Frame(shell, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        header = tk.Frame(main, bg=BG, padx=28, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="CENTRO DE COMANDO", bg=BG, fg=FG,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w", side="left")
        self.button(header, "CONFIGURAR IA  ⚙", self.settings_window, "#41cee9").pack(side="right")
        separator = tk.Frame(main, bg="#263d53", height=1)
        separator.pack(fill="x", padx=28)
        statusrow = tk.Frame(main, bg=BG, padx=28, pady=12)
        statusrow.pack(fill="x")
        self.status = self.label(statusrow, "", 10, ACCENT)
        self.status.pack(side="left")
        self.update_status()
        self.label(statusrow, "WINDOWS  •  VOZ  •  NAVEGADOR", 9, MUTED).pack(side="right")

        hero = tk.Frame(main, bg=PANEL, padx=18, pady=8)
        hero.pack(fill="x", padx=26, pady=(0, 12))
        leftinfo = tk.Frame(hero, bg=PANEL)
        leftinfo.pack(side="left", fill="both", expand=True)
        tk.Label(leftinfo, text="JARVIS ESTÁ LISTO", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", pady=(23, 8))
        tk.Label(leftinfo, text="Habla en español, abre páginas o\naplicaciones y consulta tu equipo.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 10), justify="left",
                 anchor="w").pack(fill="x")
        self.hud = tk.Canvas(hero, bg=PANEL, height=158, width=250, highlightthickness=0)
        self.hud.pack(side="right", padx=16)
        self.hud.bind("<Configure>", lambda event: self.draw_hud())

        controls = tk.Frame(main, bg=BG, padx=26)
        controls.pack(fill="x", pady=(0, 9))
        self.button(controls, "🎙  HABLAR AHORA", self.listen_voice, "#54dbe9").pack(side="left")
        tk.Checkbutton(controls, text="  Respuestas con voz", variable=self.voice_enabled,
                       bg=BG, fg=FG, selectcolor=PANEL2, activebackground=BG,
                       activeforeground=FG, font=("Segoe UI", 10)).pack(side="left", padx=15)
        self.voice_status = self.label(controls, "MICRÓFONO EN ESPERA", 9, MUTED)
        self.voice_status.pack(side="right")

        self.output = tk.Text(main, bg="#0e1c2d", fg=FG, insertbackground=FG,
                              font=("Segoe UI", 11), wrap="word", relief="flat",
                              padx=22, pady=15, state="disabled", spacing3=5)
        self.output.pack(fill="both", expand=True, padx=26, pady=(0, 12))
        self.knowledge_host = tk.Frame(main, bg="#0b1828")
        self.knowledge_canvas = tk.Canvas(self.knowledge_host, bg="#0b1828", highlightthickness=0)
        self.knowledge_scroll = ttk.Scrollbar(self.knowledge_host, orient="vertical", command=self.knowledge_canvas.yview)
        self.knowledge_content = tk.Frame(self.knowledge_canvas, bg="#0b1828")
        self.knowledge_frame_id = self.knowledge_canvas.create_window((0,0), window=self.knowledge_content, anchor="nw")
        self.knowledge_canvas.bind("<Configure>", lambda e: self.knowledge_canvas.itemconfigure(self.knowledge_frame_id, width=e.width))
        self.knowledge_content.bind("<Configure>", lambda e: self.knowledge_canvas.configure(scrollregion=self.knowledge_canvas.bbox("all")))
        self.knowledge_canvas.configure(yscrollcommand=self.knowledge_scroll.set)
        self.knowledge_scroll.pack(side="right", fill="y")
        self.knowledge_canvas.pack(side="left", fill="both", expand=True)
        self.info_visible = False
        self.add("SISTEMA", "Bienvenido a JARVIS PRIME. Prueba: puedes abrir YouTube en Google · abre Word · busca gatos en Google.")
        bottom = tk.Frame(main, bg=BG)
        self.bottom = bottom
        bottom.pack(fill="x", padx=26, pady=(0, 22))
        self.entry = tk.Entry(bottom, bg=PANEL2, fg=FG, insertbackground=FG,
                              relief="flat", font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=14)
        self.entry.bind("<Return>", self.send)
        self.send_button = self.button(bottom, "ENVIAR  ↗", self.send)
        self.send_button.pack(side="right", padx=(9, 0), fill="y")
        self.entry.focus_set()

    def quick_command(self, command):
        if self.busy:
            return
        self.entry.delete(0, "end")
        self.entry.insert(0, command)
        self.send()

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
        self.hud.create_text(x, y+65, text="JARVIS CORE • READY", fill=ACCENT, font=("Consolas", 9, "bold"))

    def animate_hud(self):
        self.hud_phase = (self.hud_phase + 2) % 360
        self.draw_hud()
        self.root.after(60, self.animate_hud)

    def dismiss_information(self):
        """Return to chat inside the same panel."""
        if self.knowledge_timeout_job is not None:
            try:
                self.root.after_cancel(self.knowledge_timeout_job)
            except tk.TclError:
                pass
            self.knowledge_timeout_job = None
        if getattr(self, "info_visible", False):
            self.knowledge_host.pack_forget()
            self.output.pack(fill="both", expand=True, padx=26, pady=(0, 12), before=self.bottom)
            self.info_visible = False
            play("dismiss")

    def schedule_knowledge_timeout(self):
        if self.knowledge_timeout_job is not None:
            self.root.after_cancel(self.knowledge_timeout_job)
            self.knowledge_timeout_job = None
        timeout = max(0, min(int(load_settings().get("info_panel_timeout", 0)), 3600))
        if timeout and self.info_visible:
            self.knowledge_timeout_job = self.root.after(timeout * 1000, self.dismiss_information)

    def show_information(self, question, answer):
        """Render one knowledge view embedded in the Command Center."""
        if not getattr(self, "info_visible", False):
            self.output.pack_forget()
            self.knowledge_host.pack(fill="both", expand=True, padx=26, pady=(0, 12), before=self.bottom)
            self.info_visible = True
        render(self.knowledge_content, information_title(question), answer)
        self.knowledge_canvas.yview_moveto(0)
        self.schedule_knowledge_timeout()
        self.root.deiconify()
        self.root.lift()
        play("panel")

    def show_apps(self):
        def done(value, error):
            self.add("APLICACIONES", "Error: " + error if error else
                     ("Instaladas en Inicio:\\n" + "\\n".join(value[:80]) if value else "Sin accesos detectados."))
        self.worker(list_apps, done)

    def listen_voice(self):
        self.voice_status.configure(text="● ESCUCHANDO...", fg=ACCENT)
        self.add("VOZ", "Escuchando una frase en español…")
        def done(value, error):
            self.voice_status.configure(text="MICRÓFONO EN ESPERA", fg=MUTED)
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
        self.dismiss_information()
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
        def job():
            return execute(msg)
        def routed(value, error):
            if error:
                done(None, error)
                return
            intent, answer = value
            done(answer, None)
            if intent.kind == "ai" and intent.visual:
                self.show_information(msg, answer)
            elif intent.kind == "dismiss_info":
                self.dismiss_information()
            elif intent.kind == "hide_panel":
                self.root.withdraw()
            if intent.kind == "vision":
                self.capture_with_consent()
        self.worker(job, routed)

    def capture_with_consent(self):
        """Consent is requested on the Tk main thread for each screenshot."""
        approved = messagebox.askyesno(
            "JARVIS | Capturar pantalla",
            "¿Autorizas guardar una captura de tu pantalla completa en tu carpeta local de JARVIS?\\n\\n"
            "Podría contener datos personales. No se enviará a ninguna IA automáticamente.",
            parent=self.root)
        if not approved:
            self.add("PRIVACIDAD", "Captura cancelada.")
            return
        self.worker(lambda: capture_screen(confirmed=True),
                    lambda result, error: self.add("PANTALLA", "Error: " + error if error else result))

    def activation_settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("JARVIS PRIME | ACTIVACIÓN")
        win.geometry("610x600")
        win.configure(bg=PANEL)
        prefs = load_settings()
        mode = tk.StringVar(value=prefs.get("activation_mode", "click"))
        word = tk.StringVar(value=prefs.get("wake_word", "jarvis"))
        path = tk.StringVar(value=prefs.get("vosk_model_path", ""))
        timeout = tk.IntVar(value=int(prefs.get("info_panel_timeout", 0)))
        sounds = tk.BooleanVar(value=bool(prefs.get("sounds", True)))
        self.label(win, "◈  ACTIVACIÓN INTELIGENTE", 17, ACCENT, True).pack(anchor="w", padx=26, pady=(20,8))
        self.label(win, "Elige cómo despertar JARVIS. Micrófono ambiental opcional.",
                   10, MUTED).pack(anchor="w", padx=26, pady=(0,16))
        self.label(win, "Modo", 10, ACCENT, True).pack(anchor="w", padx=26)
        ttk.Combobox(win, textvariable=mode, state="readonly",
                     values=["click", "wake", "clap", "both"]).pack(fill="x", padx=26, pady=(4,13))
        self.label(win, "Palabra clave (ejemplo: jarvis)", 10, ACCENT, True).pack(anchor="w", padx=26)
        tk.Entry(win, textvariable=word, bg=PANEL2, fg=FG,
                 insertbackground=FG).pack(fill="x", padx=26, pady=(4,13), ipady=5)
        self.label(win, "Carpeta de modelo Vosk español (para wake / both)",
                   10, ACCENT, True).pack(anchor="w", padx=26)
        tk.Entry(win, textvariable=path, bg=PANEL2, fg=FG,
                 insertbackground=FG).pack(fill="x", padx=26, pady=(4,13), ipady=5)
        self.label(win, "Panel informativo: cerrar después de segundos (0 = mantener)",
                   10, ACCENT, True).pack(anchor="w", padx=26)
        tk.Scale(win, from_=0, to=120, resolution=5, variable=timeout, orient="horizontal",
                 bg=PANEL, fg=FG, highlightthickness=0).pack(fill="x", padx=26)
        tk.Checkbutton(win, text="  Efectos futuristas", variable=sounds,
                       bg=PANEL, fg=FG, selectcolor=PANEL2,
                       activebackground=PANEL, activeforeground=FG).pack(anchor="w", padx=26, pady=12)
        note = ("CLICK: solo clic.  WAKE: palabra clave.  CLAP: dos aplausos.  BOTH: ambos.\\n"
                "El detector de palabra usa Vosk local. El audio ambiental no se guarda.\\n"
                "En cualquier modo, un clic sigue activando JARVIS.")
        self.label(win, note, 9, MUTED, wraplength=550, justify="left").pack(anchor="w", padx=26)
        def save_activation():
            from .ambient_activation import MODES, clean_phrase
            from pathlib import Path
            selected = mode.get()
            wake = clean_phrase(word.get())
            if selected not in MODES or not wake or len(wake) > 35:
                messagebox.showerror("Activación", "Modo o palabra clave incorrectos.", parent=win)
                return
            if selected in ("wake", "both") and not Path(path.get()).expanduser().is_dir():
                messagebox.showerror("Activación",
                    "Selecciona una carpeta real de modelo Vosk español antes de activar la palabra clave.",
                    parent=win)
                return
            updated = load_settings()
            updated.update(activation_mode=selected, wake_word=wake,
                           vosk_model_path=path.get().strip(), info_panel_timeout=timeout.get(),
                           sounds=sounds.get())
            save_settings(updated)
            self.schedule_knowledge_timeout() if self.info_visible else None
            win.destroy()
            self.add("SISTEMA", "Modo de activación guardado: " + selected)
        self.button(win, "APLICAR ACTIVACIÓN", save_activation).pack(fill="x", padx=26, pady=(13,0))

    def voice_settings_window(self):
        win = tk.Toplevel(self.root)
        win.title("JARVIS PRIME | Motor de voz")
        win.geometry("520x560")
        win.configure(bg=PANEL)
        saved = load_settings()
        engine = tk.StringVar(value=saved.get("tts_engine", "auto"))
        voice_id = tk.StringVar(value=saved.get("tts_voice", "es-MX-DaliaNeural"))
        rate = tk.IntVar(value=int(saved.get("tts_rate", 0)))
        maximum = tk.IntVar(value=int(saved.get("voice_max_chars", 750)))
        pause = tk.DoubleVar(value=float(saved.get("pause_threshold", 1.0)))
        self.label(win, "MOTOR DE VOZ", 16, ACCENT, True).pack(anchor="w", padx=25, pady=15)
        self.label(win, "Motor", 10, MUTED).pack(anchor="w", padx=25)
        ttk.Combobox(win, textvariable=engine, state="readonly", values=["auto","edge","piper","sapi"]).pack(fill="x", padx=25)
        self.label(win, "Voz Edge TTS", 10, MUTED).pack(anchor="w", padx=25, pady=(12,0))
        ttk.Combobox(win, textvariable=voice_id, values=["es-MX-DaliaNeural","es-MX-JorgeNeural","es-ES-ElviraNeural","es-ES-AlvaroNeural"]).pack(fill="x", padx=25)
        self.label(win, "Velocidad (-50 a +50%)", 10, MUTED).pack(anchor="w", padx=25, pady=(12,0))
        tk.Scale(win, from_=-50, to=50, variable=rate, orient="horizontal", bg=PANEL, fg=FG, highlightthickness=0).pack(fill="x", padx=25)
        self.label(win, "Máximo de caracteres hablados", 10, MUTED).pack(anchor="w", padx=25, pady=(12,0))
        tk.Scale(win, from_=100, to=1400, resolution=50, variable=maximum, orient="horizontal", bg=PANEL, fg=FG, highlightthickness=0).pack(fill="x", padx=25)
        self.label(win, "Pausa para detectar fin de frase (segundos)", 10, MUTED).pack(anchor="w", padx=25, pady=(12,0))
        tk.Scale(win, from_=0.5, to=2.5, resolution=0.1, variable=pause,
                 orient="horizontal", bg=PANEL, fg=FG, highlightthickness=0).pack(fill="x", padx=25)
        def save_voice():
            values = load_settings()
            values.update(tts_engine=engine.get(), tts_voice=voice_id.get().strip(),
                          tts_rate=rate.get(), voice_max_chars=maximum.get(),
                          pause_threshold=pause.get())
            save_settings(values)
            win.destroy()
            self.add("SISTEMA", "Preferencias de voz guardadas.")
        self.button(win, "GUARDAR VOZ", save_voice).pack(padx=25, pady=15, fill="x")

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
                save_settings({**load_settings(), "provider": provider.get(), "base_url": endpoint, "model": chosen})
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
