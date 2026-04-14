
from core.Instancia_cvrp import InstanciaCvrp
from Heuristicas.clarke_wright import ClarkeWright
from Heuristicas.nearest_neighbor import NearestNeighbor
from Heuristicas.sweep import Sweep
from Heuristicas.sequential_insertion import MoleJameson
from saida.execution import executar_instancia
from saida.terminal import cabecalho_sistema, mensagem_sucesso, mensagem_info, mensagem_aviso

MELHORES = {
    "A-n80-k10":       1763.00,
    "F-n72-k4":        237.00,
    "Golden_18":      995.13,
    "Golden_3":       10997.80,
    "Loggi-n601-k42": 347046.00,
    "XL-n1701-k562":   521136.00,
    "XL-n2541-k121":   146390.00,
    "CMT10":           1395.85,
    "Li_21":            16212.83,
    "tai150b":         2727.03,
}

heuristicas = [
    ClarkeWright(),
    NearestNeighbor(),
    Sweep(),
    MoleJameson()
]

instancias = [
    # InstanciaCvrp.ler_arquivo("Benchmark/A-n80-k10.vrp"), #pequeno
    # InstanciaCvrp.ler_arquivo("Benchmark/F-n72-k4.vrp"), #pequeno
    # InstanciaCvrp.ler_arquivo("Benchmark/Golden_18.vrp"), #medio
    InstanciaCvrp.ler_arquivo("Benchmark/Golden_3.vrp"), #medio
    InstanciaCvrp.ler_arquivo("Benchmark/CMT10.vrp"),
    InstanciaCvrp.ler_arquivo("Benchmark/Li_21.vrp"),
    # InstanciaCvrp.ler_arquivo("Benchmark/Loggi-n601-k42.vrp"), #grande tratar
    # InstanciaCvrp.ler_arquivo("Benchmark/XL-n1701-k562.vrp"), #grande
    # InstanciaCvrp.ler_arquivo("Benchmark/XL-n2541-k121.vrp") #grande
]

# ── Exibe banner ──────────────────────────────────────────────────────────────
cabecalho_sistema()

# ── Carrega instâncias ────────────────────────────────────────────────────────
print("  Carregando instâncias...\n")
for i, inst in enumerate(instancias, start=1):
    mensagem_sucesso(f"Instância {i}: {inst}")

# ── Roda benchmark ────────────────────────────────────────────────────────────
for inst in instancias:
    if inst.nome not in MELHORES:
        mensagem_aviso(f"BKS não cadastrado para '{inst.nome}', pulando.")
        continue

    executar_instancia(
        heuristicas=heuristicas,
        inst=inst,
        melhor_conhecido=MELHORES[inst.nome],
        arquivo_resultado="resultados/resultados.dat",
        pasta_plots="resultados",
    )


mensagem_sucesso("Testes concluídos!")
mensagem_info("Arquivo de resultados: resultados/resultados.dat")