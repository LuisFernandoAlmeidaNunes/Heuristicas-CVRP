from Arestas import read_file
from Instancia import Instancia 

# passo 1 — gera o arquivo de arestas )
read_file("Benchmark/A-n32-k5.vrp")
read_file("Benchmark/A-n33-k5.vrp")


# passo 2 — lê instância e arestas
inst1 = Instancia.ler_arquivo("Benchmark/A-n32-k5.vrp")
inst2 = Instancia.ler_arquivo("Benchmark/A-n33-k5.vrp")

# passo 3 - exibe as duas instancias e infos
for inst in [inst1, inst2]:
    print('NOME:', inst.nome)
    print('CAPACIDADE:', inst.capacidade)
    print('ID DEPÓSITO:', inst.id_deposito)
    print('COORDENADAS:', inst.coordenadas)
    # Instancia(A-n32-k5, n=31, Q=100)

    print('-' * 40)
    # distância entre nó 1 e nó 2
    print('DISTÂNCIA entre nó 1 e nó 2:')
    print(inst.dist(1, 2))
    # 34.93

    print('-' * 40)
    # demanda do cliente 2
    print('DEMANDA do cliente 2:')
    print(inst.demandas[2])
    # 19

    print('-' * 40)