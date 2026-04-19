import numpy as np
from utils import rank, load_data
from scipy.stats import f as f_dist

"""
Teste de Friedman
args:    dist: tabela de dados retornada pelo metodo.
"""

def friedman(dist):
    """Executa o teste de Friedman com rankins corretos estatisticamente e aplicando a estatistica de iman.

    Args:
        dist (Dados): Dados a serem analisados formatados pelo load_data do utils do teste de hipótese.

    Retorna:
        Dict com os dados do teste.

    """

    # ranqueia a entrada
    ranked = rank(dist)
        
    # dimensões da tabela
    n = ranked.shape[0]  # instâncias (linhas na tabela)
    k = ranked.shape[1]  # métodos (colunas na tabela)

    # rank médio por método
    R = np.mean(ranked, axis=0)

    # k-1 graus de liberdade
    df_friedman = k - 1
    df_iman = (k - 1, (k - 1) * (n - 1))

    # estatística de Friedman
    f = (
        12 * n * (np.sum(R**2) - (k * (k + 1)**2) / 4)
        / (k * (k + 1))
    )

    # Iman-Davenport
    iman = (n - 1) * f / (n * (k - 1) - f)

    p_value = 1 - f_dist.cdf(iman, df_friedman, df_iman[1])

    print("Friedman finalizado.")

    return {
        "friedman": (f, df_friedman),
        "iman": (iman, df_iman),
        "p_value": (p_value)
    }