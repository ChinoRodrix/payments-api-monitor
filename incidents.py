
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "logs" / "monitor.jsonl"

LIMITE_FALHAS = 3
LIMITE_RECUPERACAO = 3


def carregar_registros():
    if not LOG_FILE.exists():
        return []

    registros = []

    with LOG_FILE.open(encoding="utf-8") as arquivo:
        for numero, linha in enumerate(arquivo, 1):
            if not linha.strip():
                continue

            try:
                registro = json.loads(linha)
                if all(
                    chave in registro
                    for chave in ("endpoint", "timestamp", "resultado")
                ):
                    registros.append(registro)
            except json.JSONDecodeError:
                print(f"JSON inválido na linha {numero}")

    return registros


def analisar_endpoint(registros):
    estado = "HEALTHY"
    falhas = 0
    sucessos = 0
    inicio_incidente = None
    eventos = []

    for registro in registros:
        timestamp = registro["timestamp"]
        ok = registro["resultado"] == "OK"

        if ok:
            sucessos += 1
            falhas = 0
        else:
            falhas += 1
            sucessos = 0

        if estado in ("HEALTHY", "RECOVERED"):
            if not ok:
                estado = "DEGRADED"
                eventos.append(("DEGRADED", timestamp))

        elif estado == "DEGRADED":
            if falhas >= LIMITE_FALHAS:
                estado = "CRITICAL"
                inicio_incidente = timestamp
                eventos.append(("CRITICAL", timestamp))
            elif ok:
                estado = "HEALTHY"
                eventos.append(("HEALTHY", timestamp))

        elif estado == "CRITICAL":
            if sucessos >= LIMITE_RECUPERACAO:
                estado = "RECOVERED"
                fim = datetime.fromisoformat(timestamp)
                inicio = datetime.fromisoformat(inicio_incidente)

                duracao = (fim - inicio).total_seconds()

                eventos.append((
                    "RECOVERED",
                    timestamp,
                    round(duracao, 2)
                ))

    return estado, eventos



def executar():
    registros = carregar_registros()

    if not registros:
        print("Nenhum registro encontrado.")
        return

    servicos = defaultdict(list)

    for registro in registros:
        servico = registro.get("service_name") or registro["endpoint"]
        servicos[servico].append(registro)

    print("\nPAYMENTS API MONITOR v0.8")
    print("=" * 50)

    for servico, dados in servicos.items():
        dados.sort(key=lambda r: r["timestamp"])

        estado, eventos = analisar_endpoint(dados)

        print(f"\nServiço: {servico}")
        print(f"Estado atual: {estado}")

        for evento in eventos:
            print(f"  Transição: {evento}")

    print("=" * 50)


if __name__ == "__main__":
   

    executar()
