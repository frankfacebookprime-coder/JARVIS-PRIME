"""Local explicit skills registry. No dynamic untrusted plugin loading."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    confirmation_required: bool = False

REGISTRY = (
    Skill("apps", "Abrir aplicaciones permitidas"),
    Skill("browser", "Abrir sitios y búsquedas"),
    Skill("windows", "Listar y enfocar ventanas"),
    Skill("shortcuts", "Atajos básicos a la ventana activa"),
    Skill("second_brain", "Guardar y buscar información local"),
    Skill("diagnostics", "Resumen de funcionamiento y recursos"),
    Skill("vision", "Capturar pantalla bajo consentimiento", True),
)
def catalog():
    return "Habilidades disponibles:\n" + "\n".join("• "+s.name+": "+s.description for s in REGISTRY)
