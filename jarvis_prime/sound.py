"""Synthesized short sci-fi feedback tones using native Windows winsound."""
import sys
import threading

TONES = {
    "activate": ((880, 55), (1320, 70)),
    "listen": ((1100, 75),),
    "working": ((600, 40), (790, 50)),
    "done": ((820, 55), (1220, 80)),
    "panel": ((440, 60), (660, 55), (990, 65)),
    "error": ((290, 110), (230, 120)),
}
def play(event):
    if sys.platform != "win32" or event not in TONES:
        return
    def worker():
        try:
            import winsound
            for frequency, duration in TONES[event]:
                winsound.Beep(frequency, duration)
        except (OSError, RuntimeError):
            pass
    threading.Thread(target=worker, daemon=True).start()
