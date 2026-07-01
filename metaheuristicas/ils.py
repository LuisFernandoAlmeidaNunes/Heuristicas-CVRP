import random
from typing import List, Optional, Tuple

from Heuristicas.Heuristica import Heuristica
from Heuristicas.clarke_wright import ClarkeWright
from Buscalocal.two_opt import TwoOpt


class ILS(Heuristica):
    """
    ILS (Iterated Local Search) para o CVRP com restrição de duração de rota.

    Estrutura do algoritmo:
      1. Solução inicial — Clarke & Wright guloso + 2-Opt.
      2. Loop por max_iter iterações:
           a. Perturbação Double-Bridge — corta e reconecta 4 arestas entre
              duas rotas distintas, criando uma perturbação estrutural forte
              que o 2-Opt não consegue desfazer (Lourenço et al., 2003).
           b. Busca local — 2-Opt sobre a solução perturbada.
           c. Critério de aceitação — aceita se melhorar o incumbente.
      3. Retorna o melhor incumbente encontrado.

    POR QUE DOUBLE-BRIDGE E NÃO OR-OPT?
    O Or-Opt (realocar 1-3 clientes) cria perturbações que o 2-Opt consegue
    desfazer facilmente — o algoritmo sempre volta ao mesmo ótimo local.
    O Double-Bridge corta 4 arestas e reconecta os segmentos em ordem diferente,
    criando uma solução que está FORA da vizinhança 2-Opt do incumbente.
    Isso garante que o 2-Opt converge para um ótimo local genuinamente diferente.

    Esta é a perturbação padrão do ILS para VRP na literatura
    (Lourenço, Martin & Stützle, 2003 — Handbook of Metaheuristics).

    DIFERENÇA FUNDAMENTAL EM RELAÇÃO AO GRASP:
    O GRASP gera diversidade na CONSTRUÇÃO (RCL randomizada a cada iteração).
    O ILS gera diversidade na PERTURBAÇÃO (Double-Bridge sobre o incumbente).
    O GRASP parte sempre do zero; o ILS parte sempre do incumbente atual.

    Parâmetros:
      max_iter — número de iterações do loop principal.
    """

    nome = "ILS-CW-2OPT"

    def __init__(self, max_iter: int = 50):
        self.max_iter = max_iter
        self.construtivo = ClarkeWright()
        self.busca_local = TwoOpt()

    # ------------------------------------------------------------------ #
    #  PERTURBAÇÃO DOUBLE-BRIDGE                                           #
    # ------------------------------------------------------------------ #

    def _double_bridge(self, inst, rotas: List[List[int]]) -> List[List[int]]:
        """
        Perturbação Double-Bridge adaptada ao CVRP multi-rota.

        Versão intra-rota (rota com >= 8 clientes):
          Dada uma rota [A | B | C | D], corta em 4 pontos e reconecta como
          [A | C | B | D] — isso é equivalente ao Double-Bridge clássico do TSP
          e produz uma solução fora da vizinhança 2-Opt.

        Versão inter-rota (duas rotas com >= 2 clientes cada):
          Troca sufixos entre duas rotas distintas:
          Rota i: [A | B]  →  [A | D]
          Rota j: [C | D]  →  [C | B]
          Isso cria uma perturbação estrutural entre rotas que o 2-Opt intra-rota
          nunca exploraria, pois opera apenas dentro de cada rota.

        Valida viabilidade após a perturbação. Se inviável, tenta a outra
        variante. Retorna a solução original se nenhuma perturbação for viável.
        """
        rotas = [list(r) for r in rotas]

        # Tenta Double-Bridge intra-rota primeiro (rota com >= 8 clientes)
        candidatas_intra = [i for i, r in enumerate(rotas) if len(r) >= 8]
        random.shuffle(candidatas_intra)

        for idx in candidatas_intra:
            r = rotas[idx]
            n = len(r)
            # Escolhe 4 pontos de corte distintos
            cortes = sorted(random.sample(range(1, n), 3))
            a, b, c = cortes
            # Reconecta como Double-Bridge: A+C+B+D
            nova_rota = r[:a] + r[b:c] + r[a:b] + r[c:]
            if self.validar_viabilidade(inst, nova_rota):
                rotas[idx] = nova_rota
                return rotas

        # Tenta troca de sufixos inter-rota
        candidatas_inter = [i for i, r in enumerate(rotas) if len(r) >= 2]
        if len(candidatas_inter) >= 2:
            random.shuffle(candidatas_inter)
            for tentativa in range(min(10, len(candidatas_inter))):
                idx_i = candidatas_inter[tentativa]
                idx_j = random.choice([x for x in candidatas_inter if x != idx_i])

                rota_i = rotas[idx_i]
                rota_j = rotas[idx_j]

                # Ponto de corte aleatório em cada rota
                corte_i = random.randint(1, len(rota_i) - 1)
                corte_j = random.randint(1, len(rota_j) - 1)

                # Troca sufixos
                nova_i = rota_i[:corte_i] + rota_j[corte_j:]
                nova_j = rota_j[:corte_j] + rota_i[corte_i:]

                if (nova_i and nova_j and
                        self.validar_viabilidade(inst, nova_i) and
                        self.validar_viabilidade(inst, nova_j)):
                    rotas[idx_i] = nova_i
                    rotas[idx_j] = nova_j
                    return rotas

        # Nenhuma perturbação viável — retorna sem modificar
        return rotas

    # ------------------------------------------------------------------ #
    #  PONTO DE ENTRADA                                                    #
    # ------------------------------------------------------------------ #

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        # 1. Solução inicial — CW guloso + 2-Opt
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas, custo = self.busca_local.melhorar(inst, rotas, k_alvo)

        melhor_rotas = [list(r) for r in rotas]
        melhor_custo = custo

        # 2. Loop ILS com Double-Bridge
        for _ in range(self.max_iter):
            rotas_perturbadas = self._double_bridge(inst, melhor_rotas)
            rotas_perturbadas, custo_perturbado = self.busca_local.melhorar(
                inst, rotas_perturbadas, k_alvo
            )

            # Aceitação gulosa — aceita só se melhorar o incumbente
            if custo_perturbado < melhor_custo:
                melhor_custo = custo_perturbado
                melhor_rotas = [list(r) for r in rotas_perturbadas]

        return melhor_rotas, melhor_custo, len(melhor_rotas)