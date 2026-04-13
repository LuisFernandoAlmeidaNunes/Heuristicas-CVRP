from typing import List, Tuple
from .Heuristica import Heuristica


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
        grafo = inst.grafo
        clientes = inst.ids_clientes

        # 1. Inicializa rotas individuais: [cliente]
        # (O depósito é omitido da lista interna, pois calcular_custo o considera)
        rotas = [[c] for c in clientes]

        # Mapeamento cliente -> índice da rota atual em 'rotas'
        cliente_para_rota = {c: i for i, c in enumerate(clientes)}

        # 2. Calcula economias s_ij = d(0,i) + d(0,j) - d(i,j)
        economias = []
        for i in range(len(clientes)):
            for j in range(i + 1, len(clientes)):
                ci, cj = clientes[i], clientes[j]
                s = (grafo.dist(deposito, ci) +
                     grafo.dist(deposito, cj) -
                     grafo.dist(ci, cj))
                if s > 0:
                    economias.append((s, ci, cj))

        # 3. Ordena economias em ordem decrescente
        economias.sort(reverse=True, key=lambda x: x[0])

        # Função auxiliar para verificar se o cliente está nas pontas da rota
        def eh_extremo(rota, cliente):
            return cliente == rota[0] or cliente == rota[-1]

        # 4. Processa a lista de economias para realizar Merges
        for _, ci, cj in economias:
            ri = cliente_para_rota[ci]
            rj = cliente_para_rota[cj]

            # Já estão na mesma rota?
            if ri == rj:
                continue

            rota_i = rotas[ri]
            rota_j = rotas[rj]

            # Regra: Ambos os clientes devem ser extremidades de suas rotas
            if not (eh_extremo(rota_i, ci) and eh_extremo(rota_j, cj)):
                continue

            # Tenta construir a nova rota candidata baseada nas posições das extremidades
            nova_rota_proposta = []

            if ci == rota_i[-1] and cj == rota_j[0]:
                nova_rota_proposta = rota_i + rota_j
            elif ci == rota_i[0] and cj == rota_j[-1]:
                nova_rota_proposta = rota_j + rota_i
            elif ci == rota_i[0] and cj == rota_j[0]:
                nova_rota_proposta = rota_i[::-1] + rota_j
            elif ci == rota_i[-1] and cj == rota_j[-1]:
                nova_rota_proposta = rota_i + rota_j[::-1]

            # VALIDAÇÃO (Capacidade + Distância + Tempo de Serviço)
            # Se a nova rota proposta violar qualquer restrição da instância, ignoramos o merge
            if nova_rota_proposta and self.validar_viabilidade(inst, nova_rota_proposta):
                # Efetiva o Merge
                rotas[ri] = nova_rota_proposta
                rotas[rj] = []  # Esvazia a rota antiga j

                # Atualiza o mapeamento de todos os clientes que estavam na rota_j para a nova ri
                for c in nova_rota_proposta:
                    cliente_para_rota[c] = ri

        # Filtra as rotas que não ficaram vazias após os merges
        rotas_finais = [r for r in rotas if r]

        # Calcula resultados finais usando os métodos da classe base
        custo_total = self.calcular_custo(inst, rotas_finais)
        n_veiculos = len(rotas_finais)

        return rotas_finais, custo_total, n_veiculos