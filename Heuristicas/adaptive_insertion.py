from typing import List, Tuple
from Heuristicas.Heuristica import Heuristica

class AdaptiveInsertion(Heuristica):
    """
    Heurística construtiva de Inserção Adaptativa (Adaptive Insertion):

    Ideia central: em vez de construir rotas adicionando clientes no final
    (como o NN), esta heurística insere cada cliente na MELHOR POSIÇÃO
    possível dentro das rotas já existentes, minimizando o custo de inserção.

    Algoritmo:
    1. Inicializa uma rota vazia por veículo (começa com uma)
    2. Para cada cliente ainda não alocado, calcula o custo de inserção
       em cada posição de cada rota existente:
           custo_insercao(i, k, r) = d(r[k], i) + d(i, r[k+1]) - d(r[k], r[k+1])
    3. Escolhe o cliente + posição + rota com MENOR custo de inserção
    4. Se nenhuma inserção respeitar a capacidade, abre uma nova rota
    5. Repete até todos os clientes serem alocados

    Vantagem sobre NN e Sweep: considera o impacto real de cada inserção
    no custo total da rota, produzindo soluções geralmente melhores.
    """
    nome = "AI (Adaptive Insertion)"

    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        deposito = inst.id_deposito
        capacidade = inst.capacidade
        grafo = inst.grafo
        clientes = list(inst.ids_clientes)

        # Cada rota começa vazia; cargas paralelas controlam a capacidade usada
        rotas: List[List[int]] = [[]]
        cargas: List[int] = [0]

        nao_alocados = set(clientes)

        while nao_alocados:
            melhor_custo = float("inf")
            melhor_cliente = None
            melhor_rota_idx = None
            melhor_pos = None

            # Avalia todas as combinações: cliente x rota x posição
            for cliente in nao_alocados:
                demanda = grafo.nos[cliente].demanda

                for r_idx, rota in enumerate(rotas):
                    # Capacidade: só considera rotas onde o cliente cabe
                    if cargas[r_idx] + demanda > capacidade:
                        continue

                    # Posições possíveis: antes do primeiro, entre cada par,
                    # e depois do último (rota pode estar vazia)
                    n = len(rota)
                    for pos in range(n + 1):
                        custo = self._custo_insercao(
                            deposito, rota, cliente, pos, grafo
                        )

                        if custo < melhor_custo:
                            melhor_custo = custo
                            melhor_cliente = cliente
                            melhor_rota_idx = r_idx
                            melhor_pos = pos

            if melhor_cliente is not None:
                # Insere na melhor posição encontrada
                rotas[melhor_rota_idx].insert(melhor_pos, melhor_cliente)
                cargas[melhor_rota_idx] += grafo.nos[melhor_cliente].demanda
                nao_alocados.remove(melhor_cliente)
            else:
                # Nenhuma rota existente comporta nenhum cliente restante
                # Abre uma nova rota com o cliente de maior demanda primeiro
                proximo = max(nao_alocados, key=lambda c: grafo.nos[c].demanda)
                rotas.append([proximo])
                cargas.append(grafo.nos[proximo].demanda)
                nao_alocados.remove(proximo)

        # Remove rotas vazias (por segurança)
        rotas = [r for r in rotas if r]

        custo_total = super().calcular_custo(inst, rotas)
        n_veiculos = len(rotas)

        return rotas, custo_total, n_veiculos

    def _custo_insercao(self, deposito: int, rota: List[int],
                        cliente: int, pos: int, grafo) -> float:
        """
        Calcula o acréscimo no custo da rota ao inserir 'cliente' na posição 'pos'.

        Para uma rota [a, b, c] com depósito 0:
          Caminho atual:  0 → a → b → c → 0
          Inserindo x em pos=1 (entre a e b):
          Caminho novo:   0 → a → x → b → c → 0
          Custo inserção: d(a, x) + d(x, b) - d(a, b)

        Casos extremos:
          pos=0 (antes do primeiro):  d(dep, x) + d(x, rota[0]) - d(dep, rota[0])
          pos=n (depois do último):   d(rota[-1], x) + d(x, dep) - d(rota[-1], dep)
          rota vazia:                 d(dep, x) + d(x, dep)  [ida e volta]
        """
        n = len(rota)

        if n == 0:
            return grafo.dist(deposito, cliente) + grafo.dist(cliente, deposito)

        # Nó anterior à posição de inserção
        anterior = deposito if pos == 0 else rota[pos - 1]
        # Nó posterior à posição de inserção
        posterior = deposito if pos == n else rota[pos]

        return (grafo.dist(anterior, cliente)
                + grafo.dist(cliente, posterior)
                - grafo.dist(anterior, posterior))