import pandas as pd
import os
from scipy.stats import friedmanchisquare, wilcoxon
from itertools import combinations


def executar_analise_estatistica(caminho_tabela_gaps, pasta_resultados):
    """
    JUSTIFICATIVA DA METODOLOGIA ESTATÍSTICA (Fundamentado em Demšar (2006) — Statistical Comparisons of Classifiers over Multiple Data Sets)

    Optamos por uma abordagem não-paramétrica para validar a comparação entre as heurísticas
    pelos seguintes fundamentos científicos:

    1. Ausência de Normalidade: Os dados de Gap e Runtime em problemas de otimização combinatória
       frequentemente apresentam distribuições assimétricas e outliers, o que viola os pressupostos
       de testes paramétricos como o Teste T ou Z.

    2. Teste de Friedman (Global): Utilizado para detectar se existe uma diferença estatisticamente
       significativa entre pelo menos dois dos algoritmos. Trabalha com a ordenação (ranks) dos
       métodos em cada instância, tornando a análise robusta a variações de escala entre instâncias.

    3. Teste de Wilcoxon Signed-Rank (Post-hoc): Aplicado após o Friedman para realizar comparações
       par a par. É o teste mais adequado para amostras pareadas (mesmas instâncias resolvidas por
       diferentes métodos) em contextos não-paramétricos.

    4. Correção de Bonferroni: Aplicada para ajustar o nível de significância (alfa) face as
       múltiplas comparações (6 pares), reduzindo a probabilidade de erros do Tipo I (falsos positivos).
"""


    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJ_ROOT = os.path.dirname(SCRIPT_DIR)
    PASTA_RESULTADOS = os.path.join(PROJ_ROOT, "resultados")

    caminho_tabela = os.path.join(PASTA_RESULTADOS, "tabela_estatistica_gaps.csv")
    caminho_saida_estatistica = os.path.join(PASTA_RESULTADOS, "relatorio_teste_hipótese.csv")

    if not os.path.exists(caminho_tabela):
        print(f"ERRO: O arquivo não foi encontrado em: {caminho_tabela}")
        print(f"Verifique se a pasta 'resultados' está no local: {PROJ_ROOT}")

    # CARREGAMENTO DOS DADOS
    df = pd.read_csv(caminho_tabela)

    # metodo hardcoded para instances do benchmark, onde as colunas de interesse são os métodos (heurísticas) e as linhas são as instâncias
    # metodos = ['CW (Clarke & Wright Savings)', 'MJ (Mole & Jameson)', 'NN (Nearest Neighbor)', 'SW (Sweep)']
    metodos = [col for col in df.columns if col != "INSTANCE"]

    print(f"=== Iniciando Análise Estatística (n={len(df)} instâncias) ===")

    # 3. TESTE DE FRIEDMAN (GLOBAL)
    # O asterisco (*) expande a lista de colunas para a função
    data_to_test = [df[m] for m in metodos]
    stat, p_friedman = friedmanchisquare(*data_to_test)

    resultados_lista = [{"Comparacao": "GLOBAL (Friedman)", "p-value": p_friedman,
                         "Status": "Significativo" if p_friedman < 0.05 else "Equivalente"}]


    # TESTE DE WILCOXON (PAR A PAR)
    if p_friedman < 0.05:
        
        n_comparacoes = len(list(combinations(metodos, 2))) # calcular qnts pares existem

        limite_bonferroni = 0.05 / n_comparacoes

        for h1, h2 in combinations(metodos, 2):
            _, p_wilcoxon = wilcoxon(df[h1], df[h2])
            status = "Diferente (Significativo)" if p_wilcoxon < limite_bonferroni else "Equivalente"

            # Guardar para o CSV
            resultados_lista.append({
                "Comparacao": f"{h1} vs {h2}",
                "p-value": p_wilcoxon,
                "Status": status
            })


    # SALVAR NO CSV
    df_resultado = pd.DataFrame(resultados_lista)
    df_resultado.to_csv(caminho_saida_estatistica, index=False, encoding='utf-8')
    print(f"\n[Sucesso] Relatório salvo em: {caminho_saida_estatistica}")