import unittest

from syssense import diagnostics


class DiagnosticsTest(unittest.TestCase):
    def test_no_alerts_for_healthy_system(self):
        dados = {
            "cpu": {"percent": 10},
            "memoria": {"percent": 30, "swap_percent": 0},
            "disco": {"partitions": [{"percent": 40}]},
            "servicos": {"count": 0},
            "processos": {"by_memory": [], "by_cpu": []},
        }

        self.assertEqual(diagnostics.diagnosticar_por_regras(dados), [])

    def test_memory_alert_includes_top_processes(self):
        dados = {
            "cpu": {"percent": 10},
            "memoria": {"percent": 90, "swap_percent": 0},
            "disco": {"partitions": [{"percent": 40}]},
            "servicos": {"count": 0},
            "processos": {
                "by_memory": [
                    {"name": "browser", "memory_percent": 22.4},
                    {"name": "editor", "memory_percent": 12.0},
                ],
                "by_cpu": [],
            },
        }

        alertas = diagnostics.diagnosticar_por_regras(dados)

        self.assertEqual(alertas[0]["severidade"], "alta")
        self.assertIn("browser (22.4%)", alertas[0]["mensagem"])

    def test_summary_escapes_markup(self):
        alertas = [
            {
                "severidade": "media",
                "mensagem": "Processo <teste> em uso intenso.",
                "campo": "cpu_percent",
            }
        ]

        resumo = diagnostics.gerar_resumo_diagnostico(alertas)

        self.assertIn("&lt;teste&gt;", resumo)

    def test_alerts_are_sorted_by_severity(self):
        dados = {
            "cpu": {"percent": 90},
            "memoria": {"percent": 90, "swap_percent": 0},
            "disco": {"partitions": [{"percent": 40}]},
            "servicos": {"count": 0},
            "processos": {
                "by_memory": [{"name": "browser", "memory_percent": 22.4}],
                "by_cpu": [{"name": "python", "cpu_percent": 88.0}],
            },
        }

        alertas = diagnostics.diagnosticar_por_regras(dados)

        self.assertEqual(alertas[0]["severidade"], "alta")
        self.assertEqual(alertas[-1]["severidade"], "media")


if __name__ == "__main__":
    unittest.main()
