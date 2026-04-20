
import time
import csv
import pandas as pd

CAMINHO_ARQUIVO = "resultados/resultados.dat"
PASTA_PLOTS = "resultados"

CABECALHO = ["INSTANCE", "METHOD", "OBJECTIVE", "RUNTIME", "GAP"]

def calcular_penalidade(n_veiculos, melhor_k, melhor_conhecido):
    if melhor_k is None:
        return 0.0
    a = melhor_conhecido * 0.05 # 5% por veiculos a mais
    b = melhor_conhecido * 0.05
    return a * max(0,n_veiculos - melhor_k) + b * max(0, melhor_k - n_veiculos)

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
def executar_e_salvar(heuristica, inst, melhor_conhecido, melhor_k=None):
    inicio = time.perf_counter()
    rotas, custo, n_veiculos = heuristica.resolver(inst)
    fim = time.perf_counter()
    runtime = fim - inicio

    """
    Resumo: 
    k_veiculos > melhor_k = penalidade grande, GAP piora
    k_veiculos == melhor_k = penalidade zero, GAP sai normal
    k_veiculos < melhor_k = penalidade pequena, GAP nao muda muito
    """
    penalidade = calcular_penalidade(n_veiculos, melhor_k, melhor_conhecido)

    # Cálculo do GAP (Garante que não seja negativo por float drift)
    gap = (((custo + penalidade) - melhor_conhecido) / melhor_conhecido) * 100
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
def executar_instancia(heuristicas, inst, melhor_conhecido, melhor_k, arquivo_resultado, pasta_plots):
    resultados = []
    for h in heuristicas:
        r = executar_e_salvar(h, inst, melhor_conhecido, melhor_k)
    #     resultados.append(r)
    # return resultados