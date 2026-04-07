from core.Instancia_cvrp import InstanciaCvrp
from heuristicas.clarke_wright import ClarkeWright
from heuristicas.nearest_neighbor import NearestNeighbor
from heuristicas.sweep import Sweep

MELHORES = {
    "A-n32-k5": 784.0,
    "A-n33-k5": 661.0
}

#para testar novas heurísticas é só adicionar aqui embaixo
heuristicas = [
    NearestNeighbor(),
    ClarkeWright(),
    Sweep()
]

#adicionar aqui as instâncias que devem ser testadas
instancias = [
    InstanciaCvrp.ler_arquivo("Benchmark/A-n32-k5.vrp"),
    InstanciaCvrp.ler_arquivo("Benchmark/A-n33-k5.vrp")
]

print("LENDO INSTÂNCIAS...")
for i, inst in enumerate(instancias, start=1):
    print(f"✓ Instância {i}: {inst}")

for inst in instancias:
    print("\n" + "=" * 90)
    print(f"INSTÂNCIA: {inst.nome}")
    print(f"Clientes: {len(inst.ids_clientes)} | Capacidade: {inst.capacidade} | Depósito: {inst.id_deposito}")
    print("=" * 90)

    print("\n📊 DADOS DA INSTÂNCIA")
    print(f"Nós totais: {len(inst.grafo.nos)}")
    print(f"Arestas:    {len(inst.grafo.arestas)}")
    print(f"Dist(1,2):  {inst.grafo.dist(1, 2):.2f}")
    print(f"Demanda 1:  {inst.grafo.nos[1].demanda}")
    print(f"Demanda 2:  {inst.grafo.nos[2].demanda}")

    melhor = MELHORES[inst.nome]
    resultados = []

    for heuristica in heuristicas:
        rotas, custo, n_veiculos = heuristica.resolver(inst)
        gap = 100 * abs(custo - melhor) / melhor
        valida = all(heuristica.validar_capacidade(inst, rota) for rota in rotas)

        resultados.append({
            "heuristica": heuristica.nome,
            "rotas": rotas,
            "custo": custo,
            "veiculos": n_veiculos,
            "gap": gap,
            "valida": valida
        })

    resultados.sort(key=lambda x: x["custo"])

    print("\n📈 RESULTADOS DAS HEURÍSTICAS")
    print("-" * 90)
    print(f"{'Heurística':<35} {'Custo':>12} {'Veículos':>10} {'GAP(%)':>10} {'Válida':>10}")
    print("-" * 90)

    for r in resultados:
        print(f"{r['heuristica']:<35} {r['custo']:>12.2f} {r['veiculos']:>10} {r['gap']:>10.2f} {('✅' if r['valida'] else '❌'):>10}")

    print("-" * 90)
    print(f"{'Melhor conhecido':<35} {melhor:>12.2f}")
    print(f"{'Melhor heurística':<35} {resultados[0]['heuristica']}")

    for r in resultados:
        print("\n" + "-" * 90)
        print(f"🛤️ ROTAS — {r['heuristica']}")
        print("-" * 90)

        for i, rota in enumerate(r["rotas"], start=1):
            caminho = " → ".join(map(str, [inst.id_deposito] + rota + [inst.id_deposito]))
            carga = sum(inst.grafo.nos[j].demanda for j in rota)
            print(f"R{i:02d}: {caminho} | carga: {carga}/{inst.capacidade}")

print("\nTESTES CONCLUÍDOS!")