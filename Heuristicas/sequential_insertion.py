from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class MoleJameson(Heuristica):
    """
    Heurística de Mole & Jameson (1976):
    Algoritmo de inserção sequencial que utiliza critérios de economia
    e custo de inserção para construir rotas uma por uma.
    """
    nome = "MJ (Mole & Jameson)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        clientes_restantes = set(inst.ids_clientes)
        rotas = []

        # Parâmetros clássicos sugeridos por Mole & Jameson
        alpha = 1.0  # Peso para a distância do depósito
        lambda_param = 1.0  # Peso para o custo de inserção (delta)

        while clientes_restantes:
            # 1. Inicia uma nova rota com o cliente mais distante ainda não visitado
            # (Estratégia comum para "ancorar" a rota em áreas periféricas)
            semente = max(clientes_restantes, key=lambda c: grafo.dist(deposito, c))

            # Validação de segurança para o semente (se ele sozinho cabe na autonomia)
            if not self.validar_viabilidade(inst, [semente]):
                clientes_restantes.remove(semente)
                continue

            rota_atual = [semente]
            clientes_restantes.remove(semente)

            pode_inserir = True
            while pode_inserir and clientes_restantes:
                melhor_f = float('-inf')  # Queremos maximizar a economia
                melhor_cliente = None
                melhor_posicao = -1

                # 2. Tenta encontrar o melhor cliente para inserir na rota ATUAL
                for cliente in clientes_restantes:
                    # Percorre todas as posições possíveis da rota: [dep, n1, n2, ..., dep]
                    caminho = [deposito] + rota_atual + [deposito]

                    melhor_f_cliente = float('-inf')
                    posicao_cliente = -1

                    for i in range(len(caminho) - 1):
                        no_i = caminho[i]
                        no_j = caminho[i + 1]

                        # Cálculo do custo de inserção (delta)
                        delta = grafo.dist(no_i, cliente) + grafo.dist(cliente, no_j) - grafo.dist(no_i, no_j)

                        # Critério de Mole & Jameson:
                        # f = alpha * dist(dep, cliente) - lambda * delta
                        f = alpha * grafo.dist(deposito, cliente) - lambda_param * delta

                        if f > melhor_f_cliente:
                            # Validação de Viabilidade (Capacidade + Distância + Tempo)
                            rota_teste = rota_atual[:i] + [cliente] + rota_atual[i:]
                            if self.validar_viabilidade(inst, rota_teste):
                                melhor_f_cliente = f
                                posicao_cliente = i

                    # Verifica se este é o melhor cliente entre todos os candidatos
                    if melhor_f_cliente > melhor_f:
                        melhor_f = melhor_f_cliente
                        melhor_cliente = cliente
                        melhor_posicao = posicao_cliente

                # 3. Se encontrou um cliente viável, insere-o e continua na mesma rota
                if melhor_cliente is not None:
                    rota_atual.insert(melhor_posicao, melhor_cliente)
                    clientes_restantes.remove(melhor_cliente)
                else:
                    # Não cabe mais ninguém nesta rota respeitando as restrições
                    pode_inserir = False

            rotas.append(rota_atual)

        custo_total = self.calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos