from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica
from saida.terminal import spinner_busca_local, spinner_busca_local_fim


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

    def _delta(self, inst, r, i, j) -> float:
        d = inst.grafo.dist
        dep = inst.id_deposito

        prev_i = r[i - 1] if i > 0 else dep
        next_j = r[j + 1] if j < len(r) - 1 else dep

        return (
            - d(prev_i, r[i]) - d(r[j], next_j)
            + d(prev_i, r[j]) + d(r[i], next_j)
        )

    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]
        custo_inicial = self.calcular_custo(inst, rotas, k_alvo)
        custo_atual = custo_inicial
        max_dist = getattr(inst, 'max_distancia', float('inf'))

        melhorou = True
        iteracao = 0
        while melhorou:
            melhorou = False
            iteracao += 1
            # spinner_busca_local(self.nome, iteracao, custo_atual, custo_inicial)

            for idx_rota, r in enumerate(rotas):
                if len(r) < 2:
                    continue

                for i in range(len(r) - 1):
                    for j in range(i + 1, len(r)):
                        delta = self._delta(inst, r, i, j)
                        if delta >= -1e-9:
                            continue

                        nova_rota = r[:i] + r[i:j+1][::-1] + r[j+1:]

                        # capacidade não muda na intra; só valida distância/autonomia
                        if max_dist != float('inf') and not self.validar_viabilidade(inst, nova_rota):
                            continue

                        custo_atual += delta
                        rotas[idx_rota] = nova_rota
                        r = nova_rota
                        melhorou = True
                        break

                    if melhorou:
                        break

                if melhorou:
                    break

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        # spinner_busca_local_fim(self.nome, custo_inicial, custo)
        return rotas, custo, n_veiculos