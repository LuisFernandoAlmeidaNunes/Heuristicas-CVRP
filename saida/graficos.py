"""
saida/graficos.py

Gera os três gráficos exigidos pelo enunciado:
  1. Gráfico de barras — tempo de execução por instância/heurística
  2. Boxplot dos gaps por heurística
  3. Intervalo de confiança de 95% do gap médio por heurística

Uso:
    python -m saida.graficos resultado/resultados.dat
"""

import os
import sys
import math
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# Leitura do arquivo de resultados
def carregar_resultados(caminho):
    """Lê o resultados.dat (TSV com cabeçalho) e devolve um DataFrame."""
    df = pd.read_csv(caminho, sep="\t", encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    df["OBJECTIVE"] = pd.to_numeric(df["OBJECTIVE"], errors="coerce")
    df["RUNTIME"]   = pd.to_numeric(df["RUNTIME"],   errors="coerce")
    df["GAP"]       = pd.to_numeric(df["GAP"],        errors="coerce")
    return df

# ─────────────────────────────────────────────────────────────────────────────
# 1. Gráfico de barras — Tempo de execução
# ─────────────────────────────────────────────────────────────────────────────
def grafico_barras_runtime(df, pasta_saida):
    """
    Barras agrupadas por instância, uma barra por heurística.
    Eixo X  = instâncias
    Eixo Y  = tempo de execução 
    """
    tabela =df.pivot_table(index="INSTANCE", columns="METHOD", values="RUNTIME")

    cores = {
        'CW (Clarke & Wright Savings)': '#2E8B57',  # Verde floresta (rápido/bom)
        'NN (Nearest Neighbor)': '#FF6347',        # Tomate (baseline)
        'SW (Sweep)': '#4682B4',                    # Aço azul (cluster)
        'MJ (Mole & Jameson)': '#9932CC'             # Orquídea (christofides)
    }

    ax = tabela.plot(
        kind="bar",
        figsize=(12, 6),
        width=0.8,
        edgecolor="black",
        linewidth=0.7,
        color=[cores.get(col, "#808080") for col in tabela.columns]
    )
    
    ax.set_title("Tempo de Execução por Instância e Heurística", fontsize=13, fontweight="bold")
    ax.set_xlabel("Instância", fontsize=11)
    ax.set_ylabel("Tempo (s)", fontsize=11)

    plt.xticks(rotation=45, ha="right") # rotaciona e alinha rotulos
    plt.tight_layout() # espaçamento para não cortar os rótulos

    caminho = os.path.join(pasta_saida, "grafico_barras_runtime.png")

    plt.savefig(caminho)
    plt.close()
    return caminho

# ─────────────────────────────────────────────────────────────────────────────
# 2. Boxplot dos gaps por heurística
# ─────────────────────────────────────────────────────────────────────────────
def grafico_boxplot_gap(df, pasta_saida):

    cores = ['#2E8B57', '#FF6347', '#4682B4', '#DAA520', '#9932CC']

     # Agrupa por heurística e plota com cores
    fig, ax = plt.subplots(figsize=(10, 6))
    box_plot = df.boxplot(column="GAP", by="METHOD", ax=ax, 
                          patch_artist=True,  # Permite colorir boxes
                          color='black')      # Borda preta
    
    # ***MUDA CORES DOS BOXES***
    for patch, color in zip(box_plot.artists, cores):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)  # Transparência

    ax = df.boxplot(column="GAP", by="METHOD", figsize=(8,6))
    plt.title("Distribuição dos Gaps por Heurística", fontsize=13, fontweight="bold")
    plt.suptitle("") # remove titulo automatico do boxplot
    plt.ylabel("Gap (%)", fontsize=11)

    plt.xticks(rotation=20, ha="right") # rotaciona e alinha rotulos
    plt.margins(x=0.08)
    plt.subplots_adjust(bottom=0.2) # espaço para rótulos

    caminho = os.path.join(pasta_saida, "grafico_boxplot_gap.png")    
    plt.savefig(caminho)
    plt.close()
    return caminho

# ─────────────────────────────────────────────────────────────────────────────
# 3. Intervalo de confiança 95% do gap médio
# ─────────────────────────────────────────────────────────────────────────────
def grafico_ic_gap(df, pasta_saida):
    """
    Plota o gap médio de cada heurística com barras de erro (IC 95% — t de Student).
    IC = média ± t_{α/2, n-1} * (desvio_padrão / sqrt(n))
    """

    grupos = df.groupby("METHOD")["GAP"]

    medias = grupos.mean()
    desvio = grupos.std()
    n = grupos.count()

    ep = desvio/np.sqrt(n) # erro padrão
    t = stats.t.ppf(0.975, n-1) # t student crítico para 95% e n-1 graus de liberdade
    margem = t * ep
    # calcula a amrgem de erro se nao for possivel calcular (n=1) ou se o desvio for zero, a margem é zero
    margem = margem.fillna(0) # trata casos com n=1 (desvio=NaN)

    cores = {
        "CW": '#2E8B57',    # Verde (vencedor)
        "NN": '#FF6347',    # Vermelho (baseline)
        "SW": '#4682B4',    # Azul (cluster)
        "ML": '#DAA520',    # Dourado
    }
    
    # ***USE AS CORES***
    cores_plot = [cores.get(m, '#7f7f7f') for m in medias.index]

    ax = medias.plot(kind="bar", yerr=margem, capsize=6, color=cores_plot, figsize=(8,6), edgecolor="black", width=0.65)
    ax.set_title("Gap Médio por Heurística com IC 95%", fontsize=13, fontweight="bold")
    ax.set_ylabel("Gap (%)", fontsize=11)

    plt.xticks(rotation=20, ha="right") # rotaciona e alinha rotulos
    plt.margins(x=0.08)
    plt.subplots_adjust(bottom=0.2) # espaço para rótulos

    ax.yaxis.grid(True, linestyle="--", alpha=0.4)

    caminho = os.path.join(pasta_saida, "grafico_ic_gap.png")
    plt.savefig(caminho)
    plt.close()
    return caminho

# ─────────────────────────────────────────────────────────────────────────────
# Função principal — gera os três gráficos de uma vez
# ─────────────────────────────────────────────────────────────────────────────
def gerar_graficos(caminho = "resultado/resultados.dat",
                   pasta = "resultado"):
    """
    Lê o resultados.dat e salva os três gráficos na pasta_saida.

    Parâmetros
    ----------
    caminho:
        Caminho para o arquivo resultados.dat gerado por saida/resultados.py
    pasta : 
        Pasta onde os .png serão salvos (padrão: resultado/)
    """
    if not os.path.isfile(caminho):
        print(f"[graficos] Arquivo não encontrado: {caminho}")
        return

    if not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)

    df = carregar_resultados(caminho)

    if df.empty:
        print("[graficos] Arquivo de resultados está vazio.")
        return

    grafico_barras_runtime(df, pasta)
    grafico_boxplot_gap(df, pasta)
    grafico_ic_gap(df, pasta)

    print(" Todos os gráficos gerados com sucesso.")

# ─────────────────────────────────────────────────────────────────────────────
# Execução direta: python -m saida.graficos [caminho_dat]
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    arquivo = sys.argv[1] if len(sys.argv) > 1 else "resultado/resultados.dat"
    saida   = sys.argv[2] if len(sys.argv) > 2 else "resultado"
    gerar_graficos(arquivo, saida)