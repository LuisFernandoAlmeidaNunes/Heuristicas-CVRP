from core.Arestas import read_file
from core.Instancia import Instancia
from Heuristicas.DSN import DSN  # ok ser maiúsculo

# passo 1 — gera o arquivo de arestas
read_file("Benchmark/A-n32-k5.vrp")
read_file("Benchmark/A-n33-k5.vrp")

# passo 2 — lê instância e arestas
inst1 = Instancia.ler_arquivo("Benchmark/A-n32-k5.vrp")
inst2 = Instancia.ler_arquivo("Benchmark/A-n33-k5.vrp")

# melhores conhecidos (fora do loop!)
melhores = {
    "A-n32-k5": 784.0,
    "A-n33-k5": 661.0
}

# passo 3 — loop nas instâncias
for inst in [inst1, inst2]:

    print('\n' + '='*40)
    print('NOME:', inst.nome)
    print('CAPACIDADE:', inst.capacidade)
    print('ID DEPÓSITO:', inst.id_deposito)

    print('-' * 40)
    print('DISTÂNCIA entre nó 1 e nó 2:')
    print(inst.dist(1, 2))

    print('-' * 40)
    print('DEMANDA do cliente 2:')
    print(inst.demandas[2])

    print('-' * 40)

    # testando DSN
    print('TESTANDO DSN:')

    rotas, custo, C = DSN(inst)

    melhor = melhores[inst.nome]
    gap = 100 * abs(custo - melhor) / melhor

    print(f"Veículos usados:  {C}")
    print(f"Custo total:      {custo:.2f}")
    print(f"Melhor conhecido: {melhor:.2f}")
    print(f"GAP:              {gap:.2f}%")

    print('-' * 40)

    # imprime rotas
    for i, rota in enumerate(rotas):
        caminho = " → ".join(map(str, [inst.id_deposito] + rota + [inst.id_deposito]))
        print(f"Rota {i+1}: {caminho}")