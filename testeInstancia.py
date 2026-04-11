from core.Instancia_cvrp import InstanciaCvrp
from Heuristicas.clarke_wright import ClarkeWright
from Heuristicas.nearest_neighbor import NearestNeighbor
from Heuristicas.sweep import Sweep
from Heuristicas.adaptive_insertion import AdaptiveInsertion
from Heuristicas.christofides_like import ChristofidesLike
from saida.resultados import executar_instancia
from saida.terminal import cabecalho_sistema, mensagem_sucesso, mensagem_info, mensagem_aviso

MELHORES = {
    "A-n32-k5":       784.0,
    "A-n33-k5":       661.0,
    "Golden_18":      995.13,
    "Golden_3":       10997.80,
    "Loggi-n601-k42": 347046.00,
}

heuristicas = [
    ClarkeWright(),
    NearestNeighbor(),
    Sweep(),
    AdaptiveInsertion(),
    ChristofidesLike(),
]

instancias = [
    InstanciaCvrp.ler_arquivo("Benchmark/A-n32-k5.vrp"),
    InstanciaCvrp.ler_arquivo("Benchmark/A-n33-k5.vrp"),
    InstanciaCvrp.ler_arquivo("Benchmark/Golden_18.vrp"),
    InstanciaCvrp.ler_arquivo("Benchmark/Golden_3.vrp"),
    InstanciaCvrp.ler_arquivo("Benchmark/Loggi-n601-k42.vrp"),
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
        arquivo_resultado="resultado/resultados.dat",
        pasta_plots="resultado",
    )

mensagem_sucesso("Testes concluídos!")
mensagem_info("Arquivo de resultados: resultado/resultados.dat")