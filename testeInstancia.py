from core.Instancia_cvrp import InstanciaCvrp
from heuristicas.dsn import Dsn

# Melhores conhecidos
MELHORES = {
    "A-n32-k5": 784.0,
    "A-n33-k5": 661.0
}

# passo 1 — lê instâncias (grafo criado internamente!)
print("LENDO INSTÂNCIAS...")
inst1 = InstanciaCvrp.ler_arquivo("Benchmark/A-n32-k5.vrp")
inst2 = InstanciaCvrp.ler_arquivo("Benchmark/A-n33-k5.vrp")

print(f"✓ Instância 1: {inst1}")
print(f"✓ Instância 2: {inst2}")

# passo 2 — loop nas instâncias
for inst in [inst1, inst2]:
    print('\n' + '=' * 60)
    print(f'INSTÂNCIA: {inst.nome}')
    print(f'Clientes: {len(inst.ids_clientes)} | Capacidade: {inst.capacidade}')
    print(f'Depósito: {inst.id_deposito}')
    print('=' * 60)

    # Testa grafo
    print('\n📊 TESTANDO GRAFO:')
    print(f'  Nós totais: {len(inst.grafo.nos)}')
    print(f'  Arestas: {len(inst.grafo.arestas)}')
    print(f'  Distância (1→2): {inst.grafo.dist(1, 2):.2f}')

    print(f'\n📦 TESTANDO DEMANDAS:')
    print(f'  Cliente 2: {inst.grafo.nos[2].demanda}')
    print(f'  Cliente 1: {inst.grafo.nos[1].demanda}')

    # Testa DSN
    print('\n🚛 RODANDO DSN:')
    dsn = Dsn()
    rotas, custo, n_veiculos = dsn.resolver(inst)

    # Calcula GAP
    melhor = MELHORES[inst.nome]
    gap = 100 * abs(custo - melhor) / melhor

    print(f'\n📈 RESULTADOS:')
    print(f'  Veículos:  {n_veiculos}')
    print(f'  Custo:     {custo:.2f}')
    print(f'  Ótimo:     {melhor:.2f}')
    print(f'  GAP:       {gap:.2f}%')
    print(f'  Heurística:{dsn.nome}')

    # Valida solução
    todas_validas = all(dsn.validar_capacidade(inst, rota) for rota in rotas)
    print(f'  Válida:    {"✅" if todas_validas else "❌"}')

    print('\n🛤️ ROTAS:')
    for i, rota in enumerate(rotas):
        caminho = " → ".join(map(str, [inst.id_deposito] + rota + [inst.id_deposito]))
        carga = sum(inst.grafo.nos[j].demanda for j in rota)
        print(f'  R{i + 1:2d}: {caminho} (carga: {carga}/{inst.capacidade})')

print('\n🎉 TESTES CONCLUÍDOS!')