import numpy as np


class No:
    """Estrutura básica do nó para formação do grafo"""
    def __init__(self, id_no: int, x: float, y: float, demanda: int = 0):
        self.id = id_no
        self.x = x
        self.y = y
        self.demanda = demanda

    def __repr__(self):
        return f"No(id={self.id}, x={self.x}, y={self.y}, demanda={self.demanda})"


class Grafo:
    """
    Este módulo implementa a infraestrutura de dados do Grafo.
    A opção pela Matriz densa (O(n²)) em vez de listas ou cálculo dinâmico justifica-se
    pelo acesso em tempo constante O(1) às distâncias, fundamental para o desempenho
    das heurísticas que realizam milhões de consultas por segundo.

    Os principais destaques técnicos desta implementação são:

    1. Estrutura Vetorizada (NumPy): Em vez de calcular distâncias sob demanda usando
       laços de repetição (loops), o módulo utiliza Broadcasting do NumPy para
       gerar a matriz de distâncias completa de uma só vez. Isso reduz drasticamente
       o tempo de processamento inicial, especialmente em instâncias com centenas de nós.

    2. Precisão de Ponto Flutuante: O uso de 'float64' garante uma precisão de até
       15 dígitos decimais, essencial para evitar erros acumulados de arredondamento
       que poderiam invalidar os resultados de Gaps muito pequenos ou o Teste de Hipótese.

    3. Localidade de Dados e Cache: Matrizes NumPy são armazenadas em blocos contíguos
       de memória. Isso favorece a "Localidade Espacial", permitindo que a CPU
       carregue dados vizinhos no Cache L1/L2 de forma eficiente. Listas de objetos
       em Python são espalhadas na memória (ponteiros), o que causa "Cache Misses"
       e degrada a performance em algoritmos de busca intensa.

    4. Vetorização SIMD: O uso de matrizes nos permite aplicar operações de álgebra
       linear e broadcasting do NumPy. Isso possibilita que a CPU processe múltiplos
       dados simultaneamente (Single Instruction, Multiple Data), algo impossível
       com estruturas de listas convencionais.

    Embora a matriz consuma mais memória (O(n²)), para o escopo de instâncias de
    CVRP (geralmente até algumas milhares de nós), o ganho em velocidade de execução
    justifica o tradeoff de memória.

    """
    def __init__(self):
        self.nos = {}            # {id_no: No}
        self._matriz = None      # np.ndarray (n x n), índice 0-based interno
        self._matriz_list = None # list[list[float]] — espelho da matriz p/ acesso escalar rápido
        self._bigTour = None     # matriz codificada para padrão big tour
        self._id_para_idx = {}   # {id_no -> índice interno}
        self._idx_para_id = []   # [id_no por índice interno]

    def adicionar_no(self, no: No):
        self.nos[no.id] = no

    def construir_arestas(self, fn_dist=None):
        """
        Constrói a matriz de distâncias vetorizada.
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

        # Espelho em lista Python pura: o acesso escalar matriz[i][j] é bem mais
        # rápido que a indexação escalar do NumPy + float() no caminho quente das
        # buscas locais (dist() é chamada dezenas de milhões de vezes).
        self._matriz_list = self._matriz.tolist()

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

        self._matriz_list = self._matriz.tolist()

    def codificar_matriz(self):
        self._big_tour = []
        for i, rota in enumerate(self._matriz):
            self._big_tour.extend(rota)
            # Adiciona o separador '0' entre as rotas, exceto no final
            if i < len(self._matriz) - 1:
                self._big_tour.append(0)
        return self._big_tour

    def dist(self, i: int, j: int) -> float:
        idx = self._id_para_idx
        return self._matriz_list[idx[i]][idx[j]]

    @property
    def n_arestas(self) -> int:
        n = len(self._idx_para_id)
        return n * n