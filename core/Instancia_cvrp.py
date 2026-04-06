"""
Cria uma isntância do CRVP armazenando tudo no objeto Grafo, em memória
"""

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

        modo = None
        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()

                if not linha:
                    continue
                if linha.startswith("NAME"):
                    nome = linha.split(":", 1)[1].strip()
                elif linha.startswith("CAPACITY"):
                    capacidade = int(linha.split(":", 1)[1].strip())
                elif linha == "NODE_COORD_SECTION":
                    modo = "coord"
                elif linha == "DEMAND_SECTION":
                    modo = "demanda"
                elif linha == "DEPOT_SECTION":
                    modo = "deposito"
                elif linha == "EOF":
                    break
                elif modo == "coord":
                    i, x, y = linha.split()
                    coordenadas[int(i)] = (float(x), float(y))
                elif modo == "demanda":
                    i, d = linha.split()
                    demandas[int(i)] = int(d)
                elif modo == "deposito" and linha != "-1":
                    id_deposito = int(linha)

        grafo = Grafo()
        for id_no, (x, y) in coordenadas.items():
            demanda = demandas.get(id_no, 0)
            grafo.adicionar_no(No(id_no, x, y, demanda))

        grafo.construir_arestas()
        return cls(nome, capacidade, id_deposito, grafo)