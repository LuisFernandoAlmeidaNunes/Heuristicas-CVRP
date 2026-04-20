import numpy as np
from numpy.typing import NDArray
import pandas as pd
from scipy.stats import rankdata

def load_data(path, ordem):
    """
    Carrega os dados do arquivo e os organiza em uma tabela.
    Args:
        path (str): Caminho para o arquivo de dados.
    Returns:
        pd.DataFrame: Tabela organizada com as instâncias e métodos.
    """

    # metrica a ser analisada
    metrica = "GAP"

    # lê o arquivo 
    df = pd.read_csv(path, sep=r"\t", engine="python")

    # pivot: linhas = instância, colunas = método
    tabela= df.pivot(index="INSTANCE", columns="METHOD", values=metrica)
    dist = tabela.to_numpy()

    tabela = tabela[ordem]
    for i, col in enumerate(tabela.columns):
        print(f"{i}: {col}")

    return dist

def rank(dist: NDArray[np.float64], axis: int = 0):
    """
    Calcula os rankings das observações.

    Args:
        dist (Dados): Dados a serem classificados.
        axis (int): Eixo ao longo do qual os rankings são calculados (0 para colunas, 1 para linhas).

    Returns:
        Array com rankings estatisticamente corretos.
    """

    return np.apply_along_axis(rankdata, axis=axis, arr=dist)

"""
Função para calcular o ranking global a partir dos resultados do teste de Wilcoxon.
Args:
    results: dicionário de resultados do teste de Wilcoxon.
    alpha: nível de significância para considerar uma diferença como significativa.
returns:
    lista de tuplas (método, pontuação) ordenada do pior para o melhor método
"""
# Entrada
# results[(i, j)] = {
#             "W": float(W), # menor valor entre W_pos e W_neg
#             "p": float(p), # p-valor do teste de Wilcoxon para a comparação entre os métodos i e j
#             "i_melhor": float(W_pos), # Se W_pos < W_neg, o método i é melhor
#             "j_melhor": float(W_neg) # Se W_neg < W_pos, o método j é melhor
#         }
def ranking_wilcoxon(results, alpha):
    
    
    scores = {}

    for (i, j), res in results.items():

        # ignora se não for significativo
        if res["p"] > alpha:
            continue

        # inicializa
        scores.setdefault(i, 0)
        scores.setdefault(j, 0)

        # compara
        if res["W_pos"] > res["W_neg"]:
            scores[i] += 1
        else:
            scores[j] += 1

    # ordena do pior → melhor
    ranking = [k for k, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

    return ranking