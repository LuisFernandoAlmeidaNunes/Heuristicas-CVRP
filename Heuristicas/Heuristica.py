from abc import ABC, abstractmethod
from typing import List, Tuple


class Heuristica(ABC):
    """
    Esta classe abstrata define o esqueleto para todas as outras estratégias de
    resolução (heurísticas) do CVRP neste projeto. Sua existência garante que
    diferentes algoritmos possam ser implementados com uma mesma base correta.

    As funcionalidades centrais implementadas nesta base são:

    1. Definição de Interface: Através do método abstrato 'resolver', obriga todas
       as heurísticas filhas a retornarem os dados no formato padrão:
       (rotas, custo total, número de veículos).

    2. Cálculo de Custo com Penalização: Implementa uma métrica de avaliação
       que soma as distâncias euclidianas e aplica uma penalidade caso o
       número de veículos exceda o limite definido (k_alvo). Isso permite que
       o algoritmo de busca "sinta" o custo de usar veículos extras, facilitando
       a convergência para soluções viáveis em relação à frota.

    3. Validação de Viabilidade Unificada: Centraliza as regras de negócio do
       problema, verificando tanto a Capacidade do Veículo quanto a Autonomia
       Máxima (Distância + Tempo de Serviço). Já que há instâncias com esses
       dados adicionais que devem ser levados em conta

    Ao herdar desta classe, foca-se apenas na lógica de agrupamento nas classes de heurísticas
    e roteirização, enquanto a infraestrutura de validação e custo é reutilizada.
    """
    nome: str = "BASE"


    @abstractmethod
    def resolver(self, inst, k_alvo=None) -> Tuple[List[List[int]], float, int]:
        """Retorna (rotas, custo_total, n_veiculos)"""
        pass

    def calcular_custo(self, inst, rotas: List[List[int]], k_alvo= None) -> float:
        """
        Calcula o custo total considerando Distâncias
        """
        custo_viagem = 0.0
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

        # Penalidade α*max{0, k_alvo-k} + β*max{0, k-k_alvo}
        if k_alvo is not None:
            k = sum(1 for r in rotas if r)
           # não incluimos penalidade para ser menos veiculo porque tecnicamente quanto menos melhor se o custo também for menor
            custo_viagem +=  50 * max(0, k - k_alvo)


        return custo_viagem

    def validar_viabilidade(self, inst, rota: List[int]) -> bool:
        # 1. Capacidade
        carga_total = sum(inst.grafo.nos[c].demanda for c in rota)
        if carga_total > inst.capacidade:
            return False

        # 2. Distância e autonomia (só se houver limite finito)
        max_dist = getattr(inst, 'max_distancia', float('inf')) # ASSUMINDO que não existe SERVICE_TIME sem DISTANCE nas instâncias
        if max_dist == float('inf'):
            return True  # Sem restrição de autonomia, encerra aqui

        dep = inst.id_deposito
        grafo = inst.grafo

        dist_total = grafo.dist(dep, rota[0])
        for i in range(len(rota) - 1):
            dist_total += grafo.dist(rota[i], rota[i + 1])
        dist_total += grafo.dist(rota[-1], dep)


        st_unitario = getattr(inst, 'tempo_servico', 0.0)

        if st_unitario == 0.0:
            custo_total = dist_total
        else:
            # O limite DISTANCE engloba distância + service time (jornada total)
            custo_total = dist_total + (len(rota) * st_unitario)


        if custo_total > max_dist:
            return False

        return True