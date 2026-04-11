"""
saida/resultados.py

Responsável por:
  - Salvar resultados no arquivo ASCII/CSV (formato tabular exigido pelo enunciado)
  - Gerar plot .png das rotas para cada execução
  - Exibir resultados coloridos no terminal (via saida.terminal)
"""

import os
import time
import csv
import matplotlib
matplotlib.use("Agg")  # sem janela gráfica
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from saida.terminal import (
    cabecalho_instancia, linha_resultado, rodape_instancia,
    mensagem_sucesso, mensagem_info
)

CABECALHO = ["INSTANCE", "METHOD", "OBJECTIVE", "RUNTIME", "GAP"]

# ─────────────────────────────────────────────────────────────────────────────
# Arquivo ASCII / CSV
# ─────────────────────────────────────────────────────────────────────────────

def salvar_resultado(caminho_arquivo: str,
                     instancia: str,
                     metodo: str,
                     objetivo: float,
                     runtime: float,
                     gap: float):
    """
    Adiciona uma linha de resultado ao arquivo ASCII tabular.
    Cria o arquivo (com cabeçalho) se ainda não existir.
    """
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

    arquivo_existe = os.path.isfile(caminho_arquivo)

    with open(caminho_arquivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")

        if not arquivo_existe:
            writer.writerow(CABECALHO)

        writer.writerow([
            instancia,
            metodo,
            f"{objetivo:.2f}",
            f"{runtime:.4f}",
            f"{gap:.2f}"
        ])


# ─────────────────────────────────────────────────────────────────────────────
# Plot PNG das rotas
# ─────────────────────────────────────────────────────────────────────────────

def plotar_rotas(inst, rotas, metodo: str, pasta_saida: str = "resultado"):
    """
    Gera e salva um scatterplot com as rotas da solução.
    O arquivo é salvo como: <pasta_saida>/<nome_instancia>_<metodo>.png
    """
    os.makedirs(pasta_saida, exist_ok=True)

    grafo = inst.grafo
    deposito_id = inst.id_deposito
    dep = grafo.nos[deposito_id]

    fig, ax = plt.subplots(figsize=(10, 8))

    cores = cm.tab20.colors
    n_cores = len(cores)

    for idx, rota in enumerate(rotas):
        cor = cores[idx % n_cores]

        nos_seq = [deposito_id] + rota + [deposito_id]
        xs = [grafo.nos[n].x for n in nos_seq]
        ys = [grafo.nos[n].y for n in nos_seq]

        ax.plot(xs, ys, color=cor, linewidth=1.2, zorder=1)

        for cliente_id in rota:
            no = grafo.nos[cliente_id]
            ax.scatter(no.x, no.y, color=cor, s=30, zorder=2)

    ax.scatter(dep.x, dep.y, color="black", s=120,
               marker="*", zorder=3, label="Depósito")

    ax.set_title(f"{inst.nome} — {metodo}  |  {len(rotas)} veículos")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc="best", fontsize=8)
    ax.set_aspect("equal", adjustable="datalim")

    nome_arquivo = f"{inst.nome}_{metodo}.png"
    caminho = os.path.join(pasta_saida, nome_arquivo)
    plt.tight_layout()
    plt.savefig(caminho, dpi=150)
    plt.close(fig)

    return caminho


# ─────────────────────────────────────────────────────────────────────────────
# Execução individual
# ─────────────────────────────────────────────────────────────────────────────

def executar_e_salvar(heuristica,
                      inst,
                      melhor_conhecido: float,
                      arquivo_resultado: str = "resultado/resultados.dat",
                      pasta_plots: str = "resultado"):
    """
    Executa a heurística, mede o tempo, calcula o gap e salva saídas.
    Retorna dicionário com os resultados.
    """
    inicio = time.perf_counter()
    rotas, custo, n_veiculos = heuristica.resolver(inst)
    fim = time.perf_counter()
    runtime = fim - inicio

    gap = 100.0 * abs(custo - melhor_conhecido) / melhor_conhecido

    salvar_resultado(
        caminho_arquivo=arquivo_resultado,
        instancia=inst.nome,
        metodo=heuristica.nome,
        objetivo=custo,
        runtime=runtime,
        gap=gap
    )

    caminho_png = plotar_rotas(inst, rotas, heuristica.nome, pasta_plots)

    return {
        "instancia":  inst.nome,
        "heuristica": heuristica.nome,
        "rotas":      rotas,
        "custo":      custo,
        "veiculos":   n_veiculos,
        "runtime":    runtime,
        "gap":        gap,
        "png":        caminho_png,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Execução em bloco: todas as heurísticas numa instância, com saída formatada
# ─────────────────────────────────────────────────────────────────────────────

def executar_instancia(heuristicas: list,
                       inst,
                       melhor_conhecido: float,
                       arquivo_resultado: str = "resultado/resultados.dat",
                       pasta_plots: str = "resultado"):
    """
    Executa todas as heurísticas em uma instância e exibe tabela colorida.
    Ideal para usar no benchmark e no testeInstancia.
    """
    info_inst = {
        'nome': inst.nome,
        'num_clientes': len(inst.ids_clientes),
        'capacidade': inst.capacidade,
        'deposito': inst.id_deposito,
        'melhor_conhecido': melhor_conhecido #bks
    }
    cabecalho_instancia(info_inst, melhor_conhecido)

    resultados = []
    for h in heuristicas:
        r = executar_e_salvar(h, inst, melhor_conhecido, arquivo_resultado, pasta_plots)
        # add veiculos no retorno
        r["veiculos"] = len(r["rotas"])
        resultados.append(r)

    for r in resultados:
        linha_resultado(r)
    rodape_instancia(resultados, melhor_conhecido)
    mensagem_info(f"Plot salvo em: {pasta_plots}/")

    return resultados

#TODO: os dados no arquivo dat devem ser sobescritos a cada vez que rodar o algoritmo. Do jeito que está, está salvando com os resultados anteriores de todas as execuções