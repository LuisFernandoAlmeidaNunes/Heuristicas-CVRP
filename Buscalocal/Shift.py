from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica
from saida.terminal import spinner_busca_local, spinner_busca_local_fim


class Shift(Heuristica):
    nome = "Shift"

    def __init__(self, construtivo: Heuristica):
        self.construtivo = construtivo

    def _delta(self, inst, rotas, i_r1, i_c, i_r2, pos, k_alvo):
        d = inst.grafo.dist
        dep = inst.id_deposito
        r1 = rotas[i_r1]
        r2 = rotas[i_r2]
        cliente = r1[i_c]

        prev1 = r1[i_c - 1] if i_c > 0 else dep
        next1 = r1[i_c + 1] if i_c < len(r1) - 1 else dep
        a = r2[pos - 1] if pos > 0 else dep
        b = r2[pos] if pos < len(r2) else dep

        delta_dist = (
            - d(prev1, cliente) - d(cliente, next1) + d(prev1, next1)
            + d(a, cliente) + d(cliente, b) - d(a, b)
        )

        delta_pen = 0.0
        if k_alvo is not None and len(r1) == 1:
            k = len(rotas)
            penalidade = len(inst.ids_clientes) * 0.1
            delta_pen = penalidade * (max(0, k - 1 - k_alvo) - max(0, k - k_alvo))

        return delta_dist + delta_pen

    def resolver(self, inst, k_alvo=None, max_moves_por_no=1000) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]
        custo_inicial = self.calcular_custo(inst, rotas, k_alvo)

        moves_por_no = {c: 0 for c in inst.ids_clientes}
        custo_atual = custo_inicial
        melhorou = True
        iteracao = 0
        while melhorou:
            melhorou = False
            iteracao += 1
            spinner_busca_local(self.nome, iteracao, custo_atual, custo_inicial)

            for i_r1, r1 in enumerate(rotas):
                for i_c in range(len(r1)):
                    cliente = r1[i_c]
                    if moves_por_no[cliente] >= max_moves_por_no:
                        continue

                    for i_r2, r2 in enumerate(rotas):
                        if i_r2 == i_r1:
                            continue

                        carga_r2 = sum(inst.grafo.nos[c].demanda for c in r2)
                        if inst.grafo.nos[cliente].demanda + carga_r2 > inst.capacidade:
                            continue

                        for pos in range(len(r2) + 1):
                            nova_r2 = r2[:pos] + [cliente] + r2[pos:]

                            if not self.validar_viabilidade(inst, nova_r2):
                                continue

                            delta = self._delta(inst, rotas, i_r1, i_c, i_r2, pos, k_alvo)
                            if delta < -custo_atual * 1e-16:  # Considera melhoria relativa
                            # if delta < -1e-9:  # Considera melhoria significativa
                                nova_r1 = r1[:i_c] + r1[i_c + 1:]
                                nova_rotas = [
                                    nova_r1 if j == i_r1 else (nova_r2 if j == i_r2 else r)
                                    for j, r in enumerate(rotas)
                                ]
                                rotas = [r for r in nova_rotas if r]
                                custo_atual += delta
                                moves_por_no[cliente] += 1
                                melhorou = True
                                break

                        if melhorou:
                            break
                    if melhorou:
                        break
                if melhorou:
                    break

        custo = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)
        spinner_busca_local_fim(self.nome, custo_inicial, custo)
        return rotas, custo, n_veiculos
