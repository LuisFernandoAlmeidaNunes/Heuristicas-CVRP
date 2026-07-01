import os
import time
import csv
import pandas as pd


# Este módulo centraliza a lógica de execução, cronometragem e persistência de dados.
# Sua função é garantir que todas as heurísticas sejam testadas sob as mesmas
# condições e que seus resultados sejam registrados de forma padronizada.
#
# As principais responsabilidades deste arquivo incluem:
#
# 1. Controle de Execução: Gerencia o ciclo de vida da execução de uma heurística,
#    desde a medição precisa do tempo (utilizando perf_counter) até o cálculo
#    do Gap em relação ao melhor valor conhecido (BKS).
#
# 2. Cálculo de Gap e Penalidades: Garante que o Gap seja calculado sobre o custo
#    já penalizado, permitindo uma comparação justa entre métodos que respeitam
#    ou não o limite de veículos (k_alvo).
#
# 3. Persistência de Dados: Automatiza o salvamento dos resultados em formato .dat
#    tabulado, facilitando a leitura posterior por bibliotecas de análise de dados
#    como o Pandas. Também salva as rotas detalhadas em .txt quando não é benchmark.
#
# 4. Interface Visual: Integra-se ao módulo de gráficos para gerar automaticamente
#    os mapas de rotas (PNG) quando executado em modo individual, ou suprimir
#    essa geração durante o benchmark para otimizar a performance.

CAMINHO_ARQUIVO = "resultados/resultados.dat"
PASTA_PLOTS     = "resultados"

CABECALHO = ["INSTANCE", "METHOD", "OBJECTIVE", "RUNTIME", "GAP"]


def carregar_resultados(caminho_dat=CAMINHO_ARQUIVO):
    df = pd.read_csv(caminho_dat, sep="\t")
    df.columns = df.columns.str.strip()
    for col in ["OBJECTIVE", "RUNTIME", "GAP"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def salvar_resultado(instancia, metodo, objetivo, runtime, gap):
    """Append de uma linha no .dat (cria o arquivo + cabeçalho se não existir)."""
    os.makedirs(os.path.dirname(CAMINHO_ARQUIVO), exist_ok=True)
    arquivo_existe = os.path.isfile(CAMINHO_ARQUIVO)
    with open(CAMINHO_ARQUIVO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        if not arquivo_existe:
            writer.writerow(CABECALHO)
        writer.writerow([instancia, metodo,
                         f"{objetivo:.2f}", f"{runtime:.6f}", f"{gap:.4f}"])


def salvar_rotas(inst, rotas, heuristica_nome, custo, n_veiculos, runtime, gap, pasta):
    """
    Salva as rotas detalhadas em um arquivo .txt legível.

    Formato por rota:
        Rota 1 (5 municípios | carga: 87/240 | tempo: 312.4 min):
          Formiga_CD → Arcos → Pains → Iguatama → Lagoa_da_Prata → Formiga_CD

    O nome do município é recuperado do grafo via no.nome (se disponível)
    ou pelo ID numérico como fallback.
    """
    os.makedirs(pasta, exist_ok=True)
    metodo_clean = heuristica_nome.replace(" ", "_").replace("&", "e")
    caminho = os.path.join(pasta, f"{inst.nome}_{metodo_clean}_rotas.txt")

    grafo   = inst.grafo
    dep_id  = inst.id_deposito
    dep_no  = grafo.nos[dep_id]

    # Nome do depósito — usa atributo .nome se existir, senão ID
    dep_nome = getattr(dep_no, 'nome', str(dep_id))

    def nome_no(id_):
        no = grafo.nos[id_]
        return getattr(no, 'nome', str(id_))

    def custo_rota(rota):
        """Distância total da rota incluindo ida/volta ao depósito."""
        if not rota:
            return 0.0
        dist = grafo.dist(dep_id, rota[0])
        for i in range(len(rota) - 1):
            dist += grafo.dist(rota[i], rota[i + 1])
        dist += grafo.dist(rota[-1], dep_id)
        return dist

    def carga_rota(rota):
        return sum(grafo.nos[c].demanda for c in rota)

    st = getattr(inst, 'tempo_servico', 0.0)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"  ROTAS — {inst.nome}\n")
        f.write(f"  Método : {heuristica_nome}\n")
        f.write(f"  Custo  : {custo:.2f}\n")
        f.write(f"  GAP    : {gap:.4f}%\n")
        f.write(f"  Veículos utilizados : {n_veiculos}\n")
        f.write(f"  Tempo de execução   : {runtime:.2f}s\n")
        f.write("=" * 70 + "\n\n")

        for idx, rota in enumerate(rotas, start=1):
            if not rota:
                continue

            dist  = custo_rota(rota)
            carga = carga_rota(rota)
            tempo_total = dist + st * len(rota)
            sequencia   = [dep_nome] + [nome_no(c) for c in rota] + [dep_nome]

            f.write(f"Rota {idx:>3}  "
                    f"({len(rota)} municípios | "
                    f"carga: {carga}/{inst.capacidade} engradados | "
                    f"tempo: {tempo_total:.1f}/{getattr(inst, 'max_distancia', '∞')} min)\n")
            f.write("  " + " → ".join(sequencia) + "\n\n")

        f.write("=" * 70 + "\n")

    return caminho


def executar_e_salvar(heuristica, inst, melhor_conhecido, melhor_k=None, is_beenchmark=False):
    """
    Executa a heurística, mede o tempo e salva o resultado.
    Em modo não-benchmark, salva também o PNG do mapa e o .txt com as rotas.
    """
    inicio = time.perf_counter()
    rotas, custo, n_veiculos = heuristica.resolver(inst, k_alvo=melhor_k)
    fim     = time.perf_counter()
    runtime = fim - inicio

    # GAP sobre o custo já penalizado (comparável ao BKS)
    gap = max(0.0, (custo - melhor_conhecido) / melhor_conhecido * 100)

    salvar_resultado(inst.nome, heuristica.nome, custo, runtime, gap)

    from saida.graphics import plotar_rotas
    if not is_beenchmark:
        caminho_png   = plotar_rotas(inst, rotas, heuristica.nome, PASTA_PLOTS)
        caminho_rotas = salvar_rotas(inst, rotas, heuristica.nome,
                                     custo, n_veiculos, runtime, gap, PASTA_PLOTS)
        return {
            "heuristica": heuristica.nome,
            "custo":      custo,
            "veiculos":   n_veiculos,
            "runtime":    runtime,
            "gap":        gap,
            "png":        caminho_png,
            "rotas_txt":  caminho_rotas,
        }
    else:
        return {
            "heuristica": heuristica.nome,
            "custo":      custo,
            "veiculos":   n_veiculos,
            "runtime":    runtime,
            "gap":        gap,
        }


def executar_instancia(heuristicas, inst, melhor_conhecido, melhor_k, is_beenchmark=True):
    resultados = []
    for h in heuristicas:
        r = executar_e_salvar(h, inst, melhor_conhecido, melhor_k, is_beenchmark)
        resultados.append(r)
    return resultados