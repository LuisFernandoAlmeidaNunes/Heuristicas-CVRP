from typing import List, Optional, Tuple
from Heuristicas.Heuristica import Heuristica
from saida.terminal import spinner_busca_local_fim


class TwoOpt(Heuristica):
    """
    Busca Local — 2-Opt intra-rota + Or-Opt inter-rota (blocos de 1, 2 e 3).

    FASE 1 — 2-Opt intra-rota:
    Inverte segmentos dentro de cada rota. Primeira melhora.
    Não altera número de veículos.

    FASE 2 — Or-Opt inter-rota:
    Move blocos de 1, 2 ou 3 clientes contíguos de uma rota para outra.
    Avaliado em ordem: primeiro tenta eliminar rotas pequenas movendo
    todos os seus clientes de uma vez (prioritário), depois tenta
    movimentos de blocos menores que reduzam o custo total.
    Pode eliminar rotas que ficam vazias — reduz número de veículos.

    As duas fases alternam até convergência.
    """

    nome = "2opt"

    def __init__(self, construtivo: Heuristica = None):
        self.construtivo = construtivo

    def _delta(self, inst, r, i, j) -> float:
        d = inst.grafo.dist
        dep = inst.id_deposito
        prev_i = r[i - 1] if i > 0 else dep
        next_j = r[j + 1] if j < len(r) - 1 else dep
        return (
            - d(prev_i, r[i]) - d(r[j], next_j)
            + d(prev_i, r[j]) + d(r[i], next_j)
        )

    def _dois_opt_intra(self, inst, rotas: List[List[int]]) -> Tuple[List[List[int]], bool]:
        """2-Opt dentro de cada rota. Retorna (rotas, houve_melhora)."""
        max_dist = getattr(inst, 'max_distancia', float('inf'))
        melhorou_global = False

        melhorou = True
        while melhorou:
            melhorou = False
            for idx_rota, r in enumerate(rotas):
                if len(r) < 2:
                    continue
                for i in range(len(r) - 1):
                    for j in range(i + 1, len(r)):
                        delta = self._delta(inst, r, i, j)
                        if delta >= -1e-9:
                            continue
                        nova_rota = r[:i] + r[i:j+1][::-1] + r[j+1:]
                        if max_dist != float('inf') and not self.validar_viabilidade(inst, nova_rota):
                            continue
                        rotas[idx_rota] = nova_rota
                        r = nova_rota
                        melhorou = True
                        melhorou_global = True
                        break

        return rotas, melhorou_global

    def _or_opt_inter(self, inst, rotas: List[List[int]], k_alvo) -> Tuple[List[List[int]], bool]:
        """
        Or-Opt inter-rota com blocos de tamanho 1, 2 e 3.

        Estratégia:
        1. Prioriza rotas pequenas (<=3 clientes) — tenta mover todos os
           clientes de uma vez para eliminar o veículo.
        2. Tenta blocos de tamanho 3, 2 e 1 em todas as rotas.

        Ao encontrar melhora, aplica e retorna imediatamente.
        """
        custo_atual = self.calcular_custo(inst, rotas, k_alvo)

        # Ordena rotas por tamanho crescente — prioriza eliminar rotas pequenas
        indices_ordenados = sorted(range(len(rotas)), key=lambda i: len(rotas[i]))

        for tamanho_bloco in [3, 2, 1]:
            for idx_origem in indices_ordenados:
                rota_origem = rotas[idx_origem]
                if len(rota_origem) < tamanho_bloco:
                    continue

                for inicio in range(len(rota_origem) - tamanho_bloco + 1):
                    bloco = rota_origem[inicio: inicio + tamanho_bloco]
                    nova_origem = (rota_origem[:inicio] +
                                  rota_origem[inicio + tamanho_bloco:])

                    # Valida origem após remoção
                    if nova_origem and not self.validar_viabilidade(inst, nova_origem):
                        continue

                    melhor_custo = custo_atual
                    melhor_idx_destino = None
                    melhor_pos_ins = None

                    for idx_destino in range(len(rotas)):
                        if idx_destino == idx_origem:
                            continue
                        rota_destino = rotas[idx_destino]

                        for pos_ins in range(len(rota_destino) + 1):
                            nova_destino = (rota_destino[:pos_ins] +
                                           bloco +
                                           rota_destino[pos_ins:])
                            if not self.validar_viabilidade(inst, nova_destino):
                                continue

                            rotas_teste = [list(r) for r in rotas]
                            rotas_teste[idx_origem] = nova_origem
                            rotas_teste[idx_destino] = nova_destino
                            rotas_teste = [r for r in rotas_teste if r]
                            custo_teste = self.calcular_custo(inst, rotas_teste, k_alvo)

                            if custo_teste < melhor_custo:
                                melhor_custo = custo_teste
                                melhor_idx_destino = idx_destino
                                melhor_pos_ins = pos_ins

                    if melhor_idx_destino is not None:
                        rota_dest = rotas[melhor_idx_destino]
                        rotas[melhor_idx_destino] = (rota_dest[:melhor_pos_ins] +
                                                      bloco +
                                                      rota_dest[melhor_pos_ins:])
                        rotas[idx_origem] = nova_origem
                        rotas = [r for r in rotas if r]
                        return rotas, True

        return rotas, False

    def melhorar(self, inst, rotas: List[List[int]], k_alvo=None) -> Tuple[List[List[int]], float]:
        """
        Alterna 2-Opt intra-rota e Or-Opt inter-rota até convergir.
        """
        rotas = [list(r) for r in rotas if r]

        melhorou = True
        while melhorou:
            rotas, melhorou_intra = self._dois_opt_intra(inst, rotas)
            rotas, melhorou_inter = self._or_opt_inter(inst, rotas, k_alvo)
            melhorou = melhorou_intra or melhorou_inter

        return rotas, self.calcular_custo(inst, rotas, k_alvo)

    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        rotas, _, _ = self.construtivo.resolver(inst, k_alvo)
        rotas = [list(r) for r in rotas if r]
        custo_inicial = self.calcular_custo(inst, rotas, k_alvo)

        rotas, custo = self.melhorar(inst, rotas, k_alvo)

        n_veiculos = len(rotas)
        spinner_busca_local_fim(self.nome, custo_inicial, custo)
        return rotas, custo, n_veiculos