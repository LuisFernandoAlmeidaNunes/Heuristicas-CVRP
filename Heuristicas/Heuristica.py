from abc import ABC, abstractmethod
from typing import List, Tuple

class Heuristica(ABC):
    nome: str = "BASE"

    @abstractmethod
    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        """Retorna (rotas, custo_total, n_veiculos)"""
        pass

    def calcular_custo(self, inst, rotas: List[List[int]]) -> float:
        """Calcula custo total da solução"""
        custo_total = 0.0
        deposito = inst.id_deposito
        grafo = inst.grafo

        for rota in rotas:
            if not rota:
                continue
            custo_total += grafo.dist(deposito, rota[0])
            for i in range(len(rota) - 1):
                custo_total += grafo.dist(rota[i], rota[i + 1])
            custo_total += grafo.dist(rota[-1], deposito)
        return custo_total

    @staticmethod
    def validar_capacidade(inst, rota: List[int]) -> bool:
        return sum(inst.grafo.nos[i].demanda for i in rota) <= inst.capacidade

    # def otimizar_rotas_2opt(self, inst, rotas: List[List[int]]) -> List[List[int]]:
    #     """Refina cada rota com 2-opt local (permuta segmentos internos)."""
    #     deposito = inst.id_deposito
    #     grafo = inst.grafo
    #
    #     def _two_opt_rota(rota: List[int]) -> List[int]:
    #         if len(rota) < 3:
    #             return rota
    #
    #         melhor = rota
    #         melhor_encontrado = True
    #
    #         while melhor_encontrado:
    #             melhor_encontrado = False
    #             for i in range(len(melhor) - 2):
    #                 for k in range(i + 2, len(melhor)):
    #                     j = k + 1
    #                     anterior = deposito if i == 0 else melhor[i - 1]
    #                     inicio = melhor[i]
    #                     fim = melhor[k]
    #                     seguinte = deposito if j == len(melhor) else melhor[j]
    #
    #                     delta = (grafo.dist(anterior, fim) + grafo.dist(inicio, seguinte)
    #                              - grafo.dist(anterior, inicio) - grafo.dist(fim, seguinte))
    #                     if delta < -1e-6:
    #                         melhor = melhor[:i] + list(reversed(melhor[i:k + 1])) + melhor[j:]
    #                         melhor_encontrado = True
    #                         break
    #                 if melhor_encontrado:
    #                     break
    #
    #         return melhor

        return [_two_opt_rota(rota) if rota else rota for rota in rotas]