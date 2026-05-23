from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class Exchange(Heuristica):
    """
    Busca Local — Vizinhança Exchange (Swap)

    Troca dois clientes de rotas diferentes de posição (inter-rota).
    |N(s)| = O(n²), onde n = total de clientes.
    """

    nome = "Exchange"

    def __init__(self, construtivo: Heuristica):
        self.construtivo = construtivo

    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]

        melhorou = True
        while melhorou:
            melhorou = False

            # TODO: iterar sobre todos os pares de índices de rota (i_r1, i_r2), i_r1 < i_r2
            # TODO: iterar sobre o índice i_c de cada cliente em r1
            # TODO: iterar sobre o índice j_c de cada cliente em r2
            #
            # Montar candidatos:
            #   nova_r1 = cópia de r1 com r1[i_c] substituído por r2[j_c]
            #   nova_r2 = cópia de r2 com r2[j_c] substituído por r1[i_c]
            #
            # Verificar ambas:
            #   self.validar_viabilidade(inst, nova_r1)
            #   self.validar_viabilidade(inst, nova_r2)
            #
            # Calcular delta de custo:
            #   custo_antes = calcular_custo(inst, [r1, r2], k_alvo)
            #   custo_depois = calcular_custo(inst, [nova_r1, nova_r2], k_alvo)
            #   se custo_depois < custo_antes → aplicar e marcar melhorou = True
            #
            # DICA: first-improvement → break assim que encontrar melhora

            pass

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        return rotas, custo, n_veiculos
