
from incident_history import (
    construir_historico,
)
from incidents import carregar_registros

from incident_store import (
    inicializar_banco,
    salvar_incidente,
    listar_incidentes,
)


def sincronizar_incidentes():
    registros = carregar_registros()

    if not registros:
        print("Nenhum registro para sincronizar.")
        return

    historico = construir_historico(registros)

    inicializar_banco()

    for incidente in historico.values():
        registro = {
            "incident_id": incidente["id"],
            "service_name": incidente["endpoint"],
            "status": incidente["estado"],
            "detected_at": incidente["inicio_degradacao"],
            "confirmed_at": incidente["confirmacao_critica"],
            "recovered_at": incidente["recuperacao"],
            "duration_seconds": incidente["duracao_segundos"],
        }

        salvar_incidente(registro)

    print("\nPAYMENTS API MONITOR - SQLITE SYNC")
    print("=" * 45)
    print(f"Incidentes processados: {len(historico)}")
    print(f"Registros no banco: {len(listar_incidentes())}")


if __name__ == "__main__":
    sincronizar_incidentes()
