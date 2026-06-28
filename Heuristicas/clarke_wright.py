import random
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

    Randomização (RCL por cardinalidade): com k_rcl > 1, a cada passo a próxima
    fusão é sorteada entre as k_rcl melhores fusões VIÁVEIS naquele momento
    (Lista Restrita de Candidatos), em vez de sempre a melhor. Isso gera soluções
    diferentes a cada chamada (fase construtiva do GRASP) sem promover fusões
    globalmente ruins para o início — preservando a qualidade mesmo em instâncias
    de capacidade apertada. Com k_rcl = 1 o comportamento é o guloso determinístico.
    """
    nome = "CW (Clarke & Wright Savings)"

    def __init__(self, k_rcl: int = 1):
        # k_rcl = 1 -> guloso determinístico; k_rcl > 1 -> RCL por cardinalidade
        self.k_rcl = k_rcl

    def _aplicar_fusao(self, inst, rotas: dict, cliente_para_rota_id: dict,
                       ci: int, cj: int) -> bool:
        """
        Tenta fundir as rotas de ci e cj. Retorna True se a fusão foi aplicada,
        False caso contrário (mesma rota, clientes não-extremidade, ou inviável).
        """
        id_i = cliente_para_rota_id[ci]
        id_j = cliente_para_rota_id[cj]

        if id_i == id_j:
            return False

        rota_i = rotas[id_i]
        rota_j = rotas[id_j]

        # Critério Clarke-Wright: i e j devem ser extremidades conectadas ao depósito
        if not ((ci == rota_i[0] or ci == rota_i[-1]) and
                (cj == rota_j[0] or cj == rota_j[-1])):
            return False

        # Determina a orientação da fusão
        if ci == rota_i[-1] and cj == rota_j[0]:
            nova_rota = rota_i + rota_j
        elif ci == rota_i[0] and cj == rota_j[-1]:
            nova_rota = rota_j + rota_i
        elif ci == rota_i[0] and cj == rota_j[0]:
            nova_rota = rota_i[::-1] + rota_j
        else:  # ci == rota_i[-1] and cj == rota_j[-1]
            nova_rota = rota_i + rota_j[::-1]

        # Validação de Restrições (Capacidade/Autonomia)
        if not self.validar_viabilidade(inst, nova_rota):
            return False

        rotas[id_i] = nova_rota
        del rotas[id_j]
        for cliente in nova_rota:
            cliente_para_rota_id[cliente] = id_i
        return True

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        clientes = inst.ids_clientes

        # 1. Rotas individuais (0-i-0), indexadas por um ID único
        rotas = {i: [c] for i, c in enumerate(clientes)}
        cliente_para_rota_id = {c: i for i, c in enumerate(clientes)}

        # 2. Cálculo das Economias (Savings): s_ij = d(0,i) + d(0,j) - d(i,j)
        economias = []
        for i in range(len(clientes)):
            for j in range(i + 1, len(clientes)):
                ci, cj = clientes[i], clientes[j]
                s = (grafo.dist(deposito, ci) +
                     grafo.dist(deposito, cj) -
                     grafo.dist(ci, cj))
                if s > 0:
                    economias.append((s, ci, cj))

        # 3. Ordenar economias decrescente
        economias.sort(key=lambda x: x[0], reverse=True)

        # 4. Processo de Merge (Fusão)
        if self.k_rcl <= 1:
            # Guloso clássico: percorre as economias na ordem decrescente
            for _, ci, cj in economias:
                self._aplicar_fusao(inst, rotas, cliente_para_rota_id, ci, cj)
        else:
            # GRASP: seleção via RCL por cardinalidade
            self._merge_rcl(inst, rotas, cliente_para_rota_id, economias)

        rotas_finais = list(rotas.values())
        custo_total = self.calcular_custo(inst, rotas_finais, k_alvo)
        n_veiculos = len(rotas_finais)

        return rotas_finais, custo_total, n_veiculos

    def _merge_rcl(self, inst, rotas: dict, cliente_para_rota_id: dict,
                   economias: List[Tuple[float, int, int]]) -> None:
        """
        Fusão com RCL por cardinalidade: a cada passo, monta-se a lista das k_rcl
        melhores fusões viáveis (extremidades livres, rotas distintas) e sorteia-se
        uma delas. Um ponteiro de avanço (p) e um conjunto de economias "mortas"
        evitam re-escanear desde o topo, mantendo o custo amortizado próximo do
        guloso (uma economia, uma vez extremidade interna, nunca volta a ser viável).
        """
        n = len(economias)
        dead = set()

        def viavel(ci, cj) -> bool:
            if (ci, cj) in dead:
                return False
            id_i = cliente_para_rota_id[ci]
            id_j = cliente_para_rota_id[cj]
            if id_i == id_j:
                return False
            rota_i = rotas[id_i]
            rota_j = rotas[id_j]
            return ((ci == rota_i[0] or ci == rota_i[-1]) and
                    (cj == rota_j[0] or cj == rota_j[-1]))

        p = 0
        while p < n:
            # avança o ponteiro além das economias já inviáveis no topo
            while p < n and not viavel(economias[p][1], economias[p][2]):
                p += 1
            if p >= n:
                break

            # monta a RCL: até k_rcl melhores fusões viáveis a partir de p
            rcl = []
            q = p
            while q < n and len(rcl) < self.k_rcl:
                _, ci, cj = economias[q]
                if viavel(ci, cj):
                    rcl.append((ci, cj))
                q += 1

            ci, cj = random.choice(rcl)
            if not self._aplicar_fusao(inst, rotas, cliente_para_rota_id, ci, cj):
                # passou na checagem barata mas falhou por capacidade/autonomia: morta
                dead.add((ci, cj))
