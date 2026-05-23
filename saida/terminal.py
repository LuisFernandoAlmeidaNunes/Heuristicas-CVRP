"""
saida/terminal.py

Utilitários para exibir resultados no terminal com cores ANSI.
Cada heurística tem uma cor fixa. Funciona no Windows (Win10+), Linux e Mac.
"""

import os
import sys
import itertools

# Ativa cores ANSI no Windows
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        os.system("")

# ─────────────────────────────────────────────────────────────────────────────
# Códigos ANSI
# ─────────────────────────────────────────────────────────────────────────────

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
PISCAR  = "\033[5m"
BRANCO  = "\033[97m"
CINZA   = "\033[90m"
VERDE   = "\033[38;5;118m"  # neon green
AMARELO = "\033[93m"
AZUL    = "\033[94m"
MAGENTA = "\033[95m"
CIANO   = "\033[96m"
VERMELHO= "\033[91m"

# ─────────────────────────────────────────────────────────────────────────────
# Larguras das colunas (sem códigos ANSI — esses não ocupam espaço visual)
# ─────────────────────────────────────────────────────────────────────────────

W_NOME    = 36   # nome da heurística
W_CUSTO   = 14   # custo total
W_VEIC    = 10   # número de veículos
W_GAP     = 10   # GAP %
W_TEMPO   =  9   # tempo de execução
W_TOTAL   = W_NOME + W_CUSTO + W_VEIC + W_GAP + W_TEMPO + 4  # ~83

# ─────────────────────────────────────────────────────────────────────────────
# Cor fixa por heurística
# ─────────────────────────────────────────────────────────────────────────────

_CORES = {
    "CW": CIANO,
    "NN": AMARELO,
    "SW": MAGENTA,
    "Mj": AZUL,
}

def cor_heuristica(nome: str) -> str:
    return _CORES.get(nome[:2].upper(), BRANCO)

# ─────────────────────────────────────────────────────────────────────────────
# Formatação de números
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_custo(valor: float) -> str:
    """Formata custo com separador de milhar e 2 casas: 12.847,40"""
    inteiro, decimal = f"{valor:.2f}".split(".")
    inteiro_fmt = f"{int(inteiro):,}".replace(",", ".")
    return f"{inteiro_fmt},{decimal}"

# ─────────────────────────────────────────────────────────────────────────────
# Linhas separadoras
# ─────────────────────────────────────────────────────────────────────────────

def _linha(char="─", cor=CINZA):
    print(f"{cor}{char * W_TOTAL}{RESET}")

def _linha_dupla():
    print(f"{CINZA}{'═' * W_TOTAL}{RESET}")

# ─────────────────────────────────────────────────────────────────────────────
# Componentes
# ─────────────────────────────────────────────────────────────────────────────

def cabecalho_sistema():
    _linha_dupla()
    print(f"{BOLD}{CIANO}{'CVRP SOLVER':^{W_TOTAL}}{RESET}")
    print(f"{DIM}{CINZA}{'Heurísticas Construtivas — 2026.1':^{W_TOTAL}}{RESET}")
    print(f"{DIM}{CINZA}{'Augusto · Luis · Maria · Raissa':^{W_TOTAL}}{RESET}")
    _linha_dupla()
    print()

def cabecalho_instancia(inst_info: dict, melhor: float):
    print()
    _linha_dupla()
    print(
        f"  {BOLD}{BRANCO}{inst_info['nome']}{RESET}  {DIM}{CINZA}│{RESET}  "
        f"{CINZA}Clientes:{RESET} {AMARELO}{inst_info['num_clientes']}{RESET}  "
        f"{CINZA}Capacidade:{RESET} {AMARELO}{inst_info['capacidade']}{RESET}  "
        f"{CINZA}Depósito:{RESET} {AMARELO}{inst_info['deposito']}{RESET}  "
        f"{CINZA}BKS:{RESET} {VERDE}{_fmt_custo(melhor)}{RESET}"
    )
    _linha()
    print(
        f"  {DIM}{CINZA}"
        f"{'Heurística':<{W_NOME}}"
        f"{'Custo':>{W_CUSTO}}"
        f"{'Veículos':>{W_VEIC}}"
        f"{'GAP (%)':>{W_GAP}}"
        f"{'Tempo':>{W_TEMPO}}"
        f"{'':>4}"
        f"{RESET}"
    )
    _linha()

