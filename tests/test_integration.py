
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import incident_store
from incident_history import construir_historico


class TestIncidentIntegration(unittest.TestCase):

    def test_ciclo_completo(self):
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "incidents.db"

            with patch.object(incident_store, "DB_PATH", banco):
                incident_store.inicializar_banco()

                service = "payment-authorization-api"

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
                        "service_name": service,
                        "endpoint": (
                            f"https://httpbin.org/status/{codigo}"
                        ),
                        "timestamp": (
                            f"2026-10-16T12:00:{i:02d}+00:00"
                        ),
                        "resultado": resultado,
                    })

                # Primeiro: incidente crítico
                historico_critico = construir_historico(
                    registros[:3]
                )

                self.assertEqual(len(historico_critico), 1)

                incidente = next(
                    iter(historico_critico.values())
                )

                dados = {
                    "incident_id": incidente["id"],
                    "service_name": service,
                    "status": incidente["estado"],
                    "detected_at": incidente["inicio_degradacao"],
                    "confirmed_at": incidente["confirmacao_critica"],
                    "recovered_at": incidente["recuperacao"],
                    "duration_seconds": incidente["duracao_segundos"],
                }

                incident_store.salvar_incidente(dados)

                self.assertEqual(
                    incident_store.listar_incidentes()[0]["status"],
                    "CRITICAL"
                )

                # Segundo: recuperação do mesmo incidente
                historico_recuperado = construir_historico(
                    registros
                )

                recuperado = next(
                    iter(historico_recuperado.values())
                )

                self.assertEqual(
                    recuperado["id"],
                    incidente["id"]
                )

                dados["status"] = recuperado["estado"]
                dados["recovered_at"] = recuperado["recuperacao"]
                dados["duration_seconds"] = (
                    recuperado["duracao_segundos"]
                )

                incident_store.salvar_incidente(dados)
                incident_store.salvar_incidente(dados)

                armazenados = incident_store.listar_incidentes()

                self.assertEqual(len(armazenados), 1)
                self.assertEqual(
                    armazenados[0]["status"],
                    "RECOVERED"
                )
                self.assertEqual(
                    armazenados[0]["duration_seconds"],
                    5.0
                )


if __name__ == "__main__":
    unittest.main()
