import os
from pathlib import Path as FilePath
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from matplotlib import cm
import pandas as pd

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

# ── bootstrap ────────────────────────────────────────────────────────────────
 
def _bootstrap_media(dados: np.ndarray,
                     n_boot: int,
                     nivel: float,
                     seed: int) -> tuple[float, float, float]:
    """
    Retorna (media, ic_inferior, ic_superior) via bootstrap percentil.
 
    Parâmetros
    ----------
    dados   : array 1-D de valores observados
    n_boot  : número de re-amostras bootstrap
    nivel   : nível de confiança (ex.: 0.95 → IC 95%)
    seed    : semente do gerador aleatório
 
    Retorna
    -------
    media        : média da amostra original
    ic_inf       : limite inferior do IC bootstrap
    ic_sup       : limite superior do IC bootstrap
    """
    rng = np.random.default_rng(seed)
    n = len(dados)
 
    medias_boot = np.empty(n_boot)
    for i in range(n_boot):
        amostra = rng.choice(dados, size=n, replace=True)
        medias_boot[i] = amostra.mean()
 
    alfa = 1.0 - nivel
    ic_inf = np.percentile(medias_boot, 100 * alfa / 2)
    ic_sup = np.percentile(medias_boot, 100 * (1 - alfa / 2))
    media  = dados.mean()
 
    return media, ic_inf, ic_sup
 
PALETA = ["#2196F3", "#F44336", "#4CAF50", "#FF9800",
         "#9C27B0", "#00BCD4", "#795548", "#607D8B"]

# ── função principal ──────────────────────────────────────────────────────────
 
