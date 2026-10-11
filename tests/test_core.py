import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis_prime.core import remember, recall, local_action, chat
from jarvis_prime.network import validate_url
from jarvis_prime.config import save_settings, load_settings

class CoreTests(unittest.TestCase):
    def test_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.db"
            remember("uno", path)
            remember("dos", path)
            self.assertEqual(recall(path), ["dos", "uno"])

    def test_unknown_command(self):
        self.assertIsNone(local_action("comando no autorizado"))

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
