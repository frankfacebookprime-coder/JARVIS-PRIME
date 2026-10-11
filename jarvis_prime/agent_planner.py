"""Conservative two-step explicit planner; never interprets LLM output as executable actions."""
import re
from .windows_apps import normalize
def plan(text):
    value = normalize(text)
    # Only join independently allowlisted intents, never free-form chained actions.
    if not re.search(r"\s+y luego\s+|\s+despues\s+",value):
        return []
    return [part.strip() for part in re.split(r"\s+y luego\s+|\s+despues\s+", text, maxsplit=1, flags=re.I)]
def allowed(steps):
    from .intent_router import classify
    return bool(steps) and len(steps)==2 and all(classify(step).kind in ("app","browser","windows","local","panel") for step in steps)
