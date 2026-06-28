from typing import List, Optional, Tuple

from Heuristicas.Heuristica import Heuristica
from Heuristicas.clarke_wright import ClarkeWright
from Buscalocal.two_opt import TwoOpt


class GRASP(Heuristica):
    """
    GRASP (Greedy Randomized Adaptive Search Procedure) para o CVRP.

    Repete, por max_iter iterações, o par:
      1. Construção gulosa randomizada — Clarke & Wright com seleção via RCL (alpha);
      2. Busca local — 2-Opt aplicado sobre a solução construída.
    Ao final, retorna a melhor solução encontrada entre todas as iterações.

    A diversidade entre iterações vem da randomização da construção (k_rcl): cada
    chamada à construtiva parte de um ponto diferente, e a busca local refina cada
    um até um ótimo local. Com muitas iterações, varre-se vários ótimos locais.

    Parâmetros:
      k_rcl    — tamanho da RCL na construção (1 = guloso; 2 = melhor em testes).
      max_iter — número de iterações GRASP.
    """

    nome = "GRASP-CW-2OPT"

    def __init__(self, k_rcl: int = 2, max_iter: int = 50):
        self.k_rcl = k_rcl
        self.max_iter = max_iter
        self.construtivo = ClarkeWright(k_rcl=k_rcl)
        self.busca_local = TwoOpt()

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        melhor_rotas = None
        melhor_custo = float('inf')

        for _ in range(self.max_iter):
            rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
            rotas, custo = self.busca_local.melhorar(inst, rotas, k_alvo)

            if custo < melhor_custo:
                melhor_custo = custo
                melhor_rotas = [list(r) for r in rotas]

        return melhor_rotas, melhor_custo, len(melhor_rotas)
