import os
import sys
from Statistics.teste_hipotese import executar_analise_estatistica

# Este script coordena o pipeline completo de experimentos para o CVRP.
# Ele realiza a execução em lote das heurísticas, gera as visualizações de
# resultados e conduz a análise estatística rigorosa.
#
# O fluxo segue três etapas principais:
#
# 1. Execução: As heurísticas (CW, MJ, NN, SW) são testadas em um conjunto
#    de 15 instâncias. Definimos N_EXECUCOES para permitir o cálculo do
#    Intervalo de Confiança (IC 95%), garantindo que os resultados não
#    sejam baseados em uma única rodada.
#
# 2. Processamento: Através da função processar_resultados_finais, o script
#    consolida os dados brutos, gera gráficos de comparação (Boxplots e IC),
#    além de exportar as tabelas de benchmark com as BKS de cada instância.
#
# 3. Validação: A etapa final executa os testes de Friedman e Wilcoxon.
#    Esta análise não-paramétrica é o que valida cientificamente se uma
#    heurística é superior à outra através de postos (ranks), eliminando
#    distorções causadas por outliers ou escalas diferentes de instâncias.


# Garante que a raiz do projeto está no path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.Instancia_cvrp import InstanciaCvrp
from saida.execution import executar_instancia, CABECALHO
from saida.graphics import processar_resultados_finais

# Configurações do benchmark
from instancesConfig import INSTANCIAS, HEURISTICAS  # Importa a lista de instâncias e seus BKS e K

PASTA_INSTANCIAS = "Benchmark"
ARQUIVO_DAT      = "resultados/resultados.dat"
PASTA_PLOTS      = "resultados"
N_EXECUCOES = 2  # MÍNIMO para IC 95%

def preparar_arquivo_resultados():
    """Cria a pasta e reseta o arquivo com o cabeçalho."""
    os.makedirs(os.path.dirname(ARQUIVO_DAT), exist_ok=True)
    with open(ARQUIVO_DAT, "w", encoding="utf-8") as f:
        f.write("\t".join(CABECALHO) + "\n")
    print(f"[benchmark] Arquivo inicializado: {ARQUIVO_DAT}")


def main():
    preparar_arquivo_resultados()

    INSTANCIAS_COMPARATIVO = {"Li_21", "Golden_3", "XL-n2541-k121"}  

    for n in range(1, N_EXECUCOES + 1):
        print(f"\n>>> RODADA {n}/{N_EXECUCOES}")
        for idx, (nome, bks, melhor_k) in enumerate(INSTANCIAS, start=1):
            print(f"[{idx}/15] {nome}")
            caminho_vrp = os.path.join(PASTA_INSTANCIAS, f"{nome}.vrp")

            if not os.path.isfile(caminho_vrp):
                print(f"Arquivo não encontrado: {caminho_vrp}")
                continue

            try:
                inst = InstanciaCvrp.ler_arquivo(caminho_vrp)
                executar_instancia(
                    heuristicas=HEURISTICAS.values(),
                    inst=inst,
                    melhor_conhecido=bks,
                    melhor_k=melhor_k,
                    is_beenchmark=False
                )
            except Exception as e:
                print(f"Erro: {e}")

    processar_resultados_finais(ARQUIVO_DAT, PASTA_PLOTS)
    tabela_estatistica = os.path.join(PASTA_PLOTS, "tabela_estatistica_gaps.csv")
    executar_analise_estatistica(tabela_estatistica, PASTA_PLOTS)
    print("\n✅ Benchmark concluído!")

if __name__ == "__main__":
    main()

