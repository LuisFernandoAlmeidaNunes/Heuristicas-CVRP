from math import comb
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from instancesConfig import ARQUIVO_DAT, HEURISTICAS
from metodos.friedman import friedman
from metodos.wilcoxon import wilcoxon
from utils import load_data
from saida.terminal import (
    BOLD, CINZA, CIANO, VERDE, AMARELO, VERMELHO, RESET, DIM, AZUL, MAGENTA
)

def testaHipotese():
    data = load_data(ARQUIVO_DAT)
    metodos = list(HEURISTICAS.keys())

    # ── Friedman ──────────────────────────────────────────────────────────
    friedman_result = friedman(data)

    print(f"\n{BOLD}{CIANO}TESTE DE FRIEDMAN (Iman-Davenport){RESET}")
    print(f"{CINZA}{'-' * 46}{RESET}")
    print(f"  {'Estatística':<28} {BOLD}{'Valor':>15}{RESET}")
    print(f"{CINZA}{'-' * 46}{RESET}")
    print(f"  {'Friedman':<28} {AMARELO}{friedman_result['friedman'][0]:>15.4f}{RESET}")
    print(f"  {'Iman-Davenport':<28} {AMARELO}{friedman_result['iman'][0]:>15.4f}{RESET}")
    print(f"  {'P-value':<28} {AMARELO}{friedman_result['p_value']:>15.2e}{RESET}")
    rejeitou = friedman_result['p_value'] < 0.05
    cor_h0 = VERDE if rejeitou else VERMELHO
    print(f"  {'Rejeita H0 (α=0.05)':<28} {cor_h0}{str(rejeitou):>15}{RESET}")
    print(f"{CINZA}{'-' * 46}{RESET}")

    # ── Wilcoxon ──────────────────────────────────────────────────────────
    wilcoxon_result = None
    if rejeitou:
        bonferroni = 0.05 / comb(len(HEURISTICAS), 2)

        print(f"\n{BOLD}{CIANO}TESTE DE WILCOXON (par a par — Bonferroni){RESET}")
        print(f"{DIM}{VERMELHO}  Alpha corrigido: {bonferroni:.4f}{RESET}")
        print(f"{CINZA}{'-' * 90}{RESET}")
        print(f"  {BOLD}{'Par':<45} {'W':>8} {'P-value':>10} {'Significativo':>8} {'Melhor':>8}{RESET}")
        print(f"{CINZA}{'-' * 90}{RESET}")

        wilcoxon_result = wilcoxon(data, alpha=bonferroni)

        CORES_PARES = [CIANO, AMARELO, VERDE, MAGENTA, AZUL, VERMELHO]

        for idx, ((i, j), res) in enumerate(wilcoxon_result.items()):
            m1 = metodos[i]
            m2 = metodos[j]
            significativo = res['p'] < bonferroni
            melhor = m1 if res['i_melhor'] > res['j_melhor'] else m2
            cor_par = CORES_PARES[idx % len(CORES_PARES)]
            cor_sig = VERDE if significativo else VERMELHO

            par_fmt    = f"{f'{m1} vs {m2}':<45}"
            w_fmt      = f"{res['W']:>8.2f}"
            p_fmt      = f"{res['p']:>10.4f}"
            sig_fmt    = f"{'Sim':>12}" if significativo else f"{'Não':>12}"
            melhor_fmt = f"{melhor:>8}"

            print(f"  {cor_par}{par_fmt}{RESET} {w_fmt} {p_fmt} {cor_sig}{sig_fmt}{RESET} {cor_par}{melhor_fmt}{RESET}")
            
    return {
        "friedman": friedman_result,
        "wilcoxon": wilcoxon_result,
    }

testaHipotese()