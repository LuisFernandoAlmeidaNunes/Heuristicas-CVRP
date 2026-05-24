import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from matplotlib import cm
import pandas as pd

from saida.execution import carregar_resultados

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def calcular_ic_bootstrap(valores, confianca=0.95, n_bootstrap=10000):
    """
    Calcula média e semilargura do IC por bootstrap.
    Não assume distribuição — coerente com testes não-paramétricos.

    Parâmetros
    ----------
    valores : array-like 1D
        Observações de uma única métrica/método.
    confianca : float
        Nível de confiança (padrão 0.95).
    n_bootstrap : int
        Número de reamostras.

    Retorna
    -------
    media : float
    erro  : float  (semilargura do IC, ou seja, media ± erro)
    """
    valores = np.asarray(valores, dtype=float)
    n = len(valores)
    if n <= 1:
        return float(np.mean(valores)), 0.0

    rng = np.random.default_rng(42)
    medias_boot = np.array([
        np.mean(valores[rng.integers(0, n, size=n)])
        for _ in range(n_bootstrap)
    ])
    alpha = (1 - confianca) / 2
    lower = np.percentile(medias_boot, alpha * 100)
    upper = np.percentile(medias_boot, (1 - alpha) * 100)
    return float(np.mean(valores)), float((upper - lower) / 2)


def plotar_rotas(inst, rotas, metodo: str, pasta_saida: str = "resultados"):
    """Gera um gráfico das rotas da solução."""
    os.makedirs(pasta_saida, exist_ok=True)

    grafo = inst.grafo
    dep_id = inst.id_deposito
    dep_no = grafo.nos[dep_id]

    n_clientes = sum(len(r) for r in rotas)
    resolucao = 200 if n_clientes < 500 else 100

    fig, ax = plt.subplots(figsize=(12, 10))
    colormap = cm.get_cmap('tab20')
    n_rotas = len(rotas)

    for idx, rota in enumerate(rotas):
        if not rota:
            continue
        cor = colormap(idx % 20) if n_rotas <= 20 else cm.jet(idx / n_rotas)
        ids_seq = [dep_id] + rota + [dep_id]
        coords = np.array([(grafo.nos[i].x, grafo.nos[i].y) for i in ids_seq])
        xs, ys = coords[:, 0], coords[:, 1]
        ax.plot(xs, ys, color=cor, linewidth=1.5, alpha=0.6, zorder=1)
        ax.scatter(xs[1:-1], ys[1:-1], color=cor, s=40,
                   edgecolors='black', linewidths=0.3, zorder=2)
        if n_clientes < 150:
            for c_id in rota:
                ax.text(grafo.nos[c_id].x, grafo.nos[c_id].y, str(c_id),
                        fontsize=7, ha='center', va='bottom', alpha=0.8)

    ax.scatter(dep_no.x, dep_no.y, color="black", s=300,
               marker="*", zorder=4, label=f"Depósito (ID {dep_id})")
    ax.set_title(f"Solução CVRP: {inst.nome}\nMétodo: {metodo} | Veículos: {len(rotas)}",
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Coordenada X")
    ax.set_ylabel("Coordenada Y")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)

    metodo_clean = metodo.replace(" ", "_").replace("&", "e")
    caminho = os.path.join(pasta_saida, f"{inst.nome}_{metodo_clean}.png")
    plt.tight_layout()
    plt.savefig(caminho, dpi=resolucao, bbox_inches='tight')
    plt.close(fig)
    return caminho


