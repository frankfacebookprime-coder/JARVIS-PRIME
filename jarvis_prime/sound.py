"""Layered synthetic sci-fi audio cues, with no downloaded sound assets."""
import math
import struct
import sys
import threading
import wave
from io import BytesIO

CUES = {
    "activate": ((710, 1180, .17), (1180, 1430, .12)),
    "listen": ((540, 980, .22),),
    "wake": ((620, 1440, .24),),
    "clap": ((890, 1550, .22),),
    "working": ((400, 750, .21),),
    "done": ((780, 1320, .17), (1320, 920, .13)),
    "panel": ((380, 730, .19), (730, 1220, .2)),
    "dismiss": ((1000, 430, .18),),
    "error": ((400, 240, .23),),
}

def synthesize(event, sample_rate=16000):
    """Construct soft layered sine chirps with short envelopes, as a valid PCM WAV."""
    if event not in CUES:
        return b""
    frames = bytearray()
    for lo, hi, seconds in CUES[event]:
        count = max(1, int(sample_rate * seconds))
        for i in range(count):
            u = i / count
            fade = (min(1.,u/.16) * min(1.,(1.-u)/.25)) ** 1.25
            phase = 2 * math.pi * seconds * (lo*u + (hi-lo)*u*u/2)
            sound = .27 * fade * (math.sin(phase) + .28*math.sin(phase*2.01))
            frames.extend(struct.pack("<h", int(max(-1.,min(1.,sound))*32767)))
        frames.extend(b"\x00\x00" * int(sample_rate*.018))
    memory = BytesIO()
    with wave.open(memory, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(sample_rate)
        out.writeframes(bytes(frames))
    return memory.getvalue()

def play(event):
    if sys.platform != "win32" or event not in CUES:
        return
    try:
        from .config import load_settings
        if not load_settings().get("sounds", True):
            return
    except Exception:
        pass
    def worker():
        try:
            import winsound
            winsound.PlaySound(synthesize(event), winsound.SND_MEMORY | winsound.SND_NODEFAULT)
        except (OSError, RuntimeError, ValueError):
            pass
    threading.Thread(target=worker, daemon=True).start()
