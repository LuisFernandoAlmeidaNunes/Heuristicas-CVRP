import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from instancesConfig import ARQUIVO_DAT
from metodos.friedman import friedman
from utils import load_data
from saida.graphics import plotar_friedman

def testaHipotese():
    data = load_data(ARQUIVO_DAT)
    resultado = friedman(data)
    print(f"Estatística de Friedman: {resultado['friedman'][0]:.4f}")
    print(f"Estatística de Iman-Davenport: {resultado['iman'][0]:.4f}")
    print(f"P-value: {resultado['p_value']:.6f}")
    print(f"Rejeita H0 (α=0.05): {resultado['p_value'] < 0.05}")
    plotar_friedman(resultado)
    return resultado

testaHipotese()