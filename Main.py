"""
Main.py — CVRP Solver
Trabalho de Heurísticas para o CVRP - 2026.1
Alunos: Augusto, Luis, Maria e Raíssa
"""
import sys
from core.Instancia_cvrp import InstanciaCvrp
from saida.execution import executar_e_salvar
from saida.terminal import (
    BOLD, CINZA, CIANO, DIM, RESET,
    cabecalho_instancia, linha_resultado, rodape_instancia,
    mensagem_sucesso, mensagem_info, mensagem_aviso, mensagem_erro
)
from instancesConfig import INSTANCIAS, HEURISTICAS, BUSCALOCAL


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_config_instancia(nome: str):
    """Retorna (melhor_conhecido, melhor_k) do config, ou (None, None) se não achar."""
    for inst_nome, melhor_conhecido, melhor_k in INSTANCIAS:
        if inst_nome == nome:
            return melhor_conhecido, melhor_k
    return None, None


def linha(char="─", n=60):
    print(f"{CINZA}{char * n}{RESET}")


def titulo(texto):
    print()
    print(f"{BOLD}{CIANO}  {texto}{RESET}")
    print(f"{DIM}{CINZA}{'─' * (len(texto) + 4)}{RESET}")


def exibir_resultado(r, inst, melhor):
    inst_info = {
        'nome':         inst.nome,
        'num_clientes': len(inst.ids_clientes),
        'capacidade':   inst.capacidade,
        'deposito':     inst.id_deposito,
    }
    print()
    cabecalho_instancia(inst_info, melhor)
    linha_resultado(r)
    # rodape_instancia([r], melhor)
    mensagem_info(f"Plot salvo: {r['png']}")


# ─────────────────────────────────────────────────────────────────────────────
# Modo CLI
# ─────────────────────────────────────────────────────────────────────────────

def modo_cli(args):
    if len(args) != 4:
        mensagem_erro("Uso: python Main.py <arquivo.vrp> <saida.dat> <melhor_conhecido> <SIGLA>")
        mensagem_info(f"Heurísticas disponíveis: {list(HEURISTICAS.keys())}")
        sys.exit(1)

    caminho_vrp, arquivo_saida, melhor_str, sigla = args
    sigla = sigla.upper()

    heuristica = resolver_sigla(sigla)

    try:
        melhor = float(melhor_str)
    except ValueError:
        mensagem_erro(f"Melhor valor conhecido inválido: '{melhor_str}'")
        sys.exit(1)

    mensagem_info(f"Lendo instância: {caminho_vrp}")
    inst = InstanciaCvrp.ler_arquivo(caminho_vrp)
    mensagem_info(f"  → {inst}")

    # Busca melhor_k no config pelo nome da instância
    _, melhor_k = get_config_instancia(inst.nome)
    if melhor_k is None:
        mensagem_aviso(f"'{inst.nome}' não encontrado no config — penalidade de veículos desativada.")

    heuristica = HEURISTICAS[sigla]
    mensagem_info(f"Executando: {heuristica.nome}  (k_alvo={melhor_k})")

    resultado = executar_e_salvar(
        heuristica=heuristica,
        inst=inst,
        melhor_conhecido=melhor,
        melhor_k=melhor_k,
        is_beenchmark= False
    )

    titulo("RESULTADO")
    exibir_resultado(resultado, inst, melhor)
    mensagem_sucesso(f"Resultados salvos em: {arquivo_saida}")

 #────────────────────────────────────────────────────────────────────────────
# Modo Benchmark (gera .dat para análise estatística posterior)
#────────────────────────────────────────────────────────────────────────────
def resolver_sigla(sigla:str):
    sigla = sigla.upper()

    if sigla in HEURISTICAS:
        return HEURISTICAS[sigla]
    
    partes = sigla.split("-")
    if len(partes) == 3 and partes[0] == "LS":
        _, sigla_construtivo, sigla_busca = partes

        if sigla_construtivo not in HEURISTICAS:
            mensagem_erro(f"Construtivo '{sigla_construtivo}' não reconhecido.")
            mensagem_info(f"Disponíveis: {list(HEURISTICAS.keys())}")
            sys.exit(1)

        if sigla_busca not in BUSCALOCAL:
            mensagem_erro(f"Busca Local '{sigla_busca}' não reconhecida.")
            mensagem_info(f"Disponíveis: {list(BUSCALOCAL.keys())}")
            sys.exit(1)
        construtivo = HEURISTICAS[sigla_construtivo]
        classe_busca = BUSCALOCAL[sigla_busca]
        return classe_busca(construtivo)
    
    mensagem_erro(f"Sigla '{sigla}' não reconhecida.")
    sys.exit(1)
# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def print_usage():
    mensagem_info("Uso: python Main.py <arquivo.vrp> <saida.dat> <melhor_conhecido> <SIGLA>")
    mensagem_info(f"Heurísticas disponíveis: {list(HEURISTICAS.keys())}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        mensagem_erro("Nenhum argumento fornecido.")
        print_usage()
        sys.exit(1)

    modo_cli(args)

    #existe arquivo de config com os valores de BKS e K esperado de todas as instâncias já (InstancesConfig.py)