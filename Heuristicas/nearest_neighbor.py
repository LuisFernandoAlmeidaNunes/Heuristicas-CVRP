from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class NearestNeighbor(Heuristica):
    """
    Heurística construtiva Vizinho Mais Próximo (Nearest Neighbor):
    1. Inicia uma rota a partir do depósito
    2. Seleciona o cliente mais próximo do último visitado que AINDA CABE no veículo
    3. Continua até não haver mais nenhum cliente que caiba (não só o mais próximo)
    4. Fecha a rota e abre uma nova com os clientes restantes
    5. Repete até atender todos

    CORREÇÃO em relação à versão anterior:
      - O break antigo fechava a rota assim que o cliente MAIS PRÓXIMO não cabia,
        mesmo que outros clientes com demanda menor ainda coubessem.
      - Agora os candidatos são filtrados por capacidade restante antes de escolher
        o mais próximo, aproveitando melhor cada veículo.
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
                # Filtra TODOS os clientes que ainda cabem — não só o mais próximo
                candidatos = [
                    c for c in nao_visitados
                    if carga + grafo.nos[c].demanda <= capacidade
                ]

                # Só fecha a rota quando realmente não há mais nenhum que caiba
                if not candidatos:
                    break

                # Entre os que cabem, escolhe o mais próximo
                proximo = min(candidatos, key=lambda c: grafo.dist(atual, c))

                rota.append(proximo)
                carga += grafo.nos[proximo].demanda
                nao_visitados.remove(proximo)
                atual = proximo

            if rota:
                rotas.append(rota)
            elif nao_visitados:
                raise ValueError(
                    f"Cliente inviável: demanda excede capacidade {capacidade}"
                )

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos