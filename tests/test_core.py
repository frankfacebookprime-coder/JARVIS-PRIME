import tempfile
import unittest
from pathlib import Path
from jarvis_prime.core import remember, recall, local_action, chat

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
        self.assertIn("configura", chat("hola", api_key="", model="").lower())

if __name__ == "__main__":
    unittest.main()
