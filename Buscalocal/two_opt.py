from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class TwoOpt(Heuristica):
    """
    Busca Local — Vizinhança 2-Opt

    Inverte um segmento dentro de uma mesma rota (intra-rota).
    |N(s)| = O(n²) por rota, onde n = clientes na rota.

    Para cada par (i, j), remove as arestas (r[i-1]→r[i]) e (r[j]→r[j+1])
    e reconecta invertendo o segmento r[i..j].
    """

    nome = "2opt"

    def __init__(self, construtivo: Heuristica):
        self.construtivo = construtivo

    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]

        melhorou = True
        while melhorou:
            melhorou = False

            # TODO: iterar sobre cada rota r em rotas
            # TODO: iterar sobre i de 0 até len(r) - 2
            # TODO: iterar sobre j de i+1 até len(r) - 1
            #
            # Montar candidato:
            #   nova_rota = r[:i] + r[i:j+1][::-1] + r[j+1:]
            #   (inverte o segmento entre os índices i e j, inclusive)
            #
            # Verificar:
            #   self.validar_viabilidade(inst, nova_rota)
            #   (capacidade não muda, mas max_distancia pode mudar)
            #
            # Calcular delta de custo:
            #   custo_antes = calcular_custo(inst, [r], k_alvo)
            #   custo_depois = calcular_custo(inst, [nova_rota], k_alvo)
            #   se custo_depois < custo_antes → aplicar e marcar melhorou = True
            #
            # DICA: first-improvement → break assim que encontrar melhora na rota

            pass

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        return rotas, custo, n_veiculos
