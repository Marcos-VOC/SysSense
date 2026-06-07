import unittest
import subprocess
import sys
import types
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

    def test_failed_services_handles_command_error(self):
        result = subprocess.CompletedProcess(
            args=["systemctl"],
            returncode=1,
            stdout="",
            stderr="erro",
        )
        with patch("syssense.collectors._run_readonly_command", return_value=result):
            services = collectors.get_failed_services()

        self.assertEqual(services["count"], 0)
        self.assertEqual(services["failed_services"], [])

    def test_failed_services_parses_json(self):
        result = subprocess.CompletedProcess(
            args=["systemctl"],
            returncode=0,
            stdout='[{"unit":"bad.service","state":"failed","sub":"failed"}]',
            stderr="",
        )
        with patch("syssense.collectors._run_readonly_command", return_value=result):
            services = collectors.get_failed_services()

        self.assertEqual(services["count"], 1)
        self.assertEqual(services["failed_services"][0]["name"], "bad.service")

    def test_recent_logs_limits_requested_lines(self):
        result = subprocess.CompletedProcess(
            args=["journalctl"],
            returncode=0,
            stdout="linha 1\nlinha 2\n",
            stderr="",
        )
        with patch("syssense.collectors._run_readonly_command", return_value=result) as command:
            logs = collectors.get_recent_logs(500)

        self.assertEqual(logs["logs"], ["linha 1", "linha 2"])
        self.assertIn("100", command.call_args.args[0])

    def test_speedtest_returns_friendly_error_on_failure(self):
        with patch.dict("sys.modules", {"speedtest": None}):
            result = collectors.speedtest()

        self.assertFalse(result["success"])
        self.assertIn("speedtest-cli", result["error"])

    def test_speedtest_uses_timeout_and_secure_mode(self):
        created = {}

        class FakeResults:
            def dict(self):
                return {
                    "download": 120_000_000,
                    "upload": 30_000_000,
                    "ping": 11.2,
                    "server": {"sponsor": "Servidor Teste"},
                }

        class FakeSpeedtest:
            def __init__(self, timeout, secure):
                created["timeout"] = timeout
                created["secure"] = secure
                self.results = FakeResults()

            def get_servers(self, servers):
                created["servers"] = servers

            def get_best_server(self):
                created["best"] = True

            def download(self):
                created["download"] = True

            def upload(self):
                created["upload"] = True

        fake_module = types.SimpleNamespace(Speedtest=FakeSpeedtest)
        with patch.dict(sys.modules, {"speedtest": fake_module}):
            result = collectors.speedtest(timeout=7)

        self.assertTrue(result["success"])
        self.assertEqual(created["timeout"], 7)
        self.assertTrue(created["secure"])
        self.assertEqual(created["servers"], [])
        self.assertEqual(result["download_mbps"], 120.0)
        self.assertEqual(result["upload_mbps"], 30.0)
        self.assertEqual(result["server"], "Servidor Teste")

    def test_speedtest_returns_friendly_timeout_error(self):
        class FakeSpeedtest:
            def __init__(self, timeout, secure):
                pass

            def get_servers(self, servers):
                raise TimeoutError("timed out <internal>")

        fake_module = types.SimpleNamespace(Speedtest=FakeSpeedtest)
        with patch.dict(sys.modules, {"speedtest": fake_module}):
            result = collectors.speedtest()

        self.assertFalse(result["success"])
        self.assertIn("Tempo esgotado", result["error"])
        self.assertNotIn("<internal>", result["error"])


if __name__ == "__main__":
    unittest.main()
