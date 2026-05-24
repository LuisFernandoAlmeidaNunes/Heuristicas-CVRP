from typing import List, Tuple, Optional
from collections import deque
from Heuristicas.Heuristica import Heuristica


class NearestNeighbor(Heuristica):
    """
    A heurística Nearest Neighbor (Vizinho Mais Próximo) é um algoritmo construtivo
    guloso que monta rotas baseando-se na proximidade imediata entre os nós.
    Esta implementação utiliza uma estratégia de "expansão por duas pontas"
    para garantir maior flexibilidade na construção das rotas.

    O funcionamento segue este fluxo:

    1. Seleção de Semente (Seed): Para iniciar cada rota, o algoritmo escolhe o
       cliente não visitado mais distante do depósito. Esta técnica (Farthest Seed)
       ajuda a isolar clientes periféricos em rotas eficientes, evitando que eles
       sejam deixados para o final, o que geraria custos altíssimos.

    2. Expansão Bidirecional: Diferente do NN tradicional que só cresce para a
       frente, esta versão utiliza um 'deque' para avaliar a inserção de novos
       clientes tanto no início quanto no fim da sequência atual. Isso permite
       que a rota se molde melhor ao cluster de clientes.

    3. Critério de Proximidade e Viabilidade: A cada passo, o algoritmo busca o
       cliente mais próximo de qualquer uma das extremidades da rota. A inserção
       só é confirmada se respeitar as restrições de capacidade do veículo
       (validar_viabilidade).

    4. Encerramento de Rota: Quando nenhum cliente restante pode ser adicionado
       sem violar a capacidade, a rota é fechada e o processo recomeça com uma
       nova semente até que todos os clientes tenham sido atendidos.

    É uma heurística de altíssima velocidade (baixa complexidade computacional).
    """
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