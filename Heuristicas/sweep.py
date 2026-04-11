import math
from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class Sweep(Heuristica):
    """
    Heurística construtiva Sweep (Varredura) - Gillett & Miller:
    1. Calcula o ângulo polar de cada cliente em relação ao depósito
    2. Ordena os clientes por ângulo crescente (varredura angular)
    3. Agrupa clientes em rotas respeitando a capacidade do veículo
    4. Reordena os clientes DENTRO de cada rota usando Nearest Neighbor local

    """
    nome = "SW (Sweep)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo
        clientes = inst.ids_clientes

        dep = grafo.nos[deposito]

        # 1. Ângulo polar de cada cliente em relação ao depósito
        def angulo(cliente_id):
            no = grafo.nos[cliente_id]
            return math.atan2(no.y - dep.y, no.x - dep.x)

        clientes_ordenados = sorted(clientes, key=angulo)

        # 2. Agrupa por varredura angular respeitando capacidade
        grupos = []
        grupo_atual = []
        carga_atual = 0

        for c in clientes_ordenados:
            demanda = grafo.nos[c].demanda
            if carga_atual + demanda > capacidade:
                if grupo_atual:
                    grupos.append(grupo_atual)
                grupo_atual = [c]
                carga_atual = demanda
            else:
                grupo_atual.append(c)
                carga_atual += demanda

        if grupo_atual:
            grupos.append(grupo_atual)

        # 3. Reordena cada grupo com NN local
        rotas = []
        for grupo in grupos:
            rota = self._nn_local(deposito, grupo, grafo)
            rotas.append(rota)

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos

    def _nn_local(self, deposito: int, clientes: List[int], grafo) -> List[int]:
        """
        Nearest Neighbor dentro de um grupo fixo de clientes.
        Parte do depósito e visita sempre o mais próximo ainda não visitado.
        """
        nao_visitados = set(clientes)
        rota = []
        atual = deposito

        while nao_visitados:
            proximo = min(nao_visitados, key=lambda c: grafo.dist(atual, c))
            rota.append(proximo)
            nao_visitados.remove(proximo)
            atual = proximo

        return rota