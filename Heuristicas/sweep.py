import math
from typing import List, Tuple, Optional
from Heuristicas.Heuristica import Heuristica

class Sweep(Heuristica):
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