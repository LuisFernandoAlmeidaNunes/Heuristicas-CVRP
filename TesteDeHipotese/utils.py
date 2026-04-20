import numpy as np
from numpy.typing import NDArray
import pandas as pd
from scipy.stats import rankdata

def load_data(path):
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
    ordem = [
        "CW (Clarke & Wright Savings)",
        "NN (Nearest Neighbor)",
        "MJ (Mole & Jameson)",
        "SW (Sweep)"
    ]

    tabela = tabela[ordem]
    print(tabela.columns)

    return dist

def calc_hipotese(p:float, alpha: float) -> bool:
    """Calcula a hipótese.

    Args:
        p (float): Valor-p do teste.
        alpha (float): Nível de significância.

    Returns:
        bool: True se a hipótese nula for rejeitada, False caso contrário.
    """
    return p < alpha

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