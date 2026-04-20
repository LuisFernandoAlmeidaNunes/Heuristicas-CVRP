from typing import List, Tuple, Optional
from Heuristicas.Heuristica import Heuristica


class MoleJameson(Heuristica):
    nome = "MJ (Mole & Jameson)"

    def resolver(self, inst, k_alvo: Optional[int] = None) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        grafo = inst.grafo
        clientes_restantes = set(inst.ids_clientes)
        rotas = []

        # Parâmetros clássicos de Mole & Jameson
        # Alpha: peso da distância ao depósito (geralmente 1.0 ou 2.0)
        # Mu: peso do custo de inserção (delta)
        ALPHA = 1.5
        MU = 1.0

        while clientes_restantes:
            # 1. Seleção da Semente (Seed): Cliente mais distante do depósito
            semente = max(clientes_restantes, key=lambda c: grafo.dist(deposito, c))

            rota_atual = [semente]
            clientes_restantes.remove(semente)

            pode_inserir = True
            while pode_inserir and clientes_restantes:
                melhor_f = float('inf')  # Aqui buscamos MINIMIZAR a tensão (strain)
                melhor_cliente = None
                melhor_posicao = -1

                for cliente in clientes_restantes:
                    # Avaliamos a melhor posição de inserção para ESTE cliente
                    melhor_delta_cliente = float('inf')
                    pos_cliente = -1

                    # Tenta inserir entre todos os nós da rota (incluindo retorno ao depósito)
                    # Ex: Dep -> Rota[0] -> Rota[1] -> Dep
                    caminho_com_dep = [deposito] + rota_atual + [deposito]

                    for i in range(len(caminho_com_dep) - 1):
                        u, v = caminho_com_dep[i], caminho_com_dep[i + 1]

                        # Delta de inserção: d(u,c) + d(c,v) - d(u,v)
                        delta = grafo.dist(u, cliente) + grafo.dist(cliente, v) - grafo.dist(u, v)

                        if delta < melhor_delta_cliente:
                            # Checagem de viabilidade temporária
                            rota_teste = rota_atual[:i] + [cliente] + rota_atual[i:]
                            if self.validar_viabilidade(inst, rota_teste):
                                melhor_delta_cliente = delta
                                pos_cliente = i

                    # Se encontramos uma posição viável para o cliente, calculamos o critério MJ
                    if pos_cliente != -1:
                        # Critério de Tensão (Strain): f = delta - alpha * d(dep, cliente)
                        # O objetivo é escolher o cliente que minimiza esse acréscimo "líquido"
                        f = (MU * melhor_delta_cliente) - (ALPHA * grafo.dist(deposito, cliente))

                        if f < melhor_f:
                            melhor_f = f
                            melhor_cliente = cliente
                            melhor_posicao = pos_cliente

                # 2. Inserção do melhor candidato
                if melhor_cliente is not None:
                    rota_atual.insert(melhor_posicao, melhor_cliente)
                    clientes_restantes.remove(melhor_cliente)
                else:
                    # Nenhum cliente restante cabe nesta rota
                    pode_inserir = False

            rotas.append(rota_atual)

        rotas_finais = [r for r in rotas if r]
        custo_total = self.calcular_custo(inst, rotas_finais, k_alvo)
        n_veiculos = len(rotas_finais)

        return rotas_finais, custo_total, n_veiculos