
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import incident_store


class TestIncidentStore(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "incidents.db"

        self.patch_db = patch.object(
            incident_store, "DB_PATH", self.db_path
        )
        self.patch_db.start()

        incident_store.inicializar_banco()

        self.incidente = {
            "incident_id": "INC-TEST-001",
            "service_name": "payment-authorization-api",
            "status": "CRITICAL",
            "detected_at": "2026-10-16T19:00:00+00:00",
            "confirmed_at": "2026-10-16T19:00:20+00:00",
            "recovered_at": None,
            "duration_seconds": None,
        }

    def tearDown(self):
        self.patch_db.stop()
        self.temp_dir.cleanup()

    def test_insercao(self):
        incident_store.salvar_incidente(self.incidente)

        registros = incident_store.listar_incidentes()

        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["status"], "CRITICAL")

    def test_deduplicacao(self):
        incident_store.salvar_incidente(self.incidente)
        incident_store.salvar_incidente(self.incidente)

        registros = incident_store.listar_incidentes()

        self.assertEqual(len(registros), 1)

    def test_recuperacao(self):
        incident_store.salvar_incidente(self.incidente)

        recuperado = {
            **self.incidente,
            "status": "RECOVERED",
            "recovered_at": "2026-10-16T19:05:00+00:00",
            "duration_seconds": 300.0,
        }

        incident_store.salvar_incidente(recuperado)

        registro = incident_store.listar_incidentes()[0]

        self.assertEqual(registro["status"], "RECOVERED")
        self.assertEqual(registro["duration_seconds"], 300.0)

    def test_protecao_contra_regressao(self):
        incident_store.salvar_incidente({
            **self.incidente,
            "status": "RECOVERED",
            "recovered_at": "2026-10-16T19:05:00+00:00",
            "duration_seconds": 300.0,
        })

        incident_store.salvar_incidente(self.incidente)

        registro = incident_store.listar_incidentes()[0]

        self.assertEqual(registro["status"], "RECOVERED")
        self.assertIsNotNone(registro["recovered_at"])
        self.assertEqual(registro["duration_seconds"], 300.0)


if __name__ == "__main__":
    unittest.main()
