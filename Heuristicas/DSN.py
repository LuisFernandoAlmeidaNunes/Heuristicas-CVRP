
''' Heuristica de construção DSN (Distance Savings Nearest) 
Ideia geral:
    1. ordena clientes por distância do depósito (mais distante primeiro)
    2. começa cluster pelo mais distante
    3. cresce o cluster pelo vizinho mais próximo
    4. quando capacidade estourar → fecha rota, começa nova
    5. calcula custo total
'''
from Instacia import Instancia
from Arestas import read_file

# recebe a instancia geral do problema 
class DSN(inst):
    