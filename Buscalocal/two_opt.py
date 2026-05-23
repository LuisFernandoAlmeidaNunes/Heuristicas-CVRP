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

        melhorou = True
        while melhorou:
            melhorou = False

            for idx_rota, r in enumerate(rotas):
                if len(r) < 2:
                    continue

                for i in range(len(r) - 1):
                    for j in range(i + 1, len(r)):

                        if self._delta(inst, r, i, j) >= -1e-9:
                            continue

                        nova_rota = r[:i] + r[i:j+1][::-1] + r[j+1:]

                        if not self.validar_viabilidade(inst, nova_rota):
                            continue

                        rotas[idx_rota] = nova_rota
                        r = nova_rota
                        melhorou = True
                        break

                    if melhorou:
                        break

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        print(f"[2-Opt] {self.construtivo.nome}: {custo_inicial:.2f} → {custo:.2f}  (melhora: {custo_inicial - custo:.2f})")
        return rotas, custo, n_veiculos