def gerar_graficos(caminho_dat, pasta_saida):
    df = carregar_resultados(caminho_dat)
    if df.empty:
        return

    df_medio = df.groupby(["INSTANCE", "METHOD"]).mean().reset_index()
    metodos = sorted(df_medio["METHOD"].unique())

    # ── Gráfico 1: Runtime com IC bootstrap ───────────────────────────────
    INSTANCIAS_PEQUENAS = {"A-n80-k10", "CMT10", "E-n101-k14", "F-n135-k7",
                           "F-n72-k4", "Golden_18", "M-n151-k12", "tai150b"}
    INSTANCIAS_GRANDES = set(df["INSTANCE"].unique()) - INSTANCIAS_PEQUENAS

    for grupo, label in [(INSTANCIAS_PEQUENAS, "pequenas"), (INSTANCIAS_GRANDES, "grandes")]:
        df_grupo = df[df["INSTANCE"].isin(grupo)]
        if df_grupo.empty:
            continue

        instancias = sorted(df_grupo["INSTANCE"].unique())
        x = np.arange(len(instancias))
        largura = 0.8 / len(metodos)
        cores = plt.cm.tab10(np.linspace(0, 0.8, len(metodos)))

        fig, ax = plt.subplots(figsize=(13, 6))

        for i, metodo in enumerate(metodos):
            medias, erros = [], []
            for inst in instancias:
                vals = df_grupo.loc[
                    (df_grupo["INSTANCE"] == inst) & (df_grupo["METHOD"] == metodo),
                    "RUNTIME"
                ].values
                if len(vals) == 0:
                    medias.append(0.0)
                    erros.append(0.0)
                else:
                    m, e = calcular_ic_bootstrap(vals)
                    medias.append(m)
                    erros.append(e)

            offset = (i - len(metodos) / 2 + 0.5) * largura
            ax.bar(x + offset, medias, largura, yerr=erros, capsize=5,
                   label=metodo, color=cores[i], edgecolor='black', alpha=0.85)

        ax.set_title(f"Tempo Médio de Execução — Instâncias {label.capitalize()}\n"
                     f"Barras de erro = IC 95% bootstrap")
        ax.set_ylabel("Segundos")
        ax.set_xticks(x)
        ax.set_xticklabels(instancias, rotation=45, ha="right")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(pasta_saida, f"grafico_barras_runtime_{label}.png"), dpi=150)
        plt.close()

    # ── Gráfico 2: Boxplot do GAP + média com IC bootstrap ────────────────
    fig, ax = plt.subplots(figsize=(11, 6))

    dados_box = [df_medio.loc[df_medio["METHOD"] == m, "GAP"].values for m in metodos]
    bp = ax.boxplot(dados_box, patch_artist=True, positions=range(len(metodos)),
                    widths=0.4, showfliers=True)

    cores = plt.cm.viridis(np.linspace(0.2, 0.8, len(metodos)))
    for patch, cor in zip(bp['boxes'], cores):
        patch.set_facecolor(cor)
        patch.set_alpha(0.5)

    # Sobrepõe média ± IC bootstrap como diamante preto
    for i, m in enumerate(metodos):
        vals = df_medio.loc[df_medio["METHOD"] == m, "GAP"].values
        media, erro = calcular_ic_bootstrap(vals)
        ax.errorbar(i, media, yerr=erro, fmt='D', color='black',
                    markersize=6, capsize=6, linewidth=1.5,
                    label="Média ± IC 95% bootstrap" if i == 0 else "")

    ax.set_title("Dispersão do Gap Médio entre Instâncias\n"
                 "◆ = Média ± IC 95% bootstrap")
    ax.set_ylabel("Gap médio por instância (%)")
    ax.set_xticks(range(len(metodos)))
    ax.set_xticklabels(metodos, rotation=15, ha="right")
    ax.legend(fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(pasta_saida, "grafico_boxplot_gap.png"), dpi=150)
    plt.close()

    # ── Tabela comparativa ────────────────────────────────────────────────
    df_medio.to_csv(os.path.join(pasta_saida, "tabela_comparativa_media.csv"), index=False)

    resultados_ic = []
    for m in metodos:
        vals = df_medio.loc[df_medio["METHOD"] == m, "GAP"].values
        media, erro = calcular_ic_bootstrap(vals)
        resultados_ic.append({"Metodo": m, "Media_Gap": media, "Erro_IC": erro})

    pd.DataFrame(resultados_ic).to_csv(os.path.join(pasta_saida, "estatisticas_ic.csv"), index=False)

    # ── Tabela estatística (pivot INSTANCE × METHOD → GAP médio) ─────────
    tabela_gaps = df.groupby(["INSTANCE", "METHOD"])["GAP"].mean().unstack("METHOD")
    tabela_gaps.to_csv(os.path.join(pasta_saida, "tabela_estatistica_gaps.csv"))


def processar_resultados_finais(caminho_dat, pasta_saida):
    """Alias chamado pelo Benchmark — gera gráficos + tabela de gaps para análise estatística."""
    gerar_graficos(caminho_dat, pasta_saida)


def plotar_comparativo(inst, rotas_melhor, rotas_pior, metodo_melhor, metodo_pior, pasta_saida):
    """Plota lado a lado a melhor e pior rota da mesma instância."""
    fig, axes = plt.subplots(1, 2, figsize=(20, 9))

    for ax, rotas, metodo in zip(axes, [rotas_melhor, rotas_pior], [metodo_melhor, metodo_pior]):
        grafo    = inst.grafo
        dep_id   = inst.id_deposito
        dep_no   = grafo.nos[dep_id]
        n_rotas  = len(rotas)
        colormap = cm.get_cmap('tab20')

        for idx, rota in enumerate(rotas):
            if not rota:
                continue
            cor     = colormap(idx % 20) if n_rotas <= 20 else cm.jet(idx / n_rotas)
            ids_seq = [dep_id] + rota + [dep_id]
            coords  = np.array([(grafo.nos[i].x, grafo.nos[i].y) for i in ids_seq])
            ax.plot(coords[:, 0], coords[:, 1], color=cor, linewidth=1.5, alpha=0.6)
            ax.scatter(coords[1:-1, 0], coords[1:-1, 1], color=cor, s=40,
                       edgecolors='black', linewidths=0.3, zorder=2)

        ax.scatter(dep_no.x, dep_no.y, color="black", s=300, marker="*",
                   zorder=4, label="Depósito")
        ax.set_title(f"{metodo}\nVeículos: {len(rotas)}", fontsize=13, fontweight='bold')
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, linestyle=':', alpha=0.4)
        ax.legend(fontsize=9)

    fig.suptitle(f"Comparativo de Rotas — {inst.nome}", fontsize=15, fontweight='bold')
    plt.tight_layout()
    caminho = os.path.join(pasta_saida, f"{inst.nome}_comparativo.png")
    plt.savefig(caminho, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return caminho