import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import scipy.stats as stats
from saida.execution import carregar_resultados



def plotar_rotas(inst, rotas, metodo: str, pasta_saida: str = "resultados"):
    """
    Gera um gráfico das rotas da solução.
    """
    os.makedirs(pasta_saida, exist_ok=True)

    grafo = inst.grafo
    dep_id = inst.id_deposito
    dep_no = grafo.nos[dep_id]

    # Ajuste dinâmico de DPI e tamanho baseado no número de clientes
    n_clientes = sum(len(r) for r in rotas)
    resolucao = 200 if n_clientes < 500 else 100  # Menor DPI para arquivos gigantes

    fig, ax = plt.subplots(figsize=(12, 10))

    # Paleta de cores escalável
    colormap = cm.get_cmap('tab20')
    n_rotas = len(rotas)

    for idx, rota in enumerate(rotas):
        if not rota: continue

        # Define a cor (cicla tab20 ou usa gradiente se houver muitas rotas)
        cor = colormap(idx % 20) if n_rotas <= 20 else cm.jet(idx / n_rotas)

        # 1. Preparar coordenadas (Vetorizado para performance)
        ids_seq = [dep_id] + rota + [dep_id]
        coords = np.array([(grafo.nos[i].x, grafo.nos[i].y) for i in ids_seq])
        xs, ys = coords[:, 0], coords[:, 1]

        # 2. Plotar as linhas da rota
        ax.plot(xs, ys, color=cor, linewidth=1.5, alpha=0.6, zorder=1)

        # 3. Plotar os clientes da rota (Scatter único por rota para ganhar tempo)
        ax.scatter(xs[1:-1], ys[1:-1], color=cor, s=40,
                   edgecolors='black', linewidths=0.3, zorder=2)

        # 4. Adicionar IDs apenas se for legível (ex: menos de 150 clientes)
        if n_clientes < 150:
            for c_id in rota:
                ax.text(grafo.nos[c_id].x, grafo.nos[c_id].y, str(c_id),
                        fontsize=7, ha='center', va='bottom', alpha=0.8)

    # 5. Destaque do Depósito (Símbolo de estrela maior)
    ax.scatter(dep_no.x, dep_no.y, color="black", s=300,
               marker="*", zorder=4, label=f"Depósito (ID {dep_id})")

    # Estilização Técnica
    ax.set_title(f"Solução CVRP: {inst.nome}\nMétodo: {metodo} | Veículos: {len(rotas)}",
                 fontsize=14, fontweight='bold', pad=15)

    ax.set_xlabel("Coordenada X")
    ax.set_ylabel("Coordenada Y")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect("equal", adjustable="datalim")

    # Legenda fora do gráfico para não tampar rotas
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)

    # Nome do arquivo sanitizado
    metodo_clean = metodo.replace(" ", "_").replace("&", "e")
    nome_arquivo = f"{inst.nome}_{metodo_clean}.png"
    caminho = os.path.join(pasta_saida, nome_arquivo)

    plt.tight_layout()
    plt.savefig(caminho, dpi=resolucao, bbox_inches='tight')
    plt.close(fig)

    return caminho

def grafico_ic_gap(df, pasta_saida):
    """
    Gera o gráfico de IC 95% com rótulos numéricos sobre as barras.
    """
    plt.figure(figsize=(10, 6))

    # Agrupamento e estatísticas
    stats_gap = df.groupby("METHOD")["GAP"].agg(['mean', 'std', 'count'])

    medias = stats_gap['mean']
    erros = []

    for i in stats_gap.index:
        m, s, c = stats_gap.loc[i, 'mean'], stats_gap.loc[i, 'std'], stats_gap.loc[i, 'count']
        # t-Student para 95%
        margem = stats.t.ppf(0.975, c - 1) * (s / np.sqrt(c)) if c > 1 else 0
        erros.append(margem)

    # Plotagem
    cores = ['#2E8B57', '#FF6347', '#4682B4', '#9932CC']
    bars = plt.bar(stats_gap.index, medias, yerr=erros, capsize=7,
                   color=cores, edgecolor='black', alpha=0.8)

    # --- ADICIONANDO OS NÚMEROS (DATA LABELS) ---
    for bar, m, e in zip(bars, medias, erros):
        height = bar.get_height()
        # Adiciona texto: "Média % ± Erro"
        plt.text(bar.get_x() + bar.get_width() / 2., height + e + 0.1,
                 f'{m:.2f}%\n±{e:.2f}',
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')

    plt.title("Gap Médio com Intervalo de Confiança (95%)", fontsize=13, fontweight='bold')
    plt.ylabel("Gap (%)")
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    # Ajuste de margem superior para o texto não cortar
    plt.ylim(0, max(medias + erros) * 1.2)

    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_ic_gap.png"))
    plt.close()

def gerar_graficos(caminho_dat, pasta_saida):
    df = carregar_resultados(caminho_dat)
    if df.empty: return

    # Colapsa as 30 runs → 1 valor médio por (instância, heurística)
    df_medio = df.groupby(["INSTANCE", "METHOD"]).mean().reset_index()
    # n=15 por heurística — unidade amostral para boxplot e IC

    # Gráfico 1: Runtime
    fig, ax = plt.subplots(figsize=(12, 6))
    tabela_time = df_medio.pivot(index="INSTANCE", columns="METHOD", values="RUNTIME")
    tabela_time.plot(kind="bar", ax=ax, edgecolor="black")
    ax.set_title("Tempo Médio de Execução (N=30 runs)")
    ax.set_ylabel("Segundos")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_barras_runtime.png"))
    plt.close()   # ← obrigatório

    # Gráfico 2: Boxplot — usa df_medio (n=15 por heurística)
    fig, ax = plt.subplots(figsize=(10, 6))
    df_medio.boxplot(column="GAP", by="METHOD", ax=ax)
    ax.set_title("Dispersão do Gap Médio entre Instâncias")
    plt.suptitle("")
    ax.set_ylabel("Gap médio por instância (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_boxplot_gap.png"))
    plt.close()   # ← obrigatório

    # Gráfico 3: IC 95%
    grafico_ic_gap(df_medio, pasta_saida)

    df_medio.to_csv(os.path.join(pasta_saida, "tabela_comparativa_media.csv"), index=False)

    # 4. Tabela Comparativa Final (Média)
    df_medio.to_csv(os.path.join(pasta_saida, "tabela_comparativa_media.csv"), index=False)

