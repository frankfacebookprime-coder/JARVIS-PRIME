"""Lightweight safe information-card renderer for Tkinter.

AI output is display-only data; never interpreted as commands or rich HTML.
"""
import re
import tkinter as tk

DARK = "#0b1828"
CARD = "#142a40"
CYAN = "#65e8f8"
TEXT = "#eaf8fe"
MUTED = "#aec7db"

def split_sections(answer):
    blocks = []
    paragraphs = re.split(r"\n\s*\n", str(answer).strip())
    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        if len(lines) > 1 and all(x.startswith(("- ", "* ", "• ", "1.", "2.", "3.", "4.", "5.")) for x in lines):
            blocks.append(("points", lines))
        else:
            blocks.append(("text", " ".join(lines)))
    return blocks[:22]

def render(parent, title, answer):
    for child in parent.winfo_children():
        child.destroy()
    head = tk.Frame(parent, bg=DARK, padx=24, pady=20)
    head.pack(fill="x", padx=12, pady=(10, 8))
    tk.Label(head, text="JARVIS PRIME  /  KNOWLEDGE", bg=DARK, fg=CYAN,
             anchor="w", font=("Segoe UI", 9, "bold")).pack(fill="x")
    tk.Label(head, text=title[:90], bg=DARK, fg=TEXT, wraplength=640,
             justify="left", anchor="w", font=("Segoe UI", 21, "bold")).pack(fill="x", pady=(8, 3))
    blocks = split_sections(answer)
    if not blocks:
        blocks = [("text", "No se recibió contenido.")]
    for i, (kind, value) in enumerate(blocks):
        box = tk.Frame(parent, bg=CARD, padx=20, pady=15)
        box.pack(fill="x", padx=12, pady=6)
        tk.Label(box, text=("PUNTOS CLAVE" if kind == "points" else ("RESUMEN" if i == 0 else f"DETALLE {i}")),
                 bg=CARD, fg=CYAN, anchor="w", font=("Segoe UI", 9, "bold")).pack(fill="x")
        text = "\n".join(value) if isinstance(value, list) else value
        tk.Label(box, text=text[:5500], bg=CARD, fg=TEXT, justify="left",
                 wraplength=640, anchor="w", font=("Segoe UI", 11)).pack(fill="x", pady=(7, 0))
