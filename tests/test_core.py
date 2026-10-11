import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis_prime.core import remember, recall, local_action, chat, resolve_local_command, respond
from jarvis_prime.windows_apps import extract_open, match_app, normalize
from jarvis_prime.network import validate_url
from jarvis_prime.browser import browser_action, open_browser
from jarvis_prime.floating import is_panel_command
from jarvis_prime.intent_router import classify, information_title
from jarvis_prime.panel_renderer import split_sections
from jarvis_prime.config import save_settings, load_settings

class CoreTests(unittest.TestCase):
    def test_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            remember("uno", path)
            remember("dos", path)
            self.assertEqual(recall(path), ["dos", "uno"])

    def test_command_variants(self):
        for phrase in ["abre la calculadora", "abre calculadora", "abrir calculadora",
                       "JARVIS, abre la calculadora por favor", "¿Puedes abrir la calculadora?",
                       "inicia la calculadora"]:
            with self.subTest(phrase=phrase):
                self.assertEqual(resolve_local_command(phrase), "calc.exe")
        self.assertEqual(resolve_local_command("abre el bloc de notas"), "notepad.exe")

    def test_unsafe_or_unknown_commands_do_not_execute(self):
        for phrase in ["abre powershell", "elimina los archivos", "abre la calculadora y borra todo",
                       "explica como abrir la calculadora", "comando no autorizado"]:
            with self.subTest(phrase=phrase):
                self.assertIsNone(resolve_local_command(phrase))

    def test_local_command_runs_before_model(self):
        with patch("jarvis_prime.core.sys.platform", "win32"), patch("jarvis_prime.core.subprocess.Popen") as popen, patch("jarvis_prime.core.chat") as remote:
            result = respond("abre la calculadora")
            self.assertIn("calculadora", result)
            popen.assert_called_once_with(["calc.exe"], shell=False)
            remote.assert_not_called()

    def test_installed_app_routing(self):
        for phrase, name in [
            ("abre Word", "microsoft word"),
            ("Jarvis abre Chrome", "google chrome"),
            ("abre Excel", "microsoft excel"),
            ("por favor abre la calculadora", "calculadora"),
            ("puedes abrir el bloc de notas", "bloc de notas"),
        ]:
            with self.subTest(phrase=phrase):
                self.assertEqual(extract_open(phrase), name)

    def test_installed_shortcut_match(self):
        apps = {"microsoft word": "C:/Start/Word.lnk", "google chrome": "C:/Start/Chrome.lnk"}
        self.assertEqual(match_app("Word", apps), ("shortcut", "C:/Start/Word.lnk"))
        self.assertEqual(match_app("Chrome", apps), ("shortcut", "C:/Start/Chrome.lnk"))
        self.assertIsNone(match_app("powershell", apps))
        self.assertIsNone(match_app("unknown app", apps))

    def test_unrecognized_not_executed(self):
        with patch("jarvis_prime.windows_apps.sys.platform", "win32"), patch("jarvis_prime.windows_apps.discover_shortcuts", return_value={}):
            self.assertIn("No encontré", local_action("abre una app desconocida"))

    def test_browser_natural_language(self):
        for phrase in ["puedes abrir YouTube en Google", "abre youtube",
                       "Jarvis abre youtube en chrome", "abre la pagina de youtube"]:
            with self.subTest(phrase=phrase):
                action = browser_action(phrase)
                self.assertIsNotNone(action)
                self.assertEqual(action[1], "https://www.youtube.com/")
        self.assertTrue(browser_action("busca gatos en google")[1].startswith("https://www.google.com/search?q="))
        self.assertIsNone(browser_action("dime la historia de YouTube"))
        self.assertIsNone(browser_action("elimina mis archivos"))

    def test_browser_is_not_sent_to_ai(self):
        with patch("jarvis_prime.core.chat") as ai, patch("jarvis_prime.browser.webbrowser.open", return_value=True) as opener:
            value = respond("puedes abrir YouTube en Google")
            self.assertIn("YouTube".lower(), value.lower())
            ai.assert_not_called()
            opener.assert_called_once_with("https://www.youtube.com/", new=2)

    def test_floating_panel_voice_command(self):
        for phrase in ("abre el panel", "Jarvis abre el panel", "muestra el panel", "open panel"):
            self.assertTrue(is_panel_command(phrase))
        self.assertFalse(is_panel_command("abre Word"))
        self.assertFalse(is_panel_command("busca cosas en google"))

    def test_intent_routing_v06(self):
        cases = [
            ("abre Word", "app"),
            ("abre YouTube en Google", "browser"),
            ("qué es Linux", "ai"),
            ("investiga Wim Hof y muéstramelo", "ai"),
            ("abre el panel", "panel"),
            ("estado de mi computadora", "local"),
            ("ver procesos", "local"),
        ]
        for message, expected in cases:
            with self.subTest(message=message):
                self.assertEqual(classify(message).kind, expected)
        self.assertTrue(classify("explícame qué es Python").visual)
        self.assertEqual(information_title("investiga Linux y muéstramelo"), "Linux")
        self.assertEqual(split_sections("Hola mundo")[0][0], "text")

    def test_intent_executor_never_sends_app_to_ai(self):
        from jarvis_prime.core import execute
        with patch("jarvis_prime.core.local_action", return_value="Aplicación iniciada") as action:
            with patch("jarvis_prime.core.chat") as remote:
                intent, answer = execute("abre Word")
                self.assertEqual(intent.kind, "app")
                self.assertEqual(answer, "Aplicación iniciada")
                action.assert_called_once()
                remote.assert_not_called()

    def test_no_api_key(self):
        self.assertIn("configurar ia", chat("hola", api_key="", model="").lower())

    def test_https_required(self):
        with self.assertRaises(ValueError):
            validate_url("http://remoto.example/v1")
        with self.assertRaises(ValueError):
            validate_url("https://user:pass@example.com/v1")
        self.assertEqual(validate_url("http://localhost:1234/v1/"), "http://localhost:1234/v1")

    def test_settings_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "settings.json"
            with patch("jarvis_prime.config.SETTINGS", path), patch("jarvis_prime.config.FOLDER", Path(folder)):
                save_settings({"provider": "Personalizado", "base_url": "https://example.com/v1", "model": "demo"})
                data = load_settings()
                self.assertEqual(data["model"], "demo")
                self.assertNotIn("api_key", path.read_text())

if __name__ == "__main__":
    unittest.main()
