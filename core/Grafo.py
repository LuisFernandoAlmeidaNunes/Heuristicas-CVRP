import numpy as np


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
        self.nos = {}       # {id: No}
        self._matriz = None

    def adicionar_no(self, no: No):
        self.nos[no.id] = no

    def construir_arestas(self):
        ids = list(self.nos.keys())
        n = max(ids)  # IDs vão de 1..n

        # Aloca n+1 para usar ID como índice direto (ignora linha/coluna 0)
        coords = np.zeros((n + 1, 2), dtype=np.float32)
        for id_no, no in self.nos.items():
            coords[id_no] = [no.x, no.y]

        # Calcula matriz de distâncias vetorizada
        xy = coords[1:]  # fatia 1..n para o broadcasting
        dx = xy[:, 0:1] - xy[:, 0]
        dy = xy[:, 1:2] - xy[:, 1]
        matriz_nn = np.sqrt(dx**2 + dy**2).astype(np.float32)

        # Insere de volta em matriz n+1 com offset
        self._matriz = np.zeros((n + 1, n + 1), dtype=np.float32)
        self._matriz[1:, 1:] = matriz_nn

    def dist(self, i: int, j: int) -> float:
        return float(self._matriz[i, j])

    @property
    def n_arestas(self) -> int:
        n = self._matriz.shape[0] - 1  # desconta o offset
        return n * n  # grafo completo com self-loops