from typing import List, Tuple
from heuristicas.Heuristica import Heuristica


class ClarkeWright(Heuristica):
    nome = "CW (Clarke & Wright Savings)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        """
        Heurística construtiva Clarke & Wright (Savings):
        1. Cria rotas individuais para cada cliente: 0-i-0
        2. Calcula economias s_ij = d(0,i) + d(0,j) - d(i,j) para todos os pares i,j
        3. Ordena economias decrescente
        4. Faz merges respeitando capacidade até não ser mais possível
        """
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo
        clientes = inst.ids_clientes

        # 1. Inicializa rotas individuais
        rotas = [[c] for c in clientes]

        # Mapeamento cliente -> índice da rota
        cliente_para_rota = {c: i for i, c in enumerate(clientes)}

        # 2. Calcula economias
        economias = []
        for i in range(len(clientes)):
            for j in range(i + 1, len(clientes)):
                ci = clientes[i]
                cj = clientes[j]

                s = (grafo.dist(deposito, ci) +
                     grafo.dist(deposito, cj) -
                     grafo.dist(ci, cj))

                economias.append((s, ci, cj))

        # 3. Ordena economias (decrescente)
        economias.sort(reverse=True, key=lambda x: x[0])

        # Funções auxiliares
        def carga(rota):
            return sum(grafo.nos[c].demanda for c in rota)

        def eh_extremo(rota, cliente):
            return cliente == rota[0] or cliente == rota[-1]

        # 4. Processa economias
        for _, ci, cj in economias:

            ri = cliente_para_rota[ci]
            rj = cliente_para_rota[cj]

            if ri == rj:
                continue

            rota_i = rotas[ri]
            rota_j = rotas[rj]

            # Verifica extremidades
            if not (eh_extremo(rota_i, ci) and eh_extremo(rota_j, cj)):
                continue

            # Verifica capacidade
            if carga(rota_i) + carga(rota_j) > capacidade:
                continue

            # CASOS DE MERGE

            # ci no final de rota_i e cj no início de rota_j
            if ci == rota_i[-1] and cj == rota_j[0]:
                nova_rota = rota_i + rota_j

            # ci no início de rota_i e cj no final de rota_j
            elif ci == rota_i[0] and cj == rota_j[-1]:
                nova_rota = rota_j + rota_i

            # ci no início e cj no início → inverter rota_i
            elif ci == rota_i[0] and cj == rota_j[0]:
                nova_rota = rota_i[::-1] + rota_j

            # ci no final e cj no final → inverter rota_j
            elif ci == rota_i[-1] and cj == rota_j[-1]:
                nova_rota = rota_i + rota_j[::-1]

            else:
                continue  # segurança

            # Atualiza estrutura
            rotas[ri] = nova_rota
            rotas[rj] = []

            # Atualiza mapeamento
            for c in nova_rota:
                cliente_para_rota[c] = ri

        # Remove rotas vazias
        rotas = [r for r in rotas if r]

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos
