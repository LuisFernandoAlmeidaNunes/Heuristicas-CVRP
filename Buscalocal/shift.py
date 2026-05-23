from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class Shift(Heuristica):
    """
    Busca Local — Vizinhança Shift (Relocate)

    Move um cliente de uma rota para outra (inter-rota).
    |N(s)| = O(n · r), onde n = clientes, r = número de rotas.
    """

    nome = "Shift"

    def __init__(self, construtivo: Heuristica):
        self.construtivo = construtivo

    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]

        melhorou = True
        while melhorou:
            melhorou = False

            # TODO: iterar sobre todos os índices de rota de origem (i_r1)
            # TODO: iterar sobre todos os índices de cliente (i_c) em r1
            # TODO: iterar sobre todos os índices de rota de destino (i_r2), i_r2 != i_r1
            # TODO: iterar sobre todas as posições de inserção (pos) em r2
            #
            # Montar candidatos:
            #   nova_r1 = r1 sem o cliente na posição i_c
            #   nova_r2 = r2 com o cliente inserido na posição pos
            #
            # Verificar:
            #   self.validar_viabilidade(inst, nova_r2)
            #
            # Calcular delta de custo:
            #   custo_antes = calcular_custo(inst, [r1, r2], k_alvo)
            #   custo_depois = calcular_custo(inst, [nova_r1, nova_r2], k_alvo)
            #   se custo_depois < custo_antes → aplicar e marcar melhorou = True
            #
            # DICA: após aplicar, remover rotas vazias de `rotas`
            # DICA: first-improvement → break assim que encontrar melhora

            pass

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        return rotas, custo, n_veiculos
