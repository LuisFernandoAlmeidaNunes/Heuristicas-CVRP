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
        self.nos = {}            # {id_no: No}
        self._matriz = None      # np.ndarray (n x n), índice 0-based interno
        self._id_para_idx = {}   # {id_no -> índice interno}
        self._idx_para_id = []   # [id_no por índice interno]

    def adicionar_no(self, no: No):
        self.nos[no.id] = no

    def construir_arestas(self, fn_dist=None):
        """
        Constrói a matriz de distâncias vetorizada.

        fn_dist(x1, y1, x2, y2) -> float
            Função de distância customizada (CEIL_2D, ATT, etc.).
            Se None, usa EUC_2D vetorizado via numpy.

        CORREÇÕES em relação à versão anterior:
          1. float64 em vez de float32  → pra evitar erros de arrendodamento do float. (consegue uma precisão de até 15 digitos)
          2. Mapeamento id->índice explícito → suporta IDs não sequenciais
          3. Broadcasting (n,1,2)-(1,n,2) → legível e sem risco de inversão. (acho o problema relatado era esse)
        """
        ids = sorted(self.nos.keys())
        n = len(ids)

        self._id_para_idx = {id_no: idx for idx, id_no in enumerate(ids)} #parte aqui
        self._idx_para_id = ids

        coords = np.array(
            [[self.nos[id_no].x, self.nos[id_no].y] for id_no in ids],
            dtype=np.float64   # <- era float32
        )

        if fn_dist is None:
            # EUC_2D vetorizado — rápido e preciso
            # diff[i,j] = coords[i] - coords[j], shape (n, n, 2)
            diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :] # parte aqui tbm
            self._matriz = np.sqrt((diff ** 2).sum(axis=2))  # shape (n, n)
        else:
            # Tipos especiais (CEIL_2D, ATT): aplica a função escalar
            self._matriz = np.zeros((n, n), dtype=np.float64) # <- era float32
            for i in range(n):
                for j in range(i + 1, n):
                    d = fn_dist(coords[i, 0], coords[i, 1],
                                coords[j, 0], coords[j, 1])
                    self._matriz[i, j] = d
                    self._matriz[j, i] = d

    def construir_arestas_explicitas(self, matriz_por_id: np.ndarray):
        """
        Recebe matriz quadrada indexada pelo ID do nó (linha/coluna 0 é buffer).
        Converte para o índice interno 0-based.
        """
        ids = sorted(self.nos.keys())
        n = len(ids)
        self._id_para_idx = {id_no: idx for idx, id_no in enumerate(ids)}
        self._idx_para_id = ids

        self._matriz = np.zeros((n, n), dtype=np.float64) # <- era float32
        for i, id_i in enumerate(ids):
            for j, id_j in enumerate(ids):
                self._matriz[i, j] = float(matriz_por_id[id_i, id_j])

    def dist(self, i: int, j: int) -> float:
        return float(self._matriz[self._id_para_idx[i], self._id_para_idx[j]])

    @property
    def n_arestas(self) -> int:
        n = len(self._idx_para_id)
        return n * n