from typing import List, Tuple, Optional
from collections import deque
from Heuristicas.Heuristica import Heuristica


class NearestNeighbor(Heuristica):
    nome = "NN (Nearest Neighbor)"

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        nao_visitados = set(inst.ids_clientes)
        rotas = []

        while nao_visitados:
            # 1. SEED: Começa a rota pelo cliente não visitado mais distante do depósito
            # padrão 'farthest'
            semente = max(nao_visitados, key=lambda c: grafo.dist(deposito, c))

            # Usamos deque para permitir inserir no início ou no fim
            rota_atual = deque([semente])
            nao_visitados.remove(semente)

            while nao_visitados:
                melhor_dist = float('inf')
                melhor_cliente = None
                no_inicio = False  # Flag para saber em qual ponta inserir

                primeiro = rota_atual[0]
                ultimo = rota_atual[-1]

                for c in nao_visitados:
                    # Checagem de viabilidade antes de calcular a distância
                    # (Pode testar no fim, se falhar, testa no início)

                    # Teste 1: Adicionar ao final
                    dist_fim = grafo.dist(ultimo, c)
                    if dist_fim < melhor_dist:
                        if self.validar_viabilidade(inst, list(rota_atual) + [c]):
                            melhor_dist = dist_fim
                            melhor_cliente = c
                            no_inicio = False

                    # Teste 2: Adicionar ao início
                    dist_ini = grafo.dist(c, primeiro)
                    if dist_ini < melhor_dist:
                        if self.validar_viabilidade(inst, [c] + list(rota_atual)):
                            melhor_dist = dist_ini
                            melhor_cliente = c
                            no_inicio = True

                if melhor_cliente is not None:
                    if no_inicio:
                        rota_atual.appendleft(melhor_cliente)
                    else:
                        rota_atual.append(melhor_cliente)
                    nao_visitados.remove(melhor_cliente)
                else:
                    # Nenhum cliente cabe mais nesta rota
                    break

            rotas.append(list(rota_atual))

        custo_total = self.calcular_custo(inst, rotas, k_alvo)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos