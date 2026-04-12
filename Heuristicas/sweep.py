import math
from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class Sweep(Heuristica):
    """
    Heurística construtiva Sweep (Varredura) - Gillett & Miller Clássica.
    1. Calcula o ângulo polar de cada cliente em relação ao depósito.
    2. Ordena os clientes por ângulo.
    3. Constrói rotas seguindo a ordem angular e validando restrições totais.
    """
    nome = "SW (Sweep)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        clientes = inst.ids_clientes
        dep = grafo.nos[deposito]

        # 1. Cálculo do ângulo polar (atan2 lida com todos os quadrantes)
        def calcular_angulo(cliente_id):
            no = grafo.nos[cliente_id]
            return math.atan2(no.y - dep.y, no.x - dep.x)

        # 2. Ordenação Angular (A "Varredura")
        clientes_ordenados = sorted(clientes, key=calcular_angulo)

        # 3. Agrupamento em rotas respeitando a viabilidade total (Carga + Distância + Tempo)
        rotas = []
        rota_atual = []

        for cliente in clientes_ordenados:
            # Testa se o cliente cabe na rota ATUAL
            # Criamos uma cópia temporária para validar
            teste_rota = rota_atual + [cliente]

            if self.validar_viabilidade(inst, teste_rota):
                rota_atual.append(cliente)
            else:
                # Se não cabe, fecha a rota atual e começa uma nova com o cliente
                if rota_atual:
                    rotas.append(rota_atual)

                # Importante: Validar se o cliente sozinho cabe em uma rota nova
                # (necessário para instâncias com limites de distância muito rígidos)
                if self.validar_viabilidade(inst, [cliente]):
                    rota_atual = [cliente]
                else:
                    # Caso extremo: um único cliente é inviável (ex: longe demais)
                    # Em instâncias válidas de benchmark isso não deve ocorrer
                    rota_atual = []

        # Adiciona a última rota se não estiver vazia
        if rota_atual:
            rotas.append(rota_atual)

        # 4. Cálculo final usando os métodos genéricos da Base
        custo_total = self.calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos