
import time
import csv
import pandas as pd

CAMINHO_ARQUIVO = "resultados/resultados.dat"
PASTA_PLOTS = "resultados"

CABECALHO = ["INSTANCE", "METHOD", "OBJECTIVE", "RUNTIME", "GAP"]

def carregar_resultados(caminho_dat=CAMINHO_ARQUIVO):
    df = pd.read_csv(caminho_dat, sep="\t")
    # Limpeza de strings e conversão numérica
    df.columns = df.columns.str.strip()
    for col in ["OBJECTIVE", "RUNTIME", "GAP"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def salvar_resultado(instancia, metodo, objetivo, runtime, gap):
    """Apenas adiciona a linha ao arquivo (Append)."""
    with open(CAMINHO_ARQUIVO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([instancia, metodo, f"{objetivo:.2f}", f"{runtime:.6f}", f"{gap:.4f}"])

# execução individual
def executar_e_salvar(heuristica, inst, melhor_conhecido):
    inicio = time.perf_counter()
    rotas, custo, n_veiculos = heuristica.resolver(inst)
    fim = time.perf_counter()
    runtime = fim - inicio

    # Cálculo do GAP (Garante que não seja negativo por float drift)
    gap = ((custo - melhor_conhecido) / melhor_conhecido) * 100
    gap = max(0.0, gap)

    salvar_resultado(inst.nome, heuristica.nome, custo, runtime, gap)
    from saida.graphics import plotar_rotas
    caminho_png = plotar_rotas(inst, rotas, heuristica.nome, PASTA_PLOTS)

    return {
        "heuristica": heuristica.nome,
        "custo": custo,
        "veiculos": n_veiculos,
        "runtime": runtime,
        "gap": gap,
        "png": caminho_png,
    }

# usado no benchmark
def executar_instancia(heuristicas, inst, melhor_conhecido, arquivo_resultado, pasta_plots):
    resultados = []
    for h in heuristicas:
        r = executar_e_salvar(h, inst, melhor_conhecido)
        resultados.append(r)
    return resultados