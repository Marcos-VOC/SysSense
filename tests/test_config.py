import json
import tempfile
import unittest
from pathlib import Path

from syssense import config


class ConfigTest(unittest.TestCase):
    def test_load_config_returns_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.json"

            loaded = config.load_config(path)

        self.assertEqual(loaded["refresh_interval"], 2.5)
        self.assertTrue(loaded["critical_toasts"])
        self.assertTrue(loaded["visible_cards"]["cpu"])

    def test_load_config_ignores_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            path.write_text("{invalid", encoding="utf-8")

            loaded = config.load_config(path)

        self.assertEqual(loaded, config.DEFAULT_CONFIG)

    def test_normalize_config_rejects_invalid_refresh_interval(self):
        normalized = config.normalize_config({"refresh_interval": 0.1})

        self.assertEqual(normalized["refresh_interval"], 2.5)

    def test_save_config_writes_normalized_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            saved = config.save_config(
                {
                    "refresh_interval": 5,
                    "critical_toasts": False,
                    "show_speedtest": False,
                    "visible_cards": {"internet": False},
                },
                path,
            )
            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(saved["refresh_interval"], 5.0)
        self.assertFalse(saved["critical_toasts"])
        self.assertFalse(data["show_speedtest"])
        self.assertFalse(data["visible_cards"]["internet"])


if __name__ == "__main__":
    unittest.main()
