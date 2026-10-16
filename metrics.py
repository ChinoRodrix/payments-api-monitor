
import json
import statistics
from pathlib import Path

LOG_FILE = Path(__file__).parent / "logs" / "monitor.jsonl"


def carregar_logs():
    if not LOG_FILE.exists():
        print("Nenhum arquivo de logs encontrado.")
        return []

    registros = []

    with LOG_FILE.open("r", encoding="utf-8") as arquivo:
        for numero, linha in enumerate(arquivo, start=1):
            try:
                if linha.strip():
                    registros.append(json.loads(linha))
            except json.JSONDecodeError:
                print(f"Aviso: JSON inválido na linha {numero}")

    return registros


def calcular_percentil(valores, percentil):
    if not valores:
        return None

    valores = sorted(valores)
    posicao = (len(valores) - 1) * percentil / 100

    inferior = int(posicao)
    superior = min(inferior + 1, len(valores) - 1)
    fracao = posicao - inferior

    return (
        valores[inferior] * (1 - fracao)
        + valores[superior] * fracao
    )


def gerar_relatorio():
    registros = carregar_logs()

    if not registros:
        print("Não existem registros para analisar.")
        return

    total = len(registros)

    sucessos = sum(
        r.get("resultado") == "OK" for r in registros
    )

    erros_4xx = sum(
        r.get("resultado") == "ERRO_CLIENTE" for r in registros
    )

    erros_5xx = sum(
        r.get("resultado") == "ERRO_SERVIDOR" for r in registros
    )

    falhas_conexao = sum(
        r.get("resultado") == "FALHA_CONEXAO" for r in registros
    )

    falhas = total - sucessos

    latencias = [
        r["latencia_ms"]
        for r in registros
        if isinstance(r.get("latencia_ms"), (int, float))
        and not isinstance(r["latencia_ms"], bool)
    ]

    print("\n" + "=" * 44)
    print("       PAYMENTS API MONITOR v0.3")
    print("=" * 44)

    print(f"Total de verificações: {total}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {falhas}")
    print(f"Erros HTTP 4xx: {erros_4xx}")
    print(f"Erros HTTP 5xx: {erros_5xx}")
    print(f"Falhas de conexão: {falhas_conexao}")

    print(f"\nTaxa de sucesso: {sucessos / total * 100:.2f}%")
    print(f"Taxa de erro: {falhas / total * 100:.2f}%")

    if latencias:
        print("\n--- LATÊNCIA ---")
        print(f"Média: {statistics.mean(latencias):.2f} ms")

        for p in (50, 95, 99):
            valor = calcular_percentil(latencias, p)
            print(f"P{p}: {valor:.2f} ms")

    print("=" * 44)


if __name__ == "__main__":
    gerar_relatorio()
