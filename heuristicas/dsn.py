from typing import List, Tuple
from heuristicas.Heuristica import Heuristica

class Dsn(Heuristica):
    nome = "DSN (Distance Savings Nearest)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo

        # 1. Distâncias ao depósito
        distancias_deposito = {
            id_no: grafo.dist(deposito, id_no)
            for id_no in inst.ids_clientes
        }

        # 2. Ordena: mais distante primeiro
        clientes_desalocados = sorted(
            inst.ids_clientes,
            key=lambda id_no: distancias_deposito[id_no],
            reverse=True
        )

        rotas = []

        while clientes_desalocados:
            mais_distante = clientes_desalocados.pop(0)
            cluster = [mais_distante]
            carga = grafo.nos[mais_distante].demanda

            while clientes_desalocados:
                melhor = None
                melhor_dist = float("inf")

                for id_no in clientes_desalocados:
                    for id_cluster in cluster:
                        dist = grafo.dist(id_no, id_cluster)
                        if dist < melhor_dist:
                            melhor_dist = dist
                            melhor = id_no

                if melhor is None:
                    break

                demanda_melhor = grafo.nos[melhor].demanda
                if carga + demanda_melhor <= capacidade:
                    cluster.append(melhor)
                    carga += demanda_melhor
                    clientes_desalocados.remove(melhor)
                else:
                    break

            rotas.append(cluster)


        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos