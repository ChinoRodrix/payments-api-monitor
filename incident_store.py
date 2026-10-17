
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "incidents.db"


def conectar():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row

    return conexao


def inicializar_banco():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                service_name TEXT NOT NULL,
                status TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                confirmed_at TEXT,
                recovered_at TEXT,
                duration_seconds REAL
            )
        """)

    print("Banco de incidentes inicializado.")


def salvar_incidente(incidente):
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO incidents (
                incident_id,
                service_name,
                status,
                detected_at,
                confirmed_at,
                recovered_at,
                duration_seconds
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(incident_id) DO UPDATE SET
                status = CASE
                    WHEN incidents.status = 'RECOVERED'
                    THEN 'RECOVERED'
                    ELSE excluded.status
                END,
                confirmed_at = COALESCE(
                    incidents.confirmed_at,
                    excluded.confirmed_at
                ),
                recovered_at = COALESCE(
                    incidents.recovered_at,
                    excluded.recovered_at
                ),
                duration_seconds = COALESCE(
                    incidents.duration_seconds,
                    excluded.duration_seconds
                )
            """,
            (
                incidente["incident_id"],
                incidente["service_name"],
                incidente["status"],
                incidente["detected_at"],
                incidente.get("confirmed_at"),
                incidente.get("recovered_at"),
                incidente.get("duration_seconds"),
            ),
        )



def listar_incidentes():
    with conectar() as conexao:
        registros = conexao.execute("""
            SELECT *
            FROM incidents
            ORDER BY detected_at DESC
        """).fetchall()

    return [dict(registro) for registro in registros]


if __name__ == "__main__":
    inicializar_banco()