def linha_resultado(resultado: dict):
    h    = resultado["heuristica"]
    cor  = cor_heuristica(h)
    gap  = resultado["gap"]
    custo_fmt = _fmt_custo(resultado["custo"])

    # Ícone e cor do GAP
    if gap < 20:
        icone   = f"{VERDE}●{RESET}"
        cor_gap = VERDE
    elif gap < 50:
        icone   = f"{AMARELO}●{RESET}"
        cor_gap = AMARELO
    else:
        icone   = f"{VERMELHO}●{RESET}"
        cor_gap = VERMELHO

    print(
        f"  {cor}{BOLD}{h:<{W_NOME}}{RESET}"
        f"{custo_fmt:>{W_CUSTO}}"
        f"{resultado['veiculos']:>{W_VEIC}}"
        f"  {cor_gap}{gap:>{W_GAP-2}.2f}%{RESET}"
        f"{resultado['runtime']:>{W_TEMPO}.3f}s"
        f"  {icone}"
    )

def rodape_instancia(resultados: list, melhor: float):
    _linha()
    melhor_r = min(resultados, key=lambda r: r["custo"])
    cor = cor_heuristica(melhor_r["heuristica"])

    print(
        f"  {DIM}{CINZA}{'Melhor conhecido':<{W_NOME}}{RESET}"
        f"{_fmt_custo(melhor):>{W_CUSTO}}"
    )
    print(
        f"  {cor}{BOLD}{'▶ Melhor heurística':<{W_NOME}}{RESET}"
        f"  {cor}{melhor_r['heuristica']}{RESET}"
        f"  {DIM}{CINZA}({melhor_r['gap']:.2f}% do ótimo){RESET}"
    )
    _linha()

def mensagem_sucesso(texto: str):
    print(f"  {VERDE}✓{RESET}  {texto}")

def mensagem_aviso(texto: str):
    print(f"  {AMARELO}⚠{RESET}  {texto}")

def mensagem_erro(texto: str):
    print(f"  {VERMELHO}{texto}{RESET}")

def mensagem_info(texto: str):
    print(f"  {CIANO}→{RESET}  {texto}")

def rodape_benchmark(arquivo: str):
    print()
    _linha_dupla()
    print(
        f"  {BOLD}{VERDE}Benchmark concluído!{RESET}  "
        f"{DIM}{CINZA}Resultados salvos em:{RESET} {AMARELO}{arquivo}{RESET}"
    )
    _linha_dupla()
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Spinner para busca local
# ─────────────────────────────────────────────────────────────────────────────

_SPINNER_FRAMES = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])

def spinner_busca_local(nome: str, iteracao: int, custo_atual: float, custo_inicial: float):
    frame   = next(_SPINNER_FRAMES)
    melhora = custo_inicial - custo_atual
    cor     = cor_heuristica(nome)
    sys.stdout.write(
        f"\r  {CIANO}{frame}{RESET} "
        f"{cor}{BOLD}{nome}{RESET} "
        f"{DIM}{CINZA}│{RESET} "
        f"iter {AMARELO}{iteracao:<4}{RESET} "
        f"{DIM}{CINZA}│{RESET} "
        f"custo {BRANCO}{_fmt_custo(custo_atual)}{RESET} "
        f"{DIM}{CINZA}│{RESET} "
        f"melhora {VERDE}▼ {_fmt_custo(melhora)}{RESET}   "
    )
    sys.stdout.flush()

def spinner_busca_local_fim(nome: str, custo_inicial: float, custo_final: float):
    melhora = custo_inicial - custo_final
    cor     = cor_heuristica(nome)
    sys.stdout.write(
        f"\r  {VERDE}✓{RESET} "
        f"{cor}{BOLD}{nome}{RESET} "
        f"{DIM}{CINZA}│{RESET} "
        f"{_fmt_custo(custo_inicial)} {CINZA}→{RESET} {VERDE}{_fmt_custo(custo_final)}{RESET} "
        f"{DIM}{CINZA}│{RESET} "
        f"melhora {VERDE}▼ {_fmt_custo(melhora)}{RESET}   \n"
    )
    sys.stdout.flush()