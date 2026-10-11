import os
import threading
import tkinter as tk
from pathlib import Path
from .core import init_db, respond

def load_env():
    path = Path(__file__).resolve().parents[1] / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                if key.strip() in ("JARVIS_API_KEY", "JARVIS_API_BASE", "JARVIS_MODEL"):
                    os.environ.setdefault(key.strip(), value.strip().strip('"'))

def main():
    load_env()
    init_db()
    root = tk.Tk()
    root.title("JARVIS PRIME · v0.1")
    root.geometry("900x650")
    root.minsize(600, 450)
    root.configure(bg="#090f1e")
    head = tk.Frame(root, bg="#111e33")
    head.pack(fill="x")
    tk.Label(head, text="◉  J A R V I S   P R I M E", bg="#111e33", fg="#60e7ff", font=("Segoe UI", 22, "bold")).pack(pady=(18, 4))
    tk.Label(head, text="WINDOWS  /  MEMORIA LOCAL  /  IA MULTIMODELO", bg="#111e33", fg="#8ca6c1", font=("Segoe UI", 9)).pack(pady=(0, 17))
    output = tk.Text(root, bg="#101b2e", fg="#e8f6ff", font=("Consolas", 12), wrap="word", relief="flat", padx=20, pady=16)
    output.pack(fill="both", expand=True, padx=16, pady=16)
    output.insert("end", "JARVIS PRIME · SISTEMA LISTO\n\nPrueba: abrir calculadora, recuerda comprar leche, qué recuerdas.\n\n")
    output.configure(state="disabled")
    bar = tk.Frame(root, bg="#090f1e")
    bar.pack(fill="x", padx=16, pady=(0, 16))
    entry = tk.Entry(bar, bg="#1b2c44", fg="white", insertbackground="white", font=("Segoe UI", 12), relief="flat")
    entry.pack(side="left", fill="x", expand=True, ipady=12)
    def add(who, value):
        output.configure(state="normal")
        output.insert("end", who + "\n" + value + "\n\n")
        output.see("end")
        output.configure(state="disabled")
    def send(event=None):
        message = entry.get().strip()
        if not message:
            return
        entry.delete(0, "end")
        add("TÚ", message)
        button.configure(state="disabled", text="ESPERA…")
        def work():
            try:
                answer = respond(message)
            except Exception as exc:
                answer = "Error: " + str(exc)
            def done():
                add("JARVIS", answer)
                button.configure(state="normal", text="ENVIAR")
            try:
                root.after(0, done)
            except RuntimeError:
                pass
        threading.Thread(target=work, daemon=True).start()
    button = tk.Button(bar, text="ENVIAR", command=send, bg="#20c4e5", fg="#06101a", relief="flat", font=("Segoe UI", 10, "bold"), padx=18)
    button.pack(side="right", fill="y", padx=(8, 0))
    entry.bind("<Return>", send)
    entry.focus_set()
    root.mainloop()

if __name__ == "__main__":
    main()
