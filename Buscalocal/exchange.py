from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class Exchange(Heuristica):
    """
    Busca Local — Vizinhança Exchange (Swap)

    Troca dois clientes de posição, podendo estar na mesma rota (intra-rota)
    ou em rotas diferentes (inter-rota).
    |N(s)| = O(n²) por par de clientes.

    Para cada par (r1[i], r2[j]), remove os clientes de suas posições originais
    e os insere nas posições trocadas, recalculando as arestas afetadas.
    """

    nome = "Exchange"

    def __init__(self, construtivo: Heuristica, max_iter=100, max_moves_por_no=100, min_melhora_relativa=1e-4):
        self.construtivo = construtivo
        self.max_iter = max_iter
        self.max_moves_por_no = max_moves_por_no
        self.min_melhora_relativa = min_melhora_relativa

    def _delta_intra(self, inst, r, i, j) -> float:
        """Delta para troca dentro da mesma rota."""
        d = inst.grafo.dist
        dep = inst.id_deposito
        n = len(r)

        ci, cj = r[i], r[j]
        prev_i = r[i - 1] if i > 0 else dep
        next_i = r[i + 1] if i < n - 1 else dep
        prev_j = r[j - 1] if j > 0 else dep
        next_j = r[j + 1] if j < n - 1 else dep

        # Caso adjacente: os nós compartilham uma aresta (next_i == cj)
        if j == i + 1:
            return (
                - d(prev_i, ci) - d(ci, cj) - d(cj, next_j)
                + d(prev_i, cj) + d(cj, ci) + d(ci, next_j)
            )

        return (
            - d(prev_i, ci) - d(ci, next_i)
            - d(prev_j, cj) - d(cj, next_j)
            + d(prev_i, cj) + d(cj, next_i)
            + d(prev_j, ci) + d(ci, next_j)
        )

    def _delta_inter(self, inst, rotas, i_r1, i, i_r2, j) -> float:
        """Delta para troca entre rotas diferentes."""
        d = inst.grafo.dist
        dep = inst.id_deposito
        r1, r2 = rotas[i_r1], rotas[i_r2]

        ci, cj = r1[i], r2[j]
        prev_i = r1[i - 1] if i > 0 else dep
        next_i = r1[i + 1] if i < len(r1) - 1 else dep
        prev_j = r2[j - 1] if j > 0 else dep
        next_j = r2[j + 1] if j < len(r2) - 1 else dep

        return (
            - d(prev_i, ci) - d(ci, next_i)
            - d(prev_j, cj) - d(cj, next_j)
            + d(prev_i, cj) + d(cj, next_i)
            + d(prev_j, ci) + d(ci, next_j)
        )

    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]
        custo_inicial = self.calcular_custo(inst, rotas, k_alvo)

        moves_por_no = {c: 0 for c in inst.ids_clientes}
        custo_atual = custo_inicial
        iter_atual = 0
        melhorou = True

        while melhorou and iter_atual < self.max_iter:
            melhorou = False
            iter_atual += 1
            custo_anterior = custo_atual

            for i_r1 in range(len(rotas)):
                r1 = rotas[i_r1]

                for i in range(len(r1)):
                    ci = r1[i]
                    if moves_por_no[ci] >= self.max_moves_por_no:
                        continue

                    # --- Intra-rota ---
                    for j in range(i + 1, len(r1)):
                        cj = r1[j]
                        if moves_por_no[cj] >= self.max_moves_por_no:
                            continue

                        if self._delta_intra(inst, r1, i, j) >= -1e-9:
                            continue

                        nova_r1 = list(r1)
                        nova_r1[i], nova_r1[j] = nova_r1[j], nova_r1[i]

                        if not self.validar_viabilidade(inst, nova_r1):
                            continue

                        custo_atual += self._delta_intra(inst, r1, i, j)
                        rotas[i_r1] = nova_r1
                        r1 = nova_r1
                        moves_por_no[ci] += 1
                        moves_por_no[cj] += 1
                        melhorou = True
                        break

                    if melhorou:
                        break

                    # --- Inter-rota ---
                    for i_r2 in range(len(rotas)):
                        if i_r2 == i_r1:
                            continue
                        r2 = rotas[i_r2]

                        for j in range(len(r2)):
                            cj = r2[j]
                            if moves_por_no[cj] >= self.max_moves_por_no:
                                continue

                            # Verifica viabilidade de capacidade antes do delta
                            demanda_ci = inst.grafo.nos[ci].demanda
                            demanda_cj = inst.grafo.nos[cj].demanda
                            carga_r1 = sum(inst.grafo.nos[c].demanda for c in r1)
                            carga_r2 = sum(inst.grafo.nos[c].demanda for c in r2)

                            if carga_r1 - demanda_ci + demanda_cj > inst.capacidade:
                                continue
                            if carga_r2 - demanda_cj + demanda_ci > inst.capacidade:
                                continue

                            if self._delta_inter(inst, rotas, i_r1, i, i_r2, j) >= -1e-9:
                                continue

                            nova_r1 = list(r1)
                            nova_r2 = list(r2)
                            nova_r1[i], nova_r2[j] = cj, ci

                            if not self.validar_viabilidade(inst, nova_r1):
                                continue
                            if not self.validar_viabilidade(inst, nova_r2):
                                continue

                            custo_atual += self._delta_inter(inst, rotas, i_r1, i, i_r2, j)
                            rotas[i_r1] = nova_r1
                            rotas[i_r2] = nova_r2
                            r1 = nova_r1
                            moves_por_no[ci] += 1
                            moves_por_no[cj] += 1
                            melhorou = True
                            break

                        if melhorou:
                            break

                    if melhorou:
                        break
                if melhorou:
                    break

            # Critério de qualidade: para se a melhoria relativa for desprezível
            gap = (custo_anterior - custo_atual) / custo_anterior if custo_anterior > 0 else 0
            if melhorou and gap < self.min_melhora_relativa:
                break

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        print(f"[Exchange] {self.construtivo.nome}: {custo_inicial:.2f} → {custo:.2f}  (melhora: {custo_inicial - custo:.2f})")
        return rotas, custo, n_veiculos