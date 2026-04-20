
from math import comb
import os
import sys

# Garante que a raiz do projeto está no path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from instancesConfig import ARQUIVO_DAT, HEURISTICAS
from metodos.friedman import friedman
from metodos.wilcoxon import wilcoxon
from utils import load_data 

def testaHipotese():
    data = load_data(ARQUIVO_DAT)
    friedman_result = friedman(data)
    wilcoxon_result = None
    if friedman_result["p_value"] < 0.05:
        print("Diferenças significativas encontradas. Realizando teste de Wilcoxon para comparações par a par.")

        bonferroni = 0.05 / comb(len(HEURISTICAS), 2)
        wilcoxon_result = wilcoxon(data, alpha=bonferroni)

    return {
        "friedman": friedman_result,
        "wilcoxon": wilcoxon_result,
    }
# teste
testaHipotese()