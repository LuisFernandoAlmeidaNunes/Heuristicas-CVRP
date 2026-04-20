import os
import time
import csv
import pandas as pd

CAMINHO_ARQUIVO = "resultados/resultados.dat"
PASTA_PLOTS     = "resultados"

CABECALHO = ["INSTANCE", "METHOD", "OBJECTIVE", "RUNTIME", "GAP"]


def carregar_resultados(caminho_dat=CAMINHO_ARQUIVO):
    df = pd.read_csv(caminho_dat, sep="\t")
    df.columns = df.columns.str.strip()
    for col in ["OBJECTIVE", "RUNTIME", "GAP"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def salvar_resultado(instancia, metodo, objetivo, runtime, gap):
    """Append de uma linha no .dat (cria o arquivo + cabeçalho se não existir)."""
    os.makedirs(os.path.dirname(CAMINHO_ARQUIVO), exist_ok=True)
    arquivo_existe = os.path.isfile(CAMINHO_ARQUIVO)
    with open(CAMINHO_ARQUIVO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        if not arquivo_existe:
            writer.writerow(CABECALHO)
        writer.writerow([instancia, metodo,
                         f"{objetivo:.2f}", f"{runtime:.6f}", f"{gap:.4f}"])


def executar_e_salvar(heuristica, inst, melhor_conhecido, melhor_k=None):
    """
    Executa a heurística, mede o tempo e salva o resultado.

    melhor_k é passado direto para resolver() → calcular_custo(),
    onde a penalidade α/β é aplicada sobre o custo antes de calcular o GAP.
    """
    inicio = time.perf_counter()
    rotas, custo, n_veiculos = heuristica.resolver(inst, k_alvo=melhor_k)  # ← k_alvo aqui
    fim   = time.perf_counter()
    runtime = fim - inicio

    # GAP sobre o custo já penalizado (comparável ao BKS)
    gap = max(0.0, (custo - melhor_conhecido) / melhor_conhecido * 100)

    salvar_resultado(inst.nome, heuristica.nome, custo, runtime, gap)

    from saida.graphics import plotar_rotas
    caminho_png = plotar_rotas(inst, rotas, heuristica.nome, PASTA_PLOTS)

    return {
        "heuristica": heuristica.nome,
        "custo":      custo,
        "veiculos":   n_veiculos,
        "runtime":    runtime,
        "gap":        gap,
        "png":        caminho_png,
    }

def executar_instancia(heuristicas, inst, melhor_conhecido, melhor_k,
                       arquivo_resultado, pasta_plots):
    resultados = []
    for h in heuristicas:
        r = executar_e_salvar(h, inst, melhor_conhecido, melhor_k)  # ← repassa melhor_k
        resultados.append(r)
    return resultados