"""JARVIS PRIME floating orb: lightweight default UI with an optional control panel.

Only Tkinter/stdlib at import time. No permanent listening, no hidden microphone capture.
"""
import math
import queue
import threading
import tkinter as tk

from .app import Desktop
from .core import init_db, respond
from .voice import listen_once, speak

SIZE = 208
KEY = "#fc00fc"
BASE = "#071321"
CYAN = "#53e9ff"
BLUE = "#136c99"

def is_panel_command(value):
    """Explicit user intent only. Does not route regular conversation to UI actions."""
    from .windows_apps import normalize
    command = normalize(value)
    return command in {
        "abre panel", "abre el panel", "abrir panel", "abrir el panel",
        "muestra el panel", "mostrar panel", "abre el panel de jarvis",
        "jarvis abre el panel", "jarvis muestra el panel", "open panel",
        "abrir configuracion de jarvis",
    }

class Orb:
    def __init__(self):
        init_db()
        self.root = tk.Tk()
        self.root.title("JARVIS PRIME | Orb")
        self.root.geometry(f"{SIZE}x{SIZE}+40+220")
        self.root.overrideredirect(True)
        self.root.configure(bg=KEY)
        try:
            self.root.wm_attributes("-transparentcolor", KEY)
        except tk.TclError:
            self.root.configure(bg=BASE)
        self.root.wm_attributes("-topmost", True)
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=SIZE, height=SIZE, bg=KEY,
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.phase = 0.0
        self.mode = "ready"
        self.messages = queue.Queue()
        self.panel = None
        self.drag_start = None
        self.dragged = False
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Double-Button-1>", self.double_click)
        self.canvas.bind("<Button-3>", self.show_menu)
        self.menu = tk.Menu(self.root, tearoff=0, bg="#11273b", fg="#e6fbff")
        self.menu.add_command(label="Abrir panel", command=self.show_panel)
        self.menu.add_command(label="Hablar con JARVIS", command=self.listen)
        self.menu.add_command(label="Ocultar panel", command=self.hide_panel)
        self.menu.add_separator()
        self.menu.add_command(label="Salir de JARVIS", command=self.close)
        self.root.bind("<Escape>", lambda _: self.hide_panel())
        self.root.after(50, self.animate)
        self.root.after(90, self.poll)

    def start_drag(self, event):
        self.drag_start = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
        self.dragged = False

    def drag(self, event):
        if self.drag_start is None:
            return
        x0, y0, winx, winy = self.drag_start
        dx, dy = event.x_root - x0, event.y_root - y0
        if abs(dx) + abs(dy) > 7:
            self.dragged = True
            self.root.geometry(f"+{winx + dx}+{winy + dy}")

    def end_drag(self, event):
        if self.drag_start is not None and not self.dragged:
            self.toggle_panel()
        self.drag_start = None

    def double_click(self, event):
        self.listen()
        return "break"

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def show_panel(self):
        if self.panel is None or not self.panel.root.winfo_exists():
            window = tk.Toplevel(self.root)
            self.panel = Desktop(window)
            self.panel.root.protocol("WM_DELETE_WINDOW", self.hide_panel)
        self.panel.root.deiconify()
        self.panel.root.lift()
        self.panel.root.focus_force()

    def hide_panel(self):
        if self.panel is not None and self.panel.root.winfo_exists():
            self.panel.root.withdraw()

    def toggle_panel(self):
        if self.panel is not None and self.panel.root.winfo_exists() and self.panel.root.state() != "withdrawn":
            self.hide_panel()
        else:
            self.show_panel()

    def listen(self):
        if self.mode != "ready":
            return
        self.mode = "listening"
        self.run_worker(self.recognize_and_respond)

    def recognize_and_respond(self):
        try:
            phrase = listen_once()
            if not phrase:
                self.messages.put(("status", "No reconocí tu voz."))
                return
            self.messages.put(("heard", phrase))
            if is_panel_command(phrase):
                self.messages.put(("panel", None))
                answer = "Abriendo el panel, a sus órdenes."
            else:
                answer = respond(phrase)
            self.messages.put(("answered", answer))
            try:
                speak(answer)
            except Exception as exc:
                self.messages.put(("status", "Voz no disponible: " + str(exc)[:110]))
        except Exception as exc:
            self.messages.put(("status", "Error de micrófono: " + str(exc)[:140]))
        finally:
            self.messages.put(("ready", None))

    def run_worker(self, function):
        threading.Thread(target=function, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "panel":
                    self.show_panel()
                elif kind == "heard":
                    self.mode = "working"
                    if self.panel is not None and self.panel.root.winfo_exists():
                        self.panel.add("TÚ (VOZ)", value)
                elif kind == "answered":
                    if self.panel is not None and self.panel.root.winfo_exists():
                        self.panel.add("JARVIS", value)
                    self.mode = "speaking"
                elif kind == "ready":
                    self.mode = "ready"
                elif kind == "status":
                    if self.panel is not None and self.panel.root.winfo_exists():
                        self.panel.add("SISTEMA", value)
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(90, self.poll)

    def draw(self):
        c = self.canvas
        c.delete("all")
        x = SIZE / 2
        y = SIZE / 2
        t = self.phase
        # Transparent window with concentric glow, thin rotating rings and illuminated core.
        for radius, color, width in [(99, "#123043", 2), (94, "#175976", 2),
                                     (86, "#0b3349", 8), (75, "#155e7d", 2),
                                     (67, "#0c3448", 3), (56, "#2185a8", 2)]:
            c.create_oval(x-radius, y-radius, x+radius, y+radius,
                          outline=color, width=width)
        for radius, extent, speed, width, color in [
            (96, 42, 2.1, 3, "#59e5f8"), (87, 68, -1.2, 4, "#2b8cbd"),
            (76, 33, 3.4, 4, "#95faff"), (65, 65, -2.3, 3, "#2596c1"),
            (54, 55, 1.9, 2, "#5beeff"),
        ]:
            for offset in (0, 180):
                c.create_arc(x-radius, y-radius, x+radius, y+radius,
                             start=(t * speed + offset) % 360, extent=extent,
                             style="arc", outline=color, width=width)
        for i in range(32):
            angle = math.radians((i * 360 / 32) + t * .2)
            a, b = 81, 84 + (2 if i % 4 == 0 else 0)
            c.create_line(x+math.cos(angle)*a, y+math.sin(angle)*a,
                          x+math.cos(angle)*b, y+math.sin(angle)*b,
                          fill="#267b9d", width=2)
        halo = 40 + (2.8 * math.sin(t / 15))
        c.create_oval(x-halo, y-halo, x+halo, y+halo, fill="#0b3246",
                      outline="#59d8f0", width=2)
        c.create_oval(x-31, y-31, x+31, y+31, fill="#125773", outline="#65efff", width=2)
        c.create_text(x, y-4, text="J", fill="#e8fdff", font=("Segoe UI", 27, "bold"))
        status = {"ready":"EN LÍNEA", "listening":"ESCUCHANDO",
                  "working":"PROCESANDO", "speaking":"RESPONDIENDO"}[self.mode]
        c.create_text(x, y+23, text=status, fill="#92edfb",
                      font=("Consolas", 6, "bold"))

    def animate(self):
        self.phase = (self.phase + (4 if self.mode != "ready" else 1.8)) % 360
        self.draw()
        if self.root.winfo_exists():
            self.root.after(55, self.animate)

    def close(self):
        self.root.destroy()

def main():
    Orb().root.mainloop()

if __name__ == "__main__":
    main()
