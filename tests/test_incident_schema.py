
import unittest

from incident_history import construir_historico


class TestIncidentSchema(unittest.TestCase):

    def test_service_name_separado_do_endpoint(self):
        servico = "payment-authorization-api"

        resultados = [
            ("500", "ERRO_SERVIDOR"),
            ("500", "ERRO_SERVIDOR"),
            ("500", "ERRO_SERVIDOR"),
            ("200", "OK"),
            ("200", "OK"),
            ("200", "OK"),
        ]

        registros = []

        for i, (codigo, resultado) in enumerate(resultados):
            registros.append({
                "service_name": servico,
                "endpoint": f"https://httpbin.org/status/{codigo}",
                "timestamp": f"2026-10-16T12:00:{i:02d}+00:00",
                "resultado": resultado,
            })

        historico = construir_historico(registros)

        self.assertEqual(len(historico), 1)

        incidente = next(iter(historico.values()))

        self.assertEqual(
            incidente["service_name"],
            servico
        )

        self.assertEqual(
            incidente["endpoint"],
            "https://httpbin.org/status/500"
        )

        self.assertEqual(
            incidente["estado"],
            "RECOVERED"
        )


if __name__ == "__main__":
    unittest.main()
