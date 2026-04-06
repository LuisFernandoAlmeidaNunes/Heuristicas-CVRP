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