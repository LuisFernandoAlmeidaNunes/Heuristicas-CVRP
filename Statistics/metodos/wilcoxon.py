from itertools import combinations

from numpy.typing import NDArray
import numpy as np  
import math

from utils import rank

"""
Teste de Wilcoxon
args:   dict: dicionário de dados retornado pelo teste de Friedman.
        alpha: nível de significância para o teste (0.05/n_testes).
"""
def wilcoxon(dist: NDArray[np.float64], alpha: float):
    """Executa o teste de Wilcoxon para comparações par a par entre os métodos .

    Args:
        dict (dict): Dicionário contendo os resultados do teste de Friedman.
        alpha (float): Nível de significância para o teste.

    Retorna:
        Dict com os resultados do teste.

    """
    n_metodos = dist.shape[1]
    
    results = {}

    for i, j in combinations(range(n_metodos), 2):
        x = dist[:, i]
        y = dist[:, j]

        # problema de minimizacão: inverte os sinais
        d = y - x

        d = d[d != 0]

        # módulo
        abs_d = np.abs(d)

        # rankeia os valores absolutos
        ranks = rank(abs_d, axis=0)

        # soma dividida por sinal
        W_pos = np.sum(ranks[d > 0])
        W_neg = np.sum(ranks[d < 0])

        # menor valor dos w's
        W = min(W_pos, W_neg)

        n = len(d)
        mean_W = n * (n + 1) / 4
        var_W = n * (n + 1) * (2 * n + 1) / 24

        # z score
        z = (W - mean_W) / math.sqrt(var_W)


        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))

        results[(i, j)] = {
            "W": W,
            "p": p,
            "i_melhor": W_pos,
            "j_melhor": W_neg
        }

    return results
