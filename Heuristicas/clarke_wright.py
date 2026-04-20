from typing import List, Optional, Tuple
from Heuristicas.Heuristica import Heuristica

#versão de parallel savings
class ClarkeWright(Heuristica):
    """
    A heurística de Clarke & Wright (Savings) é um dos algoritmos construtivos mais
    amplamente utilizados para o CVRP. Esta implementação utiliza a
    versão "Paralela", que permite que múltiplas rotas sejam fundidas
    simultaneamente conforme as oportunidades de economia surgem.

    A lógica do algoritmo baseia-se no conceito de Economia (Savings):

    1. Inicialização: Cada cliente começa em uma rota individual dedicada, indo do
       depósito ao cliente e retornando (0 -> i -> 0).

    2. Cálculo de Economias: Para cada par de clientes (i, j), calcula-se quanto
       de distância seria economizado se eles fossem atendidos pelo mesmo veículo
       em sequência, eliminando duas viagens ao depósito.
       Fórmula: S(i,j) = d(0,i) + d(0,j) - d(i,j).

    3. Ordenação Estratégica: As economias são processadas da maior para a menor.
       Isso garante que as fusões que trazem o maior ganho logístico sejam
       priorizadas logo no início.

    4. Critérios de Fusão (Merge): Duas rotas só podem ser fundidas se:
       - Os clientes envolvidos estiverem nas extremidades das suas respectivas rotas
         (conectados diretamente ao depósito).
       - A nova rota resultante for viável em termos de capacidade e autonomia.

    5. Flexibilidade de Orientação: O algoritmo avalia as quatro combinações
       possíveis de fusão (ponta com ponta, início com início, etc.), invertendo
       as sequências quando necessário para manter a continuidade do caminho.

    Dessa forma a solução agrupa clientes em clusters lógicos e reduz
    drasticamente o número de veículos e a distância total percorrida em
    comparação com soluções puramente gulosas.
    """
    nome = "CW (Clarke & Wright Savings)"

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        clientes = inst.ids_clientes

        # 1. Rotas individuais (0-i-0)
        # Usamos um dicionário para manter as rotas ativas por um ID único
        rotas = {i: [c] for i, c in enumerate(clientes)}
        # Mapeia cada cliente para o ID da sua rota atual
        cliente_para_rota_id = {c: i for i, c in enumerate(clientes)}

        # 2. Cálculo das Economias (Savings)
        economias = []
        for i in range(len(clientes)):
            for j in range(i + 1, len(clientes)):
                ci, cj = clientes[i], clientes[j]
                # s_ij = d(0,i) + d(0,j) - d(i,j)
                s = (grafo.dist(deposito, ci) +
                     grafo.dist(deposito, cj) -
                     grafo.dist(ci, cj))
                if s > 0:
                    economias.append((s, ci, cj))

        # 3. Ordenar economias decrescente
        economias.sort(key=lambda x: x[0], reverse=True)

        # 4. Processo de Merge (Fusão)
        for _, ci, cj in economias:
            id_i = cliente_para_rota_id[ci]
            id_j = cliente_para_rota_id[cj]

            if id_i == id_j:
                continue

            rota_i = rotas[id_i]
            rota_j = rotas[id_j]

            # Critério Clarke-Wright: i e j devem ser extremidades conectadas ao depósito
            # O nó ci deve estar em uma das pontas da rota_i e cj na ponta da rota_j
            if not ((ci == rota_i[0] or ci == rota_i[-1]) and
                    (cj == rota_j[0] or cj == rota_j[-1])):
                continue

            # Determina a orientação da fusão
            if ci == rota_i[-1] and cj == rota_j[0]:
                nova_rota = rota_i + rota_j
            elif ci == rota_i[0] and cj == rota_j[-1]:
                nova_rota = rota_j + rota_i
            elif ci == rota_i[0] and cj == rota_j[0]:
                nova_rota = rota_i[::-1] + rota_j
            else:  # ci == rota_i[-1] and cj == rota_j[-1]
                nova_rota = rota_i + rota_j[::-1]

            # 5. Validação de Restrições (Capacidade/Tempo)
            if self.validar_viabilidade(inst, nova_rota):
                # Atualiza a rota i e remove a rota j
                rotas[id_i] = nova_rota
                del rotas[id_j]

                # Atualiza o mapeamento de todos os clientes da rota que foi movida
                # para garantir segurança na lógica de 'id_i == id_j', atualizamos todos)
                for cliente in nova_rota:
                    cliente_para_rota_id[cliente] = id_i

        rotas_finais = list(rotas.values())
        custo_total = self.calcular_custo(inst, rotas_finais, k_alvo)
        n_veiculos = len(rotas_finais)

        return rotas_finais, custo_total, n_veiculos