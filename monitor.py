
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://httpbin.org/status/200"
INTERVALO = 10
TIMEOUT = 5

LOG_FILE = Path(__file__).parent / "logs" / "monitor.jsonl"

estatisticas = {
    "total": 0,
    "sucessos": 0,
    "falhas": 0
}


def monitorar_api():
    inicio = time.perf_counter()
    data = datetime.now(timezone.utc).isoformat()

    try:
        resposta = requests.get(URL, timeout=TIMEOUT)
        latencia = round((time.perf_counter() - inicio) * 1000, 2)
        codigo = resposta.status_code

        if 200 <= codigo < 400:
            status = "OK"
        elif 400 <= codigo < 500:
            status = "ERRO_CLIENTE"
        else:
            status = "ERRO_SERVIDOR"

    except requests.RequestException as erro:
        latencia = round((time.perf_counter() - inicio) * 1000, 2)
        codigo = None
        status = "FALHA_CONEXAO"
        print(f"Detalhes: {erro}")

    return {
        "timestamp": data,
        "endpoint": URL,
        "http_status": codigo,
        "latencia_ms": latencia,
        "resultado": status
    }


def salvar_log(resultado):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(resultado, ensure_ascii=False) + "\n")


def executar():
    print("Payments API Monitor v0.2 iniciado")
    print(f"Endpoint: {URL}")
    print(f"Intervalo: {INTERVALO}s")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            resultado = monitorar_api()
            salvar_log(resultado)

            estatisticas["total"] += 1

            if resultado["resultado"] == "OK":
                estatisticas["sucessos"] += 1
            else:
                estatisticas["falhas"] += 1

            print(
                f'[{resultado["timestamp"]}] '
                f'HTTP {resultado["http_status"]} | '
                f'{resultado["latencia_ms"]} ms | '
                f'{resultado["resultado"]}',
                flush=True
            )

            time.sleep(INTERVALO)

    except KeyboardInterrupt:
        total = estatisticas["total"]
        taxa = (estatisticas["sucessos"] / total * 100) if total else 0

        print("\nMonitoramento encerrado.")
        print(f"Total de requisições: {total}")
        print(f"Sucessos: {estatisticas['sucessos']}")
        print(f"Falhas: {estatisticas['falhas']}")
        print(f"Taxa de sucesso: {taxa:.2f}%")


if __name__ == "__main__":
    executar()
