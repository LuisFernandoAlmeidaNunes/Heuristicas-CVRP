"""
    python Benchmark.py
"""

import os
import sys

# ── Garante que a raiz do projeto está no path ────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Imports do próprio projeto ────────────────────────────────────────────────
from core.Instancia_cvrp import InstanciaCvrp
from saida.resultados import executar_instancia
from saida.graficos import gerar_graficos

# ── Heurísticas disponíveis ───────────────────────────────────────────────────
from Heuristicas.clarke_wright    import ClarkeWright       # CW
from Heuristicas.nearest_neighbor import NearestNeighbor    # NN
from Heuristicas.sequential_insertion import MoleJameson    # MJ
from Heuristicas.sweep            import Sweep              # SW
# Adicione ou remova conforme o que seu grupo implementou

# ─────────────────────────────────────────────────────────────────────────────
# Tabela com todas as 15 instâncias do enunciado
# Formato: (nome_arquivo_sem_extensao, melhor_conhecido)
# ─────────────────────────────────────────────────────────────────────────────
INSTANCIAS = [
    # Small
    ("A-n80-k10",      1763.00),
    ("F-n72-k4",        237.00),
    ("E-n101-k14",      106.00),   # atenção: BKS = 106 (já estava errado no enunciado)
    ("F-n135-k7",      1162.00),
    ("M-n151-k12",     1015.00),
    # Medium
    ("Golden_18",       995.13),
    ("CMT10",          1395.85),
    ("tai150b",        2727.03),
    ("tai385",        24366.41),
    ("Golden_3",      10997.80),
    # Large
    ("Li_21",         16212.83),
    ("X-n502-k39",    69226.00),
    ("Loggi-n601-k42",347046.00),
    ("XL-n1701-k562", 521136.00),
    ("XL-n2541-k121", 146390.00),
]

# ─────────────────────────────────────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────────────────────────────────────
PASTA_INSTANCIAS = "Benchmark"          # onde ficam os arquivos .vrp
ARQUIVO_DAT      = "resultado/resultados.dat"
PASTA_PLOTS      = "resultado"

# Heurísticas que serão usadas em todas as instâncias
HEURISTICAS = [
    ClarkeWright(),
    NearestNeighbor(),
    MoleJameson(),  
    Sweep(),                
]

# ─────────────────────────────────────────────────────────────────────────────
# Função auxiliar: limpa o .dat antes de começar (resolve o TODO do resultados.py)
# ─────────────────────────────────────────────────────────────────────────────
def limpar_resultados():
    if os.path.isfile(ARQUIVO_DAT):
        os.remove(ARQUIVO_DAT)
        print(f"[benchmark] Arquivo anterior removido: {ARQUIVO_DAT}")


# ─────────────────────────────────────────────────────────────────────────────
# Loop principal
# ─────────────────────────────────────────────────────────────────────────────
def main():
    limpar_resultados()

    total   = len(INSTANCIAS)
    falhas  = []

    for idx, (nome, bks) in enumerate(INSTANCIAS, start=1):
        caminho_vrp = os.path.join(PASTA_INSTANCIAS, f"{nome}.vrp")

        print(f"\n{'='*60}")
        print(f"[{idx}/{total}] {nome}  (BKS = {bks})")
        print(f"{'='*60}")

        if not os.path.isfile(caminho_vrp):
            print(f"  AVISO: arquivo não encontrado → {caminho_vrp}  (pulando)")
            falhas.append(nome)
            continue

        try:
            inst = InstanciaCvrp.ler_arquivo(caminho_vrp)
            executar_instancia(
                heuristicas      = HEURISTICAS,
                inst             = inst,
                melhor_conhecido = bks,
                arquivo_resultado= ARQUIVO_DAT,
                pasta_plots      = PASTA_PLOTS,
            )
        except Exception as e:
            print(f"  ERRO em {nome}: {e}")
            falhas.append(nome)

    # ── Relatório final ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Benchmark concluído.  {total - len(falhas)}/{total} instâncias processadas.")
    if falhas:
        print(f"  Instâncias com falha: {', '.join(falhas)}")

    # ── Gera os três gráficos ─────────────────────────────────────────────────
    print("\nGerando gráficos de análise...")
    gerar_graficos(ARQUIVO_DAT, PASTA_PLOTS)
    print("Pronto! Verifique a pasta resultado/")


if __name__ == "__main__":
    main()