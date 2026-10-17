
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import incident_store
import incident_sync


class TestIncidentSync(unittest.TestCase):

    def test_sincronizacao_sem_duplicacoes(self):
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "incidents.db"

            registros = [
                {
                    "service_name": "payment-authorization-api",
                    "endpoint": "https://httpbin.org/status/500",
                    "timestamp": f"2026-10-16T12:00:{i:02d}+00:00",
                    "resultado": "ERRO_SERVIDOR",
                }
                for i in range(3)
            ]

            with (
                patch.object(incident_store, "DB_PATH", banco),
                patch.object(
                    incident_sync,
                    "carregar_registros",
                    return_value=registros
                ),
            ):
                incident_sync.sincronizar_incidentes()
                incident_sync.sincronizar_incidentes()

                incidentes = incident_store.listar_incidentes()

                self.assertEqual(len(incidentes), 1)
                self.assertEqual(
                    incidentes[0]["status"],
                    "CRITICAL"
                )
                self.assertEqual(
                    incidentes[0]["service_name"],
                    "payment-authorization-api"
                )
    def test_sincronizacao_com_recuperacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "incidents.db"

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
                codigo = 500 if resultado != "OK" else 200

                registros.append({
                    "service_name": "payment-authorization-api",
                    "endpoint": f"https://httpbin.org/status/{codigo}",
                    "timestamp": f"2026-10-16T12:00:{i:02d}+00:00",
                    "resultado": resultado,
                })

            with (
                patch.object(incident_store, "DB_PATH", banco),
                patch.object(
                    incident_sync,
                    "carregar_registros",
                    return_value=registros[:3]
                ) as mock_logs,
            ):
                incident_sync.sincronizar_incidentes()

                incidentes = incident_store.listar_incidentes()
                self.assertEqual(len(incidentes), 1)
                self.assertEqual(incidentes[0]["status"], "CRITICAL")

                incident_id = incidentes[0]["incident_id"]

                mock_logs.return_value = registros
                incident_sync.sincronizar_incidentes()

                incidentes = incident_store.listar_incidentes()

                self.assertEqual(len(incidentes), 1)
                self.assertEqual(incidentes[0]["incident_id"], incident_id)
                self.assertEqual(incidentes[0]["status"], "RECOVERED")
                self.assertEqual(
                    incidentes[0]["duration_seconds"], 5.0
                )


if __name__ == "__main__":
    unittest.main()

   