def gerar_grafico_bootstrap(arquivo_dat: str, arquivo_saida: str ) -> None:
    """
    Lê um arquivo .dat, calcula o bootstrap da `metrica` por método e
    salva o gráfico em `arquivo_saida`.
 
    Parâmetros
    ----------
    arquivo_dat   : caminho do arquivo .dat (separado por tab)
    arquivo_saida : caminho da imagem de saída (.png, .pdf, .svg …)
    metrica       : coluna numérica a analisar  (padrão: "GAP")
    n_bootstrap   : número de re-amostras bootstrap (padrão: 10 000)
    nivel_ic      : nível de confiança do IC      (padrão: 0.95)
    seed          : semente aleatória              (padrão: 42)
    figsize       : tamanho da figura em polegadas (padrão: (12, 6))
    dpi           : resolução da imagem            (padrão: 150)
 
    Exemplo
    -------
    >>> gerar_grafico_bootstrap("resultados.dat", "bootstrap.png", metrica="OBJECTIVE")
    """
 
    # ── leitura e validação ──────────────────────────────────────────────────
    arquivo_dat    = FilePath(arquivo_dat)
    arquivo_saida  = FilePath(arquivo_saida)
    metrica = "GAP"
    n_bootstrap = 10_000
    nivel_ic = 0.95
    seed = 42
    figsize = (12, 6)
    dpi = 150
 
    if not arquivo_dat.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_dat}")
 
    df = pd.read_csv(arquivo_dat, sep="\t")
 
    colunas_obrigatorias = {"METHOD", metrica}
    faltando = colunas_obrigatorias - set(df.columns)
    if faltando:
        raise ValueError(
            f"Coluna(s) ausente(s) no arquivo: {faltando}\n"
            f"Colunas disponíveis: {list(df.columns)}"
        )
 
    metodos  = df["METHOD"].unique()
    n_metodos = len(metodos)
 
    # ── cálculo do bootstrap por método ─────────────────────────────────────
    resultados = []
    for metodo in metodos:
        dados = df.loc[df["METHOD"] == metodo, metrica].dropna().to_numpy()
        if len(dados) == 0:
            continue
        media, ic_inf, ic_sup = _bootstrap_media(dados, n_bootstrap, nivel_ic, seed)
        resultados.append(
            dict(metodo=metodo, media=media, ic_inf=ic_inf, ic_sup=ic_sup, n=len(dados))
        )
 
    res_df = pd.DataFrame(resultados).sort_values("media")
 
    # ── figura ───────────────────────────────────────────────────────────────
    fig, (ax_bar, ax_dist) = plt.subplots(
        1, 2,
        figsize=figsize,
        gridspec_kw={"width_ratios": [1.2, 1]},
    )
    fig.suptitle(
        f"Análise Bootstrap — {metrica}  "
        f"(IC {int(nivel_ic * 100)}%,  {n_bootstrap:,} re-amostras)",
        fontsize=14, fontweight="bold", y=1.02,
    )
 
    cores = {m: PALETA[i % len(PALETA)] for i, m in enumerate(res_df["metodo"])}
 
    # ── painel esquerdo: barras com IC ───────────────────────────────────────
    x = np.arange(len(res_df))
    for i, row in res_df.reset_index(drop=True).iterrows():
        cor = cores[row["metodo"]]
        ax_bar.bar(i, row["media"], color=cor, alpha=0.82, zorder=2)
        ax_bar.errorbar(
            i, row["media"],
            yerr=[[row["media"] - row["ic_inf"]], [row["ic_sup"] - row["media"]]],
            fmt="none", color="black", capsize=6, linewidth=1.8, zorder=3,
        )
        ax_bar.text(
            i, row["ic_sup"] + (res_df["ic_sup"].max() * 0.01),
            f"{row['media']:.2f}",
            ha="center", va="bottom", fontsize=8.5, fontweight="bold",
        )
 
    nomes_curtos = [
        m.split("(")[0].strip() if "(" in m else m for m in res_df["metodo"]
    ]
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(nomes_curtos, rotation=15, ha="right", fontsize=9)
    ax_bar.set_ylabel(metrica, fontsize=11)
    ax_bar.set_title("Média com IC Bootstrap por Método", fontsize=11)
    ax_bar.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax_bar.set_axisbelow(True)
 
    # ── painel direito: distribuição bootstrap ───────────────────────────────
    rng = np.random.default_rng(seed)
    for _, row in res_df.iterrows():
        dados  = df.loc[df["METHOD"] == row["metodo"], metrica].dropna().to_numpy()
        n      = len(dados)
        medias = np.array([
            rng.choice(dados, size=n, replace=True).mean()
            for _ in range(n_bootstrap)
        ])
        cor = cores[row["metodo"]]
        nome_curto = row["metodo"].split("(")[0].strip() if "(" in row["metodo"] else row["metodo"]
        ax_dist.hist(
            medias, bins=60, color=cor, alpha=0.55,
            density=True, label=nome_curto,
        )
        ax_dist.axvline(row["ic_inf"], color=cor, linestyle=":", linewidth=1.2)
        ax_dist.axvline(row["ic_sup"], color=cor, linestyle=":", linewidth=1.2)
 
    ax_dist.set_xlabel(f"Média Bootstrap de {metrica}", fontsize=11)
    ax_dist.set_ylabel("Densidade", fontsize=11)
    ax_dist.set_title("Distribuição das Médias Bootstrap", fontsize=11)
    ax_dist.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)
    ax_dist.set_axisbelow(True)
    ax_dist.legend(fontsize=8, framealpha=0.7)
 
    # ── rodapé com tabela de resultados ─────────────────────────────────────
    linhas_rodape = []
    for _, row in res_df.iterrows():
        nome_curto = row["metodo"].split("(")[0].strip() if "(" in row["metodo"] else row["metodo"]
        linhas_rodape.append(
            f"{nome_curto}: média={row['media']:.3f}  "
            f"IC=[{row['ic_inf']:.3f}, {row['ic_sup']:.3f}]  n={row['n']}"
        )
    fig.text(
        0.5, -0.04, "\n".join(linhas_rodape),
        ha="center", va="top", fontsize=7.5,
        fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5f5f5", edgecolor="#cccccc"),
    )
 
    plt.tight_layout()
    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(arquivo_saida, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

def gerar_tabelas_report(df_medio, pasta_saida):
    """
    Função dedicada exclusivamente ao processamento e exportação de dados.
    """
    # 1. Tabela de Benchmark (Objetivo, BKS, Gap)
    # Calculamos a BKS aproximada: Objetivo / (1 + Gap/100)
    df_medio['BKS'] = df_medio.apply(
        lambda row: round(row['OBJECTIVE'] / (1 + row['GAP'] / 100), 2), axis=1
    )

    tabela_bench = df_medio[['INSTANCE', 'METHOD', 'OBJECTIVE', 'BKS', 'GAP']]
    tabela_bench.to_csv(os.path.join(pasta_saida, "tabela_benchmark_completa.csv"), index=False)

    # 2. Tabela para o Teste de Friedman (Formato Largo)
    df_pivot_gap = df_medio.pivot(index="INSTANCE", columns="METHOD", values="GAP")
    df_pivot_gap.to_csv(os.path.join(pasta_saida, "tabela_estatistica_gaps.csv"))

    print(f"Tabelas CSV geradas em: {pasta_saida}")
    return df_pivot_gap


def gerar_graficos_analise(df_medio, pasta_saida):
    """
    Função dedicada à geração de visualizações.
    """
    # ── Gráfico 1: Runtime separado em pequenas e grandes ──────────────────
    INSTANCIAS_PEQUENAS = {"A-n80-k10", "CMT10", "E-n101-k14", "F-n135-k7",
                           "F-n72-k4", "Golden_18", "M-n151-k12", "tai150b"}

    for grupo, label in [(INSTANCIAS_PEQUENAS, "pequenas"), (None, "grandes")]:
        if label == "pequenas":
            df_grupo = df_medio[df_medio["INSTANCE"].isin(grupo)]
        else:
            df_grupo = df_medio[~df_medio["INSTANCE"].isin(INSTANCIAS_PEQUENAS)]

        if df_grupo.empty: continue

        tabela_time = df_grupo.pivot(index="INSTANCE", columns="METHOD", values="RUNTIME")
        fig, ax = plt.subplots(figsize=(12, 6))
        tabela_time.plot(kind="bar", ax=ax, edgecolor="black")
        ax.set_title(f"Tempo Médio de Execução — Instâncias {label.capitalize()}")
        ax.set_ylabel("Segundos")
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(pasta_saida, f"grafico_barras_runtime_{label}.png"))
        plt.close()

    # ── Gráfico 2: Boxplot ─────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))
    df_medio.boxplot(column="GAP", by="METHOD", ax=ax)
    ax.set_title("Dispersão do Gap Médio entre Instâncias")
    plt.suptitle("")
    ax.set_ylabel("Gap médio por instância (%)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_boxplot_gap.png"))
    plt.close()

    # ── Gráfico 3: IC 95% ──────────────────────────────────────────────────
    grafico_ic_gap(df_medio, pasta_saida)
    print(f"Gráficos salvos em: {pasta_saida}")


def processar_resultados_finais(caminho_dat, pasta_saida):
    """
    Função principal que coordena a carga, as tabelas e os gráficos.
    """
    df = carregar_resultados(caminho_dat)
    if df.empty:
        print("Aviso: O arquivo de resultados está vazio.")
        return

    # Consolidar médias (unidade de análise por instância para o teste de Friedman)
    df_medio = df.groupby(["INSTANCE", "METHOD"]).mean(numeric_only=True).reset_index()

    # 1. Gerar Tabelas
    gerar_tabelas_report(df_medio, pasta_saida)

    # 2. Gerar Gráficos
    gerar_graficos_analise(df_medio, pasta_saida)

    # 3. Grafico Bootstrap
    gerar_grafico_bootstrap(caminho_dat, os.path.join(pasta_saida, "grafico_bootstrap_gap.png"))