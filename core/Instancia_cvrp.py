"""
Cria uma instância do CVRP armazenando tudo no objeto Grafo, em memória.
Suporta os tipos de distância: EUC_2D (padrão), CEIL_2D, ATT e EXPLICIT.
Formatos explícitos suportados: LOWER_ROW, FULL_MATRIX, UPPER_ROW.
"""

import math
import numpy as np
from core.Grafo import Grafo, No


# ── Funções de distância ────────────────────────────────────────────────────

def _euc_2d(x1, y1, x2, y2) -> float:
    return math.hypot(x2 - x1, y2 - y1)

def _ceil_2d(x1, y1, x2, y2) -> float:
    """EUC_2D arredondado para cima — padrão de várias instâncias clássicas."""
    return math.ceil(math.hypot(x2 - x1, y2 - y1))

def _att(x1, y1, x2, y2) -> float:
    """Pseudo-euclidiana ATT conforme especificação TSPLIB."""
    xd, yd = x2 - x1, y2 - y1
    r = math.hypot(xd, yd) / 10.0
    t = round(r)
    return float(t + 1 if t < r else t)

_DIST_FUNC = {
    "EUC_2D":  None,        # ← BUG: vetorizado sem arredondamento
    "CEIL_2D": _ceil_2d,
    "ATT":     _att,
}

class InstanciaCvrp:
    def __init__(self, nome: str, capacidade: int, id_deposito: int, grafo: Grafo):
        self.nome = nome
        self.capacidade = capacidade
        self.id_deposito = id_deposito
        self.grafo = grafo
        self.ids_clientes = [i for i in grafo.nos if i != id_deposito]

    def __repr__(self):
        return (f"InstanciaCvrp(nome={self.nome!r}, "
                f"clientes={len(self.ids_clientes)}, "
                f"capacidade={self.capacidade})")

    @classmethod
    def ler_arquivo(cls, caminho: str):
        nome = ""
        capacidade = 0
        id_deposito = None
        coordenadas = {}
        demandas = {}
        tipo_distancia = "EUC_2D"   # ← BUG CORRIGIDO: antes lançava erro se ausente
        formato_peso = None
        pesos_brutos = []
        max_distancia = float('inf')  # Se não houver a chave DISTANCE, a autonomia é infinita
        tempo_servico = 0

        modo = None

        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("!") or linha.startswith("c "):
                    continue

                # ── cabeçalhos ──────────────────────────────────────────────
                if ":" in linha and modo != "pesos":
                    chave, _, valor = linha.partition(":")
                    chave = chave.strip().upper()
                    valor = valor.strip()

                    if chave == "NAME":
                        nome = valor
                    elif chave == "CAPACITY":
                        capacidade = int(valor)
                    elif chave == "EDGE_WEIGHT_TYPE":
                        tipo_distancia = valor.upper()
                    elif chave == "EDGE_WEIGHT_FORMAT":
                        formato_peso = valor.upper()
                    elif chave == "DISTANCE":
                        max_distancia = float(valor)
                    elif chave == "SERVICE_TIME":
                        tempo_servico = float(valor)
                    continue

                # ── marcadores de seção ─────────────────────────────────────
                linha_up = linha.upper()
                if linha_up == "NODE_COORD_SECTION":
                    modo = "coord"; continue
                elif linha_up == "DEMAND_SECTION":
                    modo = "demanda"; continue
                elif linha_up == "DEPOT_SECTION":
                    modo = "deposito"; continue
                elif linha_up == "EDGE_WEIGHT_SECTION":
                    modo = "pesos"; continue
                elif linha_up == "EOF":
                    break

                # ── dados ───────────────────────────────────────────────────
                if modo == "coord":
                    partes = linha.split()
                    coordenadas[int(partes[0])] = (float(partes[1]), float(partes[2]))

                elif modo == "demanda":
                    i, d = linha.split()
                    demandas[int(i)] = int(d)

                elif modo == "deposito":
                    if linha != "-1" and id_deposito is None:
                        id_deposito = int(linha)

                elif modo == "pesos":
                    pesos_brutos.extend(map(float, linha.split()))

        # ── validações básicas ──────────────────────────────────────────────
        if id_deposito is None:
            raise ValueError(f"DEPOT_SECTION não encontrado em {caminho}")

        # ── monta grafo ─────────────────────────────────────────────────────
        grafo = Grafo()

        if tipo_distancia == "EXPLICIT":
            grafo = cls._montar_grafo_explicit(
                demandas, pesos_brutos, formato_peso, coordenadas
            )

        elif tipo_distancia in _DIST_FUNC:
            if not coordenadas:
                raise ValueError(
                    f"Instância {tipo_distancia} sem NODE_COORD_SECTION em {caminho}"
                )
            for id_no, (x, y) in coordenadas.items():
                grafo.adicionar_no(No(id_no, x, y, demandas.get(id_no, 0)))
            grafo.construir_arestas(fn_dist=_DIST_FUNC[tipo_distancia])

        else:
            raise NotImplementedError(
                f"EDGE_WEIGHT_TYPE '{tipo_distancia}' não suportado."
            )

        return cls(nome, capacidade, id_deposito, grafo)

    @staticmethod
    def _montar_grafo_explicit(demandas, pesos_brutos, formato_peso, coordenadas):
        """Monta o grafo a partir de uma matriz de pesos explícita."""
        if not pesos_brutos:
            raise ValueError("EDGE_WEIGHT_SECTION vazio")

        n = len(demandas)
        ids_ordenados = sorted(demandas.keys())

        # Matriz indexada por ID (linha/col 0 é buffer)
        M = np.zeros((n + 1, n + 1), dtype=np.float32)

        fmt = (formato_peso or "LOWER_ROW").upper()

        if fmt == "FULL_MATRIX":
            for i, id_i in enumerate(ids_ordenados):
                for j, id_j in enumerate(ids_ordenados):
                    M[id_i, id_j] = pesos_brutos[i * n + j]

        elif fmt == "LOWER_ROW":
            idx = 0
            for row in range(1, n):        # linha 1..n-1
                id_i = ids_ordenados[row]
                for col in range(row):     # coluna 0..row-1
                    id_j = ids_ordenados[col]
                    M[id_i, id_j] = pesos_brutos[idx]
                    M[id_j, id_i] = pesos_brutos[idx]
                    idx += 1

        elif fmt == "UPPER_ROW":
            idx = 0
            for row in range(n - 1):
                id_i = ids_ordenados[row]
                for col in range(row + 1, n):
                    id_j = ids_ordenados[col]
                    M[id_i, id_j] = pesos_brutos[idx]
                    M[id_j, id_i] = pesos_brutos[idx]
                    idx += 1

        else:
            raise NotImplementedError(f"EDGE_WEIGHT_FORMAT '{fmt}' não suportado.")

        grafo = Grafo()
        for id_no in ids_ordenados:
            x, y = coordenadas.get(id_no, (0.0, 0.0))
            grafo.adicionar_no(No(id_no, x, y, demandas[id_no]))
        grafo.construir_arestas_explicitas(M)
        return grafo