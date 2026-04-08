import math
from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class Sweep(Heuristica):
    """
    Heurística construtiva Sweep (Varredura) - Gillett & Miller:
    1. Calcula o ângulo polar de cada cliente em relação ao depósito
    2. Ordena os clientes por ângulo crescente (varredura angular)
    3. Agrupa clientes em rotas respeitando a capacidade do veículo
    4. A ordem de visita dentro de cada rota é a própria ordem da varredura
    """
    nome = "SW (Sweep)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo
        clientes = inst.ids_clientes

        dep = grafo.nos[deposito]

        # 1. Calcula ângulo polar de cada cliente em relação ao depósito
        def angulo(cliente_id):
            no = grafo.nos[cliente_id]
            return math.atan2(no.y - dep.y, no.x - dep.x)

        clientes_ordenados = sorted(clientes, key=angulo)

        # 2. Agrupa e define ordem de visita pela própria varredura angular
        rotas = []
        rota_atual = []
        carga_atual = 0

        for c in clientes_ordenados:
            demanda = grafo.nos[c].demanda

            if carga_atual + demanda > capacidade:
                if rota_atual:
                    rotas.append(rota_atual)
                rota_atual = [c]
                carga_atual = demanda
            else:
                rota_atual.append(c)
                carga_atual += demanda

        if rota_atual:
            rotas.append(rota_atual)

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos