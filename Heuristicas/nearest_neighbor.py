from typing import List, Tuple
from heuristicas.Heuristica import Heuristica


class NearestNeighbor(Heuristica):
    """
    Heurística construtiva Vizinho Mais Próximo (Nearest Neighbor):
    1. Inicia uma rota a partir do depósito (0)
    2. Seleciona, entre os clientes não atendidos, o mais próximo do último cliente visitado
    3. Adiciona o cliente à rota, respeitando a capacidade do veículo
    4. Repete o processo até não ser possível inserir mais clientes na rota
    5. Retorna ao depósito e inicia uma nova rota com os clientes restantes
    6. Continua até que todos os clientes sejam atendidos
    """
    nome = "NN (Nearest Neighbor)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo

        nao_visitados = set(inst.ids_clientes)
        rotas = []

        while nao_visitados:
            rota = []
            carga = 0
            atual = deposito

            while True:
                candidatos = [
                    c for c in nao_visitados
                    if carga + grafo.nos[c].demanda <= capacidade
                ]

                if not candidatos:
                    break

                proximo = min(candidatos, key=lambda c: grafo.dist(atual, c))

                rota.append(proximo)
                carga += grafo.nos[proximo].demanda
                nao_visitados.remove(proximo)
                atual = proximo

            if rota:  # evita rotas vazias
                rotas.append(rota)
            elif nao_visitados:  # evita loop infinito
                # Cliente inviável: remove o de menor demanda (ou lança erro)
                raise ValueError(
                    f"Cliente inviável detectado demanda excede capacidade {capacidade}"
                )

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos