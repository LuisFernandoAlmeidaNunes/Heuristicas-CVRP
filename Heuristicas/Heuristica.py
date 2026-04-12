from abc import ABC, abstractmethod
from typing import List, Tuple


class Heuristica(ABC):
    nome: str = "BASE"

    @abstractmethod
    def resolver(self, inst) -> Tuple[List[List[int]], float, int]:
        """Retorna (rotas, custo_total, n_veiculos)"""
        pass

    def calcular_custo(self, inst, rotas: List[List[int]]) -> float:
        """
        Calcula o custo total considerando Distâncias
        """
        custo_viagem = 0.0
        total_service_time = 0.0
        deposito = inst.id_deposito
        grafo = inst.grafo

        for rota in rotas:
            if not rota:
                continue

            # 1. Soma distâncias (Depósito -> Clientes -> Depósito)
            custo_viagem += grafo.dist(deposito, rota[0])
            for i in range(len(rota) - 1):
                custo_viagem += grafo.dist(rota[i], rota[i + 1])
            custo_viagem += grafo.dist(rota[-1], deposito)


        return custo_viagem + total_service_time

    def validar_viabilidade(self, inst, rota: List[int]) -> bool:
        # 1. Capacidade
        carga_total = sum(inst.grafo.nos[c].demanda for c in rota)
        if carga_total > inst.capacidade:
            return False

        # 2. Distância e autonomia (só se houver limite finito)
        max_dist = getattr(inst, 'max_distancia', float('inf'))
        if max_dist == float('inf'):
            return True  # Sem restrição de autonomia, encerra aqui

        dep = inst.id_deposito
        grafo = inst.grafo

        dist_total = grafo.dist(dep, rota[0])
        for i in range(len(rota) - 1):
            dist_total += grafo.dist(rota[i], rota[i + 1])
        dist_total += grafo.dist(rota[-1], dep)

        # 'tempo_servico' é o nome real setado pelo leitor
        st_unitario = getattr(inst, 'tempo_servico', 0.0)
        tempo_total = dist_total + (len(rota) * st_unitario)

        # O limite DISTANCE engloba distância + service time (jornada total)
        if tempo_total > max_dist:
            return False

        return True