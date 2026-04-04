from Arestas import Arestas

"""
Classe Instancia: guarda dados 
"""

class Instancia:
    def __init__(self):

        self.demandas = {} # é um dicionario pq cada clie. tem sua demanda
        self.ids_clientes = [] # lista pq é sequencial
        self.capacidade = 0 # capacidade max de um veiculo
        self.coordenadas = {} # dicionario com as coordenadas de cada cliente
        self.id_deposito = 0 # id do deposito - é 1 ou 0
        self.matriz = [] # matriz de distancias entre os cliente
        
        