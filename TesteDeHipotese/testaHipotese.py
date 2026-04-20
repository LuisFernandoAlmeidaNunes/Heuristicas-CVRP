
from math import comb
import os
import sys

# Garante que a raiz do projeto está no path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from instancesConfig import ARQUIVO_DAT, HEURISTICAS
from TesteDeHipotese.metodos.friedman import friedman
from TesteDeHipotese.metodos.wilcoxon import wilcoxon
from TesteDeHipotese.utils import load_data, ranking_wilcoxon

def testaHipotese():
    ORDEM= [
        "CW (Clarke & Wright Savings)",
        "NN (Nearest Neighbor)",
        "MJ (Mole & Jameson)",
        "SW (Sweep)"
    ]
    data = load_data(ARQUIVO_DAT, ORDEM)
    friedman_result = friedman(data)
    wilcoxon_result = None
    ranking_global = None
    print("Iniciando teste de Friedman...")
    if friedman_result["p_value"] < 0.05:
        print("Diferenças significativas encontradas. \niniciando Wilcoxon...")

        bonferroni = 0.05 / comb(len(HEURISTICAS), 2)
        wilcoxon_result = wilcoxon(data, alpha=bonferroni)
        ranking_global = ranking_wilcoxon(wilcoxon_result, alpha=bonferroni)


        print("Teste de hipótese finalizado. \nRanking global dos métodos")
        for i in range(len(ranking_global)):
            if i < len(ranking_global) -1:
                print(f" {ORDEM[ranking_global[i]]} >", end="")
            else:
                print(f" {ORDEM[ranking_global[i]]}")
                
    return friedman_result, wilcoxon_result

# teste
# testaHipotese()
