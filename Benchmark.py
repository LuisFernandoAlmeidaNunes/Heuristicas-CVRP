import os
import sys


# Garante que a raiz do projeto está no path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.Instancia_cvrp import InstanciaCvrp
from saida.execution import executar_instancia, CABECALHO
from saida.graphics import gerar_graficos, plotar_comparativo



# Configurações do benchmark
from instancesConfig import INSTANCIAS, HEURISTICAS  # Importa a lista de instâncias e seus BKS e K

PASTA_INSTANCIAS = "Benchmark"
ARQUIVO_DAT      = "resultados/resultados.dat"
PASTA_PLOTS      = "resultados"
N_EXECUCOES      = 50

def preparar_arquivo_resultados():
    """Cria a pasta e reseta o arquivo com o cabeçalho."""
    os.makedirs(os.path.dirname(ARQUIVO_DAT), exist_ok=True)
    with open(ARQUIVO_DAT, "w", encoding="utf-8") as f:
        f.write("\t".join(CABECALHO) + "\n")
    print(f"[benchmark] Arquivo inicializado: {ARQUIVO_DAT}")


def main():
    preparar_arquivo_resultados()

    for n in range(1, N_EXECUCOES + 1):
        print(f"\n>>> INICIANDO RODADA {n}/{N_EXECUCOES}")
        for idx, (nome, bks, melhor_k) in enumerate(INSTANCIAS, start=1):
            print(f"{nome}: bks={bks}, melhor_k={melhor_k}")  # visualizar qq ta acontecendo c/ os resultados
            caminho_vrp = os.path.join(PASTA_INSTANCIAS, f"{nome}.vrp")
            if not os.path.isfile(caminho_vrp):
                continue
            try:
                inst = InstanciaCvrp.ler_arquivo(caminho_vrp)
                executar_instancia(
                    heuristicas=HEURISTICAS.values(),
                    inst=inst,
                    melhor_conhecido=bks,
                    melhor_k=melhor_k,
                    arquivo_resultado=ARQUIVO_DAT,
                    pasta_plots=PASTA_PLOTS
                )
                # pra que isso?
                # Gera comparativo só na primeira rodada e na instância escolhida
                if n == 1 and nome in INSTANCIAS:
                    resultados_rotas = {}
                    for h in HEURISTICAS.values():
                        rotas, custo, k = h.resolver(inst)
                        resultados_rotas[h.nome] = (rotas, custo)

                    melhor_nome = min(resultados_rotas, key=lambda x: resultados_rotas[x][1])
                    pior_nome   = max(resultados_rotas, key=lambda x: resultados_rotas[x][1])

                    plotar_comparativo(
                        inst=inst,
                        rotas_melhor=resultados_rotas[melhor_nome][0],
                        rotas_pior=resultados_rotas[pior_nome][0],
                        metodo_melhor=melhor_nome,
                        metodo_pior=pior_nome,
                        pasta_saida=PASTA_PLOTS
                    )

            except Exception as e:
                print(f"  Erro em {nome}: {e}")

    print("\nGerando análise estatística e gráficos...")
    print("Benchmark Finalizado.")

if __name__ == "__main__":
    main()
    # gerar_graficos(ARQUIVO_DAT, PASTA_PLOTS)