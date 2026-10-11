"""Layered synthetic sci-fi audio cues, with no downloaded sound assets."""
import math
import struct
import sys
import threading
import wave
from io import BytesIO

CUES = {
    "activate": ((440, 660, .11),),
    "listen": ((480, 715, .14),),
    "wake": ((500, 740, .13),),
    "clap": ((475, 705, .13),),
    "working": ((405, 570, .1),),
    "done": ((570, 790, .13),),
    "panel": ((370, 560, .14),),
    "dismiss": ((540, 380, .11),),
    "error": ((300, 250, .16),),
}
_SOUND_LOCK = threading.Lock()

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
            sound = .13 * fade * (math.sin(phase) + .11*math.sin(phase*1.51))
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
            with _SOUND_LOCK:
                winsound.PlaySound(synthesize(event), winsound.SND_MEMORY | winsound.SND_NODEFAULT)
        except (OSError, RuntimeError, ValueError):
            pass
    threading.Thread(target=worker, daemon=True).start()
