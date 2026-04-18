import os
import sys
import pandas as pd

# Garante que a raiz do projeto está no path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.Instancia_cvrp import InstanciaCvrp
from saida.execution import executar_instancia, CABECALHO
from saida.graphics import gerar_graficos

# Heurísticas
# from Heuristicas.clarke_wright    import ClarkeWright
# from Heuristicas.nearest_neighbor import NearestNeighbor
# from Heuristicas.sequential_insertion import MoleJameson
# from Heuristicas.sweep            import Sweep

# Configurações do benchmark
from instancesConfig import INSTANCIAS, HEURISTICAS  # Importa a lista de instâncias e seus BKS e K

# Extrair para arquivo de configuração
# INSTANCIAS = [
#     ("A-n80-k10", 1763.00), ("F-n72-k4", 237.00), ("E-n101-k14", 1067.00),
#     ("F-n135-k7", 1162.00), ("M-n151-k12", 1015.00), ("Golden_18", 995.13),
#     ("CMT10", 1395.85), ("tai150b", 2727.03), ("tai385", 24366.41),
#     ("Golden_3", 10997.80), ("Li_21", 16212.83), ("X-n502-k39", 69226.00),
#     ("Loggi-n601-k42", 347046.00), ("XL-n1701-k562", 521136.00), ("XL-n2541-k121", 146390.00),
# ]

PASTA_INSTANCIAS = "Benchmark"
ARQUIVO_DAT      = "resultados/resultados.dat"
PASTA_PLOTS      = "resultados"
N_EXECUCOES      = 1  # Definido conforme necessidade do benchmark

# HEURISTICAS = [ClarkeWright(), NearestNeighbor(), MoleJameson(), Sweep()]

def preparar_arquivo_resultados():
    """Cria a pasta e reseta o arquivo com o cabeçalho."""
    os.makedirs(os.path.dirname(ARQUIVO_DAT), exist_ok=True)
    with open(ARQUIVO_DAT, "w", encoding="utf-8") as f:
        f.write("\t".join(CABECALHO) + "\n")
    print(f"[benchmark] Arquivo inicializado: {ARQUIVO_DAT}")

def main():
    preparar_arquivo_resultados()
    # total_inst = len(INSTANCIAS) Para que essa linha ?

    for n in range(1, N_EXECUCOES + 1):
        print(f"\n>>> INICIANDO RODADA {n}/{N_EXECUCOES}")
        for idx, (nome, bks, melhor_k) in enumerate(INSTANCIAS, start=1):
            caminho_vrp = os.path.join(PASTA_INSTANCIAS, f"{nome}.vrp")

            if not os.path.isfile(caminho_vrp):
                continue

            try:
                inst = InstanciaCvrp.ler_arquivo(caminho_vrp)
                # O executar_instancia agora apenas faz append no arquivo
                executar_instancia(
                    heuristicas=HEURISTICAS.values(),
                    inst=inst,
                    melhor_conhecido=bks,
                    melhor_k=melhor_k,
                    arquivo_resultado=ARQUIVO_DAT,
                    pasta_plots=PASTA_PLOTS
                )
            except Exception as e:
                print(f"  Erro em {nome}: {e}")

    print("\nGerando análise estatística e gráficos...")
    gerar_graficos(ARQUIVO_DAT, PASTA_PLOTS)
    print("Benchmark Finalizado.")

if __name__ == "__main__":
    main()
    # gerar_graficos(ARQUIVO_DAT, PASTA_PLOTS)