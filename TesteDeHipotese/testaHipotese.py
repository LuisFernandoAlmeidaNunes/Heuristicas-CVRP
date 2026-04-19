
import os
import sys

# Garante que a raiz do projeto está no path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from instancesConfig import ARQUIVO_DAT
from metodos.friedman import friedman
from utils import load_data 

def testaHipotese():
    data = load_data(ARQUIVO_DAT)
    return friedman(data)

# teste
testaHipotese()