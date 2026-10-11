"""Searchable local notes; private to the Windows user profile."""
import sqlite3
from contextlib import closing
from pathlib import Path
from .config import FOLDER

DATABASE = FOLDER / "second_brain.sqlite3"
def setup(path=None):
    path = Path(path) if path else DATABASE
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY, subject TEXT NOT NULL, detail TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP)")
        db.commit()
    return path
def save(subject, detail, path=None):
    target = setup(path)
    with closing(sqlite3.connect(target)) as db:
        cur = db.execute("INSERT INTO knowledge(subject,detail) VALUES (?,?)", (subject.strip()[:160], detail.strip()[:4000]))
        db.commit()
        return cur.lastrowid
def search(term, path=None, limit=10):
    target = setup(path)
    with closing(sqlite3.connect(target)) as db:
        rows = db.execute("SELECT id,subject,detail FROM knowledge WHERE subject LIKE ? OR detail LIKE ? ORDER BY id DESC LIMIT ?",
                          ("%"+term[:100]+"%", "%"+term[:100]+"%", min(max(limit,1),30))).fetchall()
    return rows
def delete(item_id, path=None):
    target = setup(path)
    with closing(sqlite3.connect(target)) as db:
        changed = db.execute("DELETE FROM knowledge WHERE id=?", (int(item_id),)).rowcount
        db.commit()
    return bool(changed)
def request(text):
    from .windows_apps import normalize
    command = normalize(text)
    if command.startswith("guarda en second brain "):
        return ("save", text[len("guarda en second brain "):].strip())
    if command.startswith("busca en second brain "):
        return ("search", text[len("busca en second brain "):].strip())
    return None
def handle(text):
    kind, content = request(text)
    if not content:
        return "Especifica qué deseas guardar o buscar."
    if kind == "save":
        item_id = save(content[:90], content)
        return f"Nota guardada en Second Brain, identificador {item_id}."
    rows = search(content)
    return "\n".join(f"#{ident} · {subject}: {detail[:250]}" for ident,subject,detail in rows) or "No encontré información relacionada."
