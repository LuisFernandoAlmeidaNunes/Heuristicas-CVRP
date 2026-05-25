import os
import time
import csv
import pandas as pd
from Heuristicas.Heuristica import Heuristica

# Este módulo centraliza a lógica de execução, cronometragem e persistência de dados.
# Sua função é garantir que todas as heurísticas sejam testadas sob as mesmas
# condições e que seus resultados sejam registrados de forma padronizada.
#
# As principais responsabilidades deste arquivo incluem:
#
# 1. Controle de Execução: Gerencia o ciclo de vida da execução de uma heurística,
#    desde a medição precisa do tempo (utilizando perf_counter) até o cálculo
#    do Gap em relação ao melhor valor conhecido (BKS).
#
# 2. Cálculo de Gap e Penalidades: Garante que o Gap seja calculado sobre o custo
#    final retornado, permitindo uma comparação justa entre métodos que respeitam
#    ou não o limite de veículos (k_alvo).
#
# 3. Persistência de Dados: Automatiza o salvamento dos resultados em formato .dat
#    tabulado, facilitando a leitura posterior por bibliotecas de análise de dados
#    como o Pandas.
#
# 4. Interface Visual: Integra-se ao módulo de gráficos para gerar automaticamente
#    os mapas de rotas (PNG) quando executado em modo individual, ou suprimir
#    essa geração durante o benchmark para otimizar a performance.

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


def executar_e_salvar(heuristica, inst, melhor_conhecido, melhor_k=None, is_beenchmark = False):
    """
    Executa a heurística, mede o tempo e salva o resultado.
    """
    inicio = time.perf_counter()
    rotas, custo, n_veiculos = heuristica.resolver(inst, k_alvo=melhor_k)  # ← k_alvo aqui
    fim   = time.perf_counter()
    runtime = fim - inicio

    # GAP sobre o custo com penalidade de veículos
    custo_penalidade = heuristica.calcular_custo(inst, rotas, melhor_k)
    gap = max(0.0, (custo_penalidade - melhor_conhecido) / melhor_conhecido * 100)

    salvar_resultado(inst.nome, heuristica.nome, custo_penalidade, runtime, gap)

    from saida.graphics import plotar_rotas
    
    if not is_beenchmark:
        caminho_png = plotar_rotas(inst, rotas, heuristica.nome, PASTA_PLOTS)

        return {
            "heuristica": heuristica.nome,
            "custo":      custo_penalidade,
            "veiculos":   n_veiculos,
            "runtime":    runtime,
            "gap":        gap,
            "png":        caminho_png,
        }
    else:
        return {
            "heuristica": heuristica.nome,
            "custo": custo_penalidade,
            "veiculos": n_veiculos,
            "runtime": runtime,
            "gap": gap
        }

def executar_instancia(heuristicas, inst, melhor_conhecido, melhor_k, is_beenchmark = True):
    resultados = []
    for h in heuristicas:
        r = executar_e_salvar(h, inst, melhor_conhecido, melhor_k, is_beenchmark)  # ← repassa melhor_k
        resultados.append(r)
    return resultados