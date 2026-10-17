
import unittest
from datetime import datetime, timedelta, timezone

from incidents import analisar_endpoint


class TestIncidentDetection(unittest.TestCase):

    def criar_registros(self, resultados):
        inicio = datetime(
            2026, 10, 16, 12, 0, 0,
            tzinfo=timezone.utc
        )

        return [
            {
                "endpoint": "payment-authorization-api",
                "timestamp": (
                    inicio + timedelta(seconds=i * 10)
                ).isoformat(),
                "resultado": resultado
            }
            for i, resultado in enumerate(resultados)
        ]

    def testar_healthy(self):
        registros = self.criar_registros([
            "OK", "OK", "OK"
        ])

        estado, eventos = analisar_endpoint(registros)

        self.assertEqual(estado, "HEALTHY")
        self.assertEqual(eventos, [])

    def testar_degraded(self):
        registros = self.criar_registros([
            "OK", "ERRO_SERVIDOR"
        ])

        estado, eventos = analisar_endpoint(registros)

        self.assertEqual(estado, "DEGRADED")
        self.assertEqual(eventos[-1][0], "DEGRADED")

    def testar_critical(self):
        registros = self.criar_registros([
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR"
        ])

        estado, eventos = analisar_endpoint(registros)

        self.assertEqual(estado, "CRITICAL")
        self.assertEqual(eventos[-1][0], "CRITICAL")

    def testar_recovered(self):
        registros = self.criar_registros([
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "OK", "OK", "OK"
        ])

        estado, eventos = analisar_endpoint(registros)

        self.assertEqual(estado, "RECOVERED")
        self.assertEqual(eventos[-1][0], "RECOVERED")

    def testar_recuperacao_incompleta(self):
        registros = self.criar_registros([
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "OK", "OK"
        ])

        estado, eventos = analisar_endpoint(registros)

        self.assertEqual(estado, "CRITICAL")
        self.assertNotIn(
            "RECOVERED",
            [evento[0] for evento in eventos]
        )

    def testar_falha_durante_recuperacao(self):
        registros = self.criar_registros([
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "OK", "OK",
            "ERRO_SERVIDOR",
            "OK", "OK", "OK"
        ])

        estado, eventos = analisar_endpoint(registros)

        self.assertEqual(estado, "RECOVERED")

        recuperacoes = [
            evento for evento in eventos
            if evento[0] == "RECOVERED"
        ]

        self.assertEqual(len(recuperacoes), 1)


    def testar_identidade_estavel(self):
        from incident_history import construir_historico

        resultados = [
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "ERRO_SERVIDOR",
            "OK",
            "OK",
            "OK",
        ]

        registros = []

        for i, resultado in enumerate(resultados):
            codigo = "500" if resultado != "OK" else "200"

            registros.append({
                "service_name": "payment-authorization-api",
                "endpoint": f"https://httpbin.org/status/{codigo}",
                "timestamp": f"2026-10-16T12:00:{i:02d}+00:00",
                "resultado": resultado,
            })

        historico = construir_historico(registros)

        self.assertEqual(len(historico), 1)

        incidente = next(iter(historico.values()))

        self.assertEqual(incidente["estado"], "RECOVERED")
        self.assertEqual(incidente["duracao_segundos"], 5.0)
        self.assertEqual(
              incidente["service_name"],
            "payment-authorization-api"
        )

        self.assertEqual(
            incidente["endpoint"],
            "https://httpbin.org/status/500"
        )


if __name__ == "__main__":
    unittest.main()



