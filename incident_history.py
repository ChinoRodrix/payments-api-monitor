
import hashlib
import json
from datetime import datetime
from pathlib import Path

from incidents import carregar_registros, analisar_endpoint

BASE_DIR = Path(__file__).parent
ARQUIVO_INCIDENTES = BASE_DIR / "data" / "incidents.jsonl"


def gerar_id(endpoint, timestamp):
    identificador = f"{endpoint}|{timestamp}"
    hash_id = hashlib.sha256(
        identificador.encode("utf-8")
    ).hexdigest()[:12]

    return f"INC-{hash_id.upper()}"


def carregar_incidentes():
    if not ARQUIVO_INCIDENTES.exists():
        return {}

    incidentes = {}

    with ARQUIVO_INCIDENTES.open(encoding="utf-8") as arquivo:
        for linha in arquivo:
            if linha.strip():
                incidente = json.loads(linha)
                incidentes[incidente["id"]] = incidente

    return incidentes


def construir_historico(registros):
    endpoints = {}

    for registro in registros:
        servico = registro.get("service_name") or registro["endpoint"]
        endpoints.setdefault(servico, []).append(registro)

    historico = {}

    for endpoint, dados in endpoints.items():
        dados.sort(key=lambda r: r["timestamp"])
        _, eventos = analisar_endpoint(dados)

        incidente = None

        for evento in eventos:
            estado, timestamp = evento[:2]

            if estado == "DEGRADED":
                incidente = {
                    "id": gerar_id(endpoint, timestamp),
                    "endpoint": endpoint,
                    "inicio_degradacao": timestamp,
                    "confirmacao_critica": None,
                    "recuperacao": None,
                    "duracao_segundos": None,
                    "estado": "DEGRADED",
                    "timeline": [
                        {"estado": estado, "timestamp": timestamp}
                    ]
                }

            elif estado == "CRITICAL" and incidente:
                incidente["confirmacao_critica"] = timestamp
                incidente["estado"] = "CRITICAL"
                incidente["timeline"].append({
                    "estado": estado,
                    "timestamp": timestamp
                })

            elif estado == "RECOVERED" and incidente:
                incidente["recuperacao"] = timestamp
                incidente["estado"] = "RECOVERED"

                inicio = datetime.fromisoformat(
                    incidente["inicio_degradacao"]
                )
                fim = datetime.fromisoformat(timestamp)

                incidente["duracao_segundos"] = round(
                    (fim - inicio).total_seconds(), 2
                )

                incidente["timeline"].append({
                    "estado": estado,
                    "timestamp": timestamp
                })

                historico[incidente["id"]] = incidente
                incidente = None

            elif estado == "HEALTHY" and incidente:
                # Degradação transitória sem incidente crítico
                incidente = None

        if incidente:
            historico[incidente["id"]] = incidente

    return historico


def salvar_historico(historico):
    ARQUIVO_INCIDENTES.parent.mkdir(
        parents=True, exist_ok=True
    )

    with ARQUIVO_INCIDENTES.open(
        "w", encoding="utf-8"
    ) as arquivo:
        for incidente in historico.values():
            arquivo.write(
                json.dumps(incidente, ensure_ascii=False) + "\n"
            )


def executar():
    registros = carregar_registros()

    if not registros:
        print("Nenhum registro para analisar.")
        return

    historico = construir_historico(registros)
    salvar_historico(historico)

    print("\nPAYMENTS API MONITOR v0.6")
    print("=" * 50)
    print(f"Incidentes registrados: {len(historico)}")

    for incidente in historico.values():
        print(f"\nID: {incidente['id']}")
        print(f"Endpoint: {incidente['endpoint']}")
        print(f"Estado: {incidente['estado']}")
        print(f"Início: {incidente['inicio_degradacao']}")
        print(f"Confirmação: {incidente['confirmacao_critica']}")
        print(f"Recuperação: {incidente['recuperacao']}")
        print(f"Duração: {incidente['duracao_segundos']} s")


if __name__ == "__main__":
    executar()
