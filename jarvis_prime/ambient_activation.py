"""Opt-in background activation. Local Vosk wake phrase and double-clap detector.

No audio is saved or sent over the network by the ambient detector.
Requires sounddevice and numpy; Vosk plus a downloaded local model for hotword.
"""
import collections
import math
import queue
import re
import threading
import time

MODES = ("click", "wake", "clap", "both")
DEFAULT_WORD = "jarvis"
SAMPLE_RATE = 16000
_VOSK_MODELS = {}
_VOSK_LOCK = threading.Lock()

def clean_phrase(value):
    import unicodedata
    value = "".join(ch for ch in unicodedata.normalize("NFKD", str(value).casefold())
                    if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[a-z0-9]+", value))

def wake_detected(recognized, phrase=DEFAULT_WORD):
    words = clean_phrase(recognized).split()
    target = clean_phrase(phrase).split()
    return bool(target) and any(words[i:i+len(target)] == target
                                for i in range(len(words)-len(target)+1))

class ClapDetector:
    """Amplitude/impulse detector with inter-clap timing and refractory window."""
    def __init__(self, min_gap=.18, max_gap=.8, cooldown=2.5):
        self.min_gap = min_gap
        self.max_gap = max_gap
        self.cooldown = cooldown
        self.first = None
        self.last_hit = -1000.0
        self.last_trigger = -1000.0
        self.noise = .012
        self.armed = True
        self.quiet_frames = 0

    def feed(self, rms, peak, now):
        rms = max(0., float(rms))
        peak = max(0., float(peak))
        # Adapt only to ambient levels below the impulsive threshold.
        threshold = max(.08, self.noise * 4.5)
        impulse = peak >= threshold and rms >= max(.025, self.noise * 1.8)
        if not impulse:
            self.quiet_frames += 1
            if self.quiet_frames >= 2:
                self.armed = True
            self.noise = max(.002, min(.075, self.noise * .985 + min(rms, .075) * .015))
            if self.first is not None and now - self.first > self.max_gap:
                self.first = None
            return False
        if not self.armed or now-self.last_hit < .12 or now-self.last_trigger < self.cooldown:
            return False
        self.armed = False
        self.quiet_frames = 0
        self.last_hit = now
        if self.first is not None and self.min_gap <= now-self.first <= self.max_gap:
            self.first = None
            self.last_trigger = now
            return True
        self.first = now
        return False

class AmbientActivation:
    """One audio stream shared by both detectors; never runs unless enabled."""
    def __init__(self, on_trigger, on_status=None):
        self.on_trigger = on_trigger
        self.on_status = on_status or (lambda message: None)
        self.stop_event = threading.Event()
        self.thread = None
        self.retry_after = 0.0

    def start(self, mode, word="jarvis", model_path=""):
        self.stop()
        if mode not in MODES or mode == "click":
            return
        self.stop_event = threading.Event()
        self.retry_after = 0.0
        self.thread = threading.Thread(target=self._run,
            args=(mode, word, model_path, self.stop_event), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        # Never block Tk while the microphone is being released.

    def _run(self, mode, word, model_path, stop):
        try:
            import sounddevice as sd
            import numpy as np
            recognize = None
            if mode in ("wake", "both"):
                from pathlib import Path
                from vosk import Model, KaldiRecognizer, SetLogLevel
                path = Path(model_path).expanduser()
                if not path.is_dir():
                    raise RuntimeError("Configura una carpeta de modelo Vosk en Activación de voz.")
                SetLogLevel(-1)
                with _VOSK_LOCK:
                    if str(path.resolve()) not in _VOSK_MODELS:
                        _VOSK_MODELS.clear()
                        _VOSK_MODELS[str(path.resolve())] = Model(str(path))
                    model = _VOSK_MODELS[str(path.resolve())]
                recognize = KaldiRecognizer(model, SAMPLE_RATE)
            detector = ClapDetector()
            chunks = queue.Queue(maxsize=15)
            def callback(indata, frames, timing, status):
                if stop.is_set():
                    return
                try:
                    chunks.put_nowait(bytes(indata))
                except queue.Full:
                    pass
            triggered = None
            with sd.RawInputStream(samplerate=SAMPLE_RATE, channels=1,
                                   dtype="int16", blocksize=1024, callback=callback):
                self.on_status("Detección ambiental activa (" + mode + ")")
                import json
                while not stop.is_set():
                    try:
                        raw = chunks.get(timeout=.2)
                    except queue.Empty:
                        continue
                    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)/32768.
                    rms = float(np.sqrt(np.mean(data*data)))
                    peak = float(np.max(np.abs(data)))
                    if mode in ("clap", "both") and detector.feed(rms, peak, time.monotonic()):
                        triggered = "clap"
                        break
                    if recognize:
                        completed = recognize.AcceptWaveform(raw)
                        item = json.loads(recognize.Result() if completed else recognize.PartialResult())
                        transcript = item.get("text" if completed else "partial", "")
                        if wake_detected(transcript, word):
                            triggered = "wake"
                            break
            if triggered and not stop.is_set():
                self.on_trigger(triggered)
        except Exception as exc:
            if not stop.is_set():
                self.retry_after = time.monotonic() + 20
                self.on_status("Activación ambiental no disponible: " + str(exc)[:180])
