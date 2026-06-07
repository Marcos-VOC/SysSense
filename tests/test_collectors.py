import unittest
from unittest.mock import patch

from syssense import collectors


class CollectorsTest(unittest.TestCase):
    def test_clean_text_removes_control_characters_and_limits_size(self):
        text = collectors._clean_text("ok\x00\x1fbom" * 20, max_chars=10)

        self.assertNotIn("\x00", text)
        self.assertNotIn("\x1f", text)
        self.assertLessEqual(len(text), 10)

    def test_runtime_info_has_expected_shape(self):
        info = collectors.get_runtime_info()

        self.assertIn(info["mode"], {"native", "sandbox"})
        self.assertIn(info["process_scope"], {"host", "sandbox"})
        self.assertIsInstance(info["is_flatpak"], bool)

    def test_runtime_info_detects_flatpak_from_environment(self):
        with patch.dict("os.environ", {"FLATPAK_ID": "br.com.syssense"}, clear=True):
            with patch("os.path.exists", return_value=False):
                info = collectors.get_runtime_info()

        self.assertTrue(info["is_flatpak"])
        self.assertEqual(info["mode"], "sandbox")
        self.assertEqual(info["process_scope"], "sandbox")

    def test_runtime_info_detects_native_without_flatpak_markers(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("os.path.exists", return_value=False):
                info = collectors.get_runtime_info()

        self.assertFalse(info["is_flatpak"])
        self.assertEqual(info["mode"], "native")
        self.assertEqual(info["process_scope"], "host")


if __name__ == "__main__":
    unittest.main()
