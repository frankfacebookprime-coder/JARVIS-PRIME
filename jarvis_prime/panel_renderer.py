"""Lightweight safe information-card renderer for Tkinter.

AI output is display-only data; never interpreted as commands or rich HTML.
"""
import re
import tkinter as tk

DARK = "#0b1828"
CARD = "#11263b"
CARD2 = "#172d46"
ACCENT = "#359fc4"
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
    """Reuses one information surface and keeps AI output strictly as plain text."""
    from datetime import datetime
    for child in parent.winfo_children():
        child.destroy()
    outer = tk.Frame(parent, bg=DARK, padx=18, pady=14)
    outer.pack(fill="both", expand=True)
    header = tk.Frame(outer, bg="#091d30", padx=20, pady=18,
                      highlightbackground="#276784", highlightthickness=1)
    header.pack(fill="x", pady=(0, 15))
    tk.Label(header, text="◈  JARVIS PRIME   /   INTELLIGENCE DISPLAY",
             bg="#091d30", fg=CYAN, font=("Consolas", 10, "bold"), anchor="w").pack(fill="x")
    tk.Label(header, text=datetime.now().strftime("SESIÓN  ·  %H:%M") + "   |   INFORMACIÓN GENERADA",
             bg="#091d30", fg=MUTED, font=("Consolas", 8), anchor="w").pack(fill="x", pady=(4,9))
    tk.Label(header, text=title[:110], bg="#091d30", fg=TEXT,
             wraplength=690, justify="left", anchor="w",
             font=("Segoe UI", 23, "bold")).pack(fill="x", pady=(2,9))
    tk.Frame(header, bg=CYAN, height=2).pack(fill="x", pady=(5,0))
    blocks = split_sections(answer) or [("text", "No se recibió contenido.")]
    tk.Label(outer, text=f"RESULTADOS ORGANIZADOS    /    {len(blocks):02d} MÓDULOS",
             bg=DARK, fg=MUTED, font=("Consolas", 9, "bold"), anchor="w").pack(fill="x", pady=(0,7))
    for i,(kind,value) in enumerate(blocks):
        bg = CARD if i % 2 == 0 else CARD2
        box = tk.Frame(outer, bg=bg, padx=18, pady=14, highlightbackground="#225577", highlightthickness=1)
        box.pack(fill="x", pady=5)
        top = tk.Frame(box, bg=bg)
        top.pack(fill="x")
        tk.Label(top, text=f"{i+1:02d}  /  " +
                 ("PUNTOS CLAVE" if kind == "points" else "SÍNTESIS" if i == 0 else "ANÁLISIS"),
                 bg=bg, fg=CYAN, anchor="w", font=("Consolas", 10, "bold")).pack(side="left")
        tk.Label(top, text="◆", bg=bg, fg=ACCENT).pack(side="right")
        tk.Frame(box, bg="#244b65", height=1).pack(fill="x", pady=9)
        text = "\n".join(value) if isinstance(value, list) else value
        tk.Label(box, text=text[:5500], bg=bg, fg=TEXT, justify="left",
                 wraplength=680, anchor="w", font=("Segoe UI", 11)).pack(fill="x")
    footer = tk.Frame(outer, bg=DARK, pady=12)
    footer.pack(fill="x")
    tk.Label(footer, text="JARVIS PRIME  //  FIN DE RESPUESTA   ·   CONTENIDO GENERADO POR IA",
             bg=DARK, fg=MUTED, font=("Consolas", 8)).pack(anchor="w")
