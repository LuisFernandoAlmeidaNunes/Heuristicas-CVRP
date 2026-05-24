import math
from typing import List, Tuple, Optional
from Heuristicas.Heuristica import Heuristica

class Sweep(Heuristica):
    """
    A heurística Sweep (Varredura) é um algoritmo geométrico clássico para o CVRP,
    baseado na estratégia "Cluster-First, Route-Second". Sua lógica principal
    consiste em converter as coordenadas cartesianas dos clientes em coordenadas
    polares em relação ao depósito.

    O funcionamento dessa implementação segue estas etapas fundamentais:

    1. Transformação Polar: Calcula o ângulo (atan2) de cada cliente em relação
       ao depósito central, tratando o depósito como a origem do sistema.

    2. Varredura Angular: Ordena os clientes por seus ângulos, simulando o
       movimento de um radar ou ponteiro de relógio que "varre" o plano.

    3. Agrupamento (Clustering): Os clientes são adicionados à rota atual
       conforme a ordem angular. Quando a capacidade do veículo é atingida,
       a rota é fechada e uma nova se inicia imediatamente no próximo cliente.

    4. Otimização por Rotação: Como o ponto de início da varredura (0°) é
       arbitrário, o algoritmo testa todos os clientes como possíveis pontos
       de partida e nos dois sentidos (horário e anti-horário), selecionando
       a configuração que resulta no menor custo total e melhor uso da frota.

    Esta heurística é extremamente rápida e eficaz para instâncias onde os
    clientes estão distribuídos geograficamente ao redor do depósito, embora
    possa ter dificuldades em cenários com restrições de tempo ou janelas muito curtas.
    """
    nome = "SW (Sweep)"

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        clientes = inst.ids_clientes
        dep = grafo.nos[deposito]

        # 1. Pré-calcula ângulos de todos os clientes
        def calcular_angulo(c_id):
            no = grafo.nos[c_id]
            # atan2 retorna entre -pi e pi
            return math.atan2(no.y - dep.y, no.x - dep.x)

        # Lista de tuplas (angulo, id_cliente)
        dados_clientes = [(calcular_angulo(c), c) for c in clientes]
        # Ordena por ângulo para facilitar a rotação do ponto de início
        dados_clientes.sort()

        melhor_solucao = None
        melhor_custo = float('inf')

        # Testar múltiplos pontos de partida (Seed Nodes)
        # Em vez de testar todos (lento), testamos cada cliente como início de uma rota
        for i in range(len(dados_clientes)):
            # Rotaciona a lista para começar no cliente i
            clientes_ordenados = [c for _, c in (dados_clientes[i:] + dados_clientes[:i])]

            # Testa nos dois sentidos (Horário e Anti-horário)
            for sentido in [clientes_ordenados, clientes_ordenados[::-1]]:
                rotas_tentativa = self._construir_agrupamento(inst, sentido)

                # Calcula o custo (incluindo penalidade de veículos)
                custo_tentativa = self.calcular_custo(inst, rotas_tentativa, k_alvo)

                if custo_tentativa < melhor_custo:
                    melhor_custo = custo_tentativa
                    melhor_solucao = rotas_tentativa

        rotas_finais = melhor_solucao if melhor_solucao else []
        n_veiculos = len(rotas_finais)

        return rotas_finais, melhor_custo, n_veiculos

    def _construir_agrupamento(self, inst, clientes_ordenados) -> List[List[int]]:
        """Lógica interna de agrupamento respeitando a viabilidade"""
        rotas = []
        rota_atual = []

        for cliente in clientes_ordenados:
            teste_rota = rota_atual + [cliente]
            if self.validar_viabilidade(inst, teste_rota):
                rota_atual.append(cliente)
            else:
                if rota_atual:
                    rotas.append(rota_atual)
                rota_atual = [cliente]

        if rota_atual:
            rotas.append(rota_atual)
        return rotas