"""Optional push-to-talk + speech output. SpeechRecognition online recognizer needs internet."""
import threading

def speak(text):
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError("Falta pyttsx3. Instala: .venv\\Scripts\\python.exe -m pip install pyttsx3") from exc
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    voices = engine.getProperty("voices")
    spanish = next((v for v in voices if "spanish" in (str(v.name) + " " + str(v.id)).lower()
                    or "es-" in str(v.id).lower()), None)
    if spanish:
        engine.setProperty("voice", spanish.id)
    engine.say(text[:1700])
    engine.runAndWait()

def listen_once(seconds=6):
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise RuntimeError("Falta SpeechRecognition. Instala las dependencias de voz opcionales del README.") from exc
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=seconds, phrase_time_limit=12)
    try:
        return recognizer.recognize_google(audio, language="es-GT")
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        raise RuntimeError("Reconocimiento de voz no disponible: " + str(exc)) from exc
