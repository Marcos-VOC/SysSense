import unittest

from syssense import formatters


class FormattersTest(unittest.TestCase):
    def test_format_refresh_option(self):
        self.assertEqual(formatters.format_refresh_option(1.0), "1s")
        self.assertEqual(formatters.format_refresh_option(2.5), "2.5s")

    def test_format_disk_size(self):
        self.assertEqual(formatters.format_disk_size(512 * 1024**2), "512M")
        self.assertEqual(formatters.format_disk_size(2 * 1024**3), "2.0G")

    def test_format_rate(self):
        self.assertEqual(formatters.format_rate(500), "500 B/s")
        self.assertEqual(formatters.format_rate(2048), "2 KB/s")
        self.assertEqual(formatters.format_rate(2.5 * 1024**2), "2.5 MB/s")

    def test_format_total_transfer(self):
        self.assertEqual(formatters.format_total_transfer(1024), "1 KB")
        self.assertEqual(formatters.format_total_transfer(4 * 1024**2), "4.0 MB")
        self.assertEqual(formatters.format_total_transfer(3 * 1024**3), "3.00 GB")

    def test_format_network_text_parts(self):
        self.assertEqual(formatters.format_network_rates(1024, 512), "↓ 1 KB/s | ↑ 512 B/s")
        self.assertEqual(
            formatters.format_network_tooltip(1024, 2048),
            "Acumulado recebido: 1 KB\nAcumulado enviado: 2 KB",
        )

    def test_format_load_average(self):
        self.assertEqual(
            formatters.format_load_average({"1min": 0.1, "5min": 1.2, "15min": 2.345}),
            "1min: 0.10 | 5min: 1.20 | 15min: 2.35",
        )

    def test_format_uptime(self):
        self.assertEqual(formatters.format_uptime({"uptime_formatted": "1d 2h 3m"}), "1d 2h 3m")
        self.assertEqual(formatters.format_uptime({"uptime_seconds": 90061}), "1d 1h 1m")
        self.assertEqual(formatters.format_uptime({}), "N/A")


if __name__ == "__main__":
    unittest.main()
