from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica


class ChristofidesLike(Heuristica):
    """
    Heurística construtiva Christofides-Like (Inserção Sequencial Normalizada):

    Inspirada no algoritmo de Christofides para o TSP, adaptada para o CVRP.
    A ideia central é construir rotas inserindo clientes de forma sequencial,
    mas usando um critério de custo NORMALIZADO que equilibra dois fatores:

        criterio(i, pos, r) = custo_insercao(i, pos, r) / d(deposito, i)

    O numerador mede o quanto a rota fica mais cara ao inserir o cliente i.
    O denominador penaliza clientes longe do depósito — forçando o algoritmo
    a "puxar" clientes distantes para dentro das rotas antes que fiquem
    isolados, o que é exatamente o insight do Christofides original.

    Diferença em relação à Inserção Adaptativa (AI):
      - AI: minimiza custo absoluto de inserção → tende a formar rotas densas
            perto do depósito e deixar clientes distantes para rotas caras no fim
      - CL: minimiza custo RELATIVO (normalizado) → distribui melhor os clientes
            distantes entre as rotas, gerando soluções mais equilibradas

    Esqueleto do Algoritmo:
    1. Inicializa cada rota com o cliente mais distante do depósito ainda
       não alocado (semente da rota) — garante que clientes extremos sejam
       atendidos cedo e não fiquem isolados
    2. Para cada cliente restante, calcula o critério normalizado em todas
       as posições de todas as rotas abertas
    3. Insere o cliente com MENOR critério normalizado
    4. Se nenhuma rota comportar nenhum cliente, abre nova rota com nova semente
    5. Repete até alocar todos os clientes
    """
    nome = "CL (Christofides-Like)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo

        rotas: List[List[int]] = []
        cargas: List[int] = []

        nao_alocados = set(inst.ids_clientes)

        # Abre a primeira rota com a semente mais distante do depósito
        self._abrir_rota(deposito, nao_alocados, rotas, cargas, grafo)

        while nao_alocados:
            melhor_criterio = float("inf")
            melhor_cliente = None
            melhor_rota_idx = None
            melhor_pos = None

            for cliente in nao_alocados:
                demanda = grafo.nos[cliente].demanda
                dist_deposito = grafo.dist(deposito, cliente)

                # Evita divisao por zero (cliente no deposito — nao deve ocorrer)
                if dist_deposito == 0:
                    dist_deposito = 1e-9

                for r_idx, rota in enumerate(rotas):
                    if cargas[r_idx] + demanda > capacidade:
                        continue

                    for pos in range(len(rota) + 1):
                        custo = self._custo_insercao(
                            deposito, rota, cliente, pos, grafo
                        )

                        # Criterio normalizado — coracao do Christofides-Like
                        criterio = custo / dist_deposito

                        if criterio < melhor_criterio:
                            melhor_criterio = criterio
                            melhor_cliente = cliente
                            melhor_rota_idx = r_idx
                            melhor_pos = pos

            if melhor_cliente is not None:
                rotas[melhor_rota_idx].insert(melhor_pos, melhor_cliente)
                cargas[melhor_rota_idx] += grafo.nos[melhor_cliente].demanda
                nao_alocados.remove(melhor_cliente)
            else:
                # Nenhuma rota existente comporta os clientes restantes
                # Abre nova rota com a próxima semente mais distante
                self._abrir_rota(deposito, nao_alocados, rotas, cargas, grafo)

        rotas = [r for r in rotas if r]

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _abrir_rota(self, deposito: int, nao_alocados: set,
                    rotas: list, cargas: list, grafo) -> None:
        """
        Abre uma nova rota usando como semente o cliente mais distante
        do depósito entre os ainda não alocados.
        Clientes distantes são sementes naturais: se não forem colocados
        cedo em alguma rota, acabam gerando rotas extras caras no final.
        """
        semente = max(nao_alocados, key=lambda c: grafo.dist(deposito, c))
        rotas.append([semente])
        cargas.append(grafo.nos[semente].demanda)
        nao_alocados.remove(semente)

    def _custo_insercao(self, deposito: int, rota: List[int],
                        cliente: int, pos: int, grafo) -> float:
        """
        Acréscimo no custo da rota ao inserir 'cliente' na posição 'pos'.

            custo = d(anterior, cliente) + d(cliente, posterior) - d(anterior, posterior)

        Casos extremos tratados:
          - Rota vazia     → d(dep, cliente) + d(cliente, dep)
          - pos = 0        → anterior = depósito
          - pos = len(rota)→ posterior = depósito
        """
        n = len(rota)

        if n == 0:
            return grafo.dist(deposito, cliente) + grafo.dist(cliente, deposito)

        anterior = deposito if pos == 0 else rota[pos - 1]
        posterior = deposito if pos == n else rota[pos]

        return (grafo.dist(anterior, cliente)
                + grafo.dist(cliente, posterior)
                - grafo.dist(anterior, posterior))