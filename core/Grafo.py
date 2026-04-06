"""
estrutura de dados para armazenar o grafo.
Utilizada matriz pois CVRP euclidiano é grafo completo e nesse caso mais eficiente que lista de adjacências
"""
import math

class No:
    def __init__(self, id_no: int, x: float, y: float, demanda: int = 0):
        self.id = id_no
        self.x = x
        self.y = y
        self.demanda = demanda

    def __repr__(self):
        return f"No(id={self.id}, x={self.x}, y={self.y}, demanda={self.demanda})"


class Grafo:
    def __init__(self):
        self.nos = {}          # {id: No}
        self.arestas = {}      # {(i, j): distancia}

    def adicionar_no(self, no: No):
        self.nos[no.id] = no

    def construir_arestas(self):
        ids = list(self.nos.keys())
        for i in range(len(ids)):
            self.arestas[(ids[i], ids[i])] = 0.0
            for j in range(i + 1, len(ids)):
                no1 = self.nos[ids[i]]
                no2 = self.nos[ids[j]]
                dist = math.hypot(no2.x - no1.x, no2.y - no1.y)
                self.arestas[(ids[i], ids[j])] = dist
                self.arestas[(ids[j], ids[i])] = dist

    def dist(self, i: int, j: int) -> float:
        return self.arestas[(i, j)]