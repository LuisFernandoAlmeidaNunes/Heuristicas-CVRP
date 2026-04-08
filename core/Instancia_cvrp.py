"""
Cria uma isntância do CRVP armazenando tudo no objeto Grafo, em memória
"""

# TODO: está com erro de leitura genérica de instâncias, só funciona com int positivo. Tem que corrigir isso para conseguir ler as outras instâncias e armazenar corretamente
from core.Grafo import Grafo, No

class InstanciaCvrp:
    def __init__(self, nome: str, capacidade: int, id_deposito: int, grafo: Grafo):
        self.nome = nome
        self.capacidade = capacidade
        self.id_deposito = id_deposito
        self.grafo = grafo
        self.ids_clientes = [i for i in grafo.nos if i != id_deposito]

    @classmethod
    def ler_arquivo(cls, caminho: str):
        nome = ""
        capacidade = 0
        id_deposito = None

        coordenadas = {}
        demandas = {}

        tipo_distancia = None
        formato_peso = None

        modo = None
        pesos = []

        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()

                if not linha:
                    continue

                # ---------------- HEADERS ----------------
                if linha.startswith("NAME"):
                    nome = linha.split(":", 1)[1].strip()

                elif linha.startswith("CAPACITY"):
                    capacidade = int(linha.split(":", 1)[1].strip())

                elif linha.startswith("EDGE_WEIGHT_TYPE"):
                    tipo_distancia = linha.split(":", 1)[1].strip()

                elif linha.startswith("EDGE_WEIGHT_FORMAT"):
                    formato_peso = linha.split(":", 1)[1].strip()

                # ---------------- MODOS ----------------
                elif linha.startswith("NODE_COORD_SECTION"):
                    modo = "coord"

                elif linha.startswith("DEMAND_SECTION"):
                    modo = "demanda"

                elif linha.startswith("DEPOT_SECTION"):
                    modo = "deposito"

                elif linha.startswith("EDGE_WEIGHT_SECTION"):
                    modo = "pesos"

                elif linha == "EOF":
                    break

                # ---------------- LEITURA ----------------
                elif modo == "coord":
                    i, x, y = linha.split()
                    coordenadas[int(i)] = (float(x), float(y))

                elif modo == "demanda":
                    i, d = linha.split()
                    demandas[int(i)] = int(d)

                elif modo == "deposito":
                    if linha != "-1":
                        id_deposito = int(linha)

                elif modo == "pesos":
                    valores = list(map(float, linha.split()))
                    pesos.extend(valores)

        # ---------------- VALIDAÇÕES ----------------
        if tipo_distancia is None:
            raise ValueError("EDGE_WEIGHT_TYPE não encontrado")

        grafo = Grafo()

        # ==========================================================
        # ✅ CASO 1: EUC_2D (coordenadas)
        # ==========================================================
        if tipo_distancia == "EUC_2D":

            if not coordenadas:
                raise ValueError("Instância EUC_2D sem coordenadas")

            if demandas and len(demandas) != len(coordenadas):
                print("⚠️ Aviso: número de demandas diferente de nós")

            for id_no, (x, y) in coordenadas.items():
                if demandas:
                    demanda = demandas[id_no]  # força erro se faltar
                else:
                    demanda = 0

                grafo.adicionar_no(No(id_no, x, y, demanda))

            grafo.construir_arestas()

        # ==========================================================
        # ✅ CASO 2: EXPLICIT (matriz de distância)
        # ==========================================================
        elif tipo_distancia == "EXPLICIT":

            if formato_peso != "LOWER_ROW":
                raise NotImplementedError(f"Formato {formato_peso} não suportado")

            if not pesos:
                raise ValueError("EDGE_WEIGHT_SECTION vazio")

            # descobrir dimensão
            n = int((1 + (1 + 8 * len(pesos)) ** 0.5) / 2)

            matriz = [[0.0] * (n + 1) for _ in range(n + 1)]

            idx = 0
            for i in range(2, n + 1):
                for j in range(1, i):
                    matriz[i][j] = pesos[idx]
                    matriz[j][i] = pesos[idx]
                    idx += 1

            # cria nós fictícios (sem coordenada real)
            for i in range(1, n + 1):
                demanda = demandas.get(i, 0)
                grafo.adicionar_no(No(i, 0.0, 0.0, demanda))

            import numpy as np
            grafo.construir_arestas_explicitas(np.array(matriz, dtype=np.float64))

        else:
            raise NotImplementedError(f"Tipo {tipo_distancia} não suportado")

        # ---------------- DEPÓSITO ----------------
        if id_deposito is None:
            raise ValueError("DEPOT_SECTION não encontrado")

        return cls(nome, capacidade, id_deposito, grafo)