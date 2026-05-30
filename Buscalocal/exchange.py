from typing import List, Tuple, Optional
from Heuristicas.Heuristica import Heuristica
from saida.terminal import spinner_busca_local, spinner_busca_local_fim


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
        max_dist = getattr(inst, 'max_distancia', float('inf'))

        moves_por_no = {c: 0 for c in inst.ids_clientes}

        # Ponto 1: cargas calculadas uma vez e mantidas atualizadas pontualmente
        cargas = {
            idx: sum(inst.grafo.nos[c].demanda for c in r)
            for idx, r in enumerate(rotas)
        }

        custo_atual = custo_inicial
        iter_atual = 0
        melhorou = True

        while melhorou and iter_atual < self.max_iter:
            melhorou = False
            iter_atual += 1
            custo_anterior = custo_atual
            spinner_busca_local(self.nome, iter_atual, custo_atual, custo_inicial)

            for i_r1 in range(len(rotas)):
                r1 = rotas[i_r1]

                for i in range(len(r1)):
                    ci = r1[i]
                    if moves_por_no[ci] >= self.max_moves_por_no:
                        continue

                    demanda_ci = inst.grafo.nos[ci].demanda

                    # --- Intra-rota ---
                    movimento_intra = None
                    for j in range(i + 1, len(r1)):
                        cj = r1[j]
                        if moves_por_no[cj] >= self.max_moves_por_no:
                            continue

                        delta = self._delta_intra(inst, r1, i, j)
                        if delta >= -1e-9:
                            continue

                        nova_r1 = list(r1)
                        nova_r1[i], nova_r1[j] = nova_r1[j], nova_r1[i]

                        # capacidade não muda na intra; só valida distância/autonomia
                        if max_dist != float('inf') and not self.validar_viabilidade(inst, nova_r1):
                            continue

                        movimento_intra = (j, delta, nova_r1)
                        break

                    if movimento_intra is not None:
                        j, delta, nova_r1 = movimento_intra
                        cj = r1[j]
                        custo_atual += delta
                        rotas[i_r1] = nova_r1
                        r1 = nova_r1
                        moves_por_no[ci] += 1
                        moves_por_no[cj] += 1
                        # carga não muda na intra
                        melhorou = True
                        break

                    # --- Inter-rota ---
                    # Ponto 2: detecção separada da aplicação — ci e estado
                    # permanecem consistentes independente do first-improvement
                    movimento_inter = None
                    for i_r2 in range(len(rotas)):
                        if i_r2 == i_r1:
                            continue
                        r2 = rotas[i_r2]

                        for j in range(len(r2)):
                            cj = r2[j]
                            if moves_por_no[cj] >= self.max_moves_por_no:
                                continue

                            demanda_cj = inst.grafo.nos[cj].demanda

                            if cargas[i_r1] - demanda_ci + demanda_cj > inst.capacidade:
                                continue
                            if cargas[i_r2] - demanda_cj + demanda_ci > inst.capacidade:
                                continue

                            delta = self._delta_inter(inst, rotas, i_r1, i, i_r2, j)
                            if delta >= -1e-9:
                                continue

                            nova_r1 = list(r1)
                            nova_r2 = list(r2)
                            nova_r1[i], nova_r2[j] = cj, ci

                            if max_dist != float('inf'):
                                if not self.validar_viabilidade(inst, nova_r1):
                                    continue
                                if not self.validar_viabilidade(inst, nova_r2):
                                    continue

                            movimento_inter = (i_r2, j, delta, nova_r1, nova_r2, demanda_ci, demanda_cj)
                            break

                        if movimento_inter is not None:
                            break

                    if movimento_inter is not None:
                        i_r2, j, delta, nova_r1, nova_r2, demanda_ci, demanda_cj = movimento_inter
                        cj = rotas[i_r2][j]
                        custo_atual += delta
                        rotas[i_r1] = nova_r1
                        rotas[i_r2] = nova_r2
                        # Ponto 1: atualização pontual das cargas
                        cargas[i_r1] = cargas[i_r1] - demanda_ci + demanda_cj
                        cargas[i_r2] = cargas[i_r2] - demanda_cj + demanda_ci
                        moves_por_no[ci] += 1
                        moves_por_no[cj] += 1
                        melhorou = True
                        break

                if melhorou:
                    break

            # Para se a melhoria relativa for desprezível
            gap = (custo_anterior - custo_atual) / custo_anterior if custo_anterior > 0 else 0
            if melhorou and gap < self.min_melhora_relativa:
                break

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        spinner_busca_local_fim(self.nome, custo_inicial, custo)
        return rotas, custo, n_veiculos