''' Classe Instancia: representa uma instância do CVRP, com dados lidos de um arquivo .vrp
 Ideia Geral:
    - Lê o arquivo .vrp e armazena as informações relevantes (nome, capacidade, coordenadas, demandas, etc)
    - Lê o arquivo de arestas pré-calculadas (gerado por Arestas.py) e armazena as distâncias entre os nós em uma matriz
    - Fornece métodos para acessar essas informações, como a distância entre dois nós ou a demanda de um cliente
    - Facilita o uso dessas informações por heurísticas e algoritmos de busca, evitando a
      necessidade de ler o arquivo ou calcular distâncias repetidamente
    '''
from Arestas import No 
class Instancia:

    def __init__(self):
        self.nome = ""
        self.capacidade = 0
        self.id_deposito = None
        self.coordenadas = {}   # {id: (x, y)}
        self.demandas = {}      # {id: demanda}
        self.ids_clientes = []  # ids sem depósito
        self.matriz = {}        # {(i,j): distancia}

    # Lê o arq. de distancia entre os nós  e guarda dentro da classe
    @classmethod
    def ler_arquivo(cls, caminho:str) -> 'Instancia':
        inst = cls()
        modo = None

        # Lê linha por linha, identificando tipos de infos
        with open(caminho, 'r') as file:
            for linha in file:
                linha = linha.strip()

                # ignora linhas vazias
                if not linha:
                    continue

                if linha.startswith("NAME"):
                    inst.nome = linha.split(":")[1].strip()
                
                elif linha.startswith("CAPACITY"):
                    inst.capacidade = int(linha.split(":")[1].strip())
                
                elif linha == "NODE_COORD_SECTION":
                    modo = 'coord'
                
                elif linha == "DEMAND_SECTION":
                    modo = 'demanda'
                
                elif linha == "DEPOT_SECTION":
                    modo = 'deposito'
                
                elif linha == "EOF":
                    break
                
                elif modo == 'coord':
                    partes = linha.split()
                    id_no = int(partes[0])
                    # Coordenadas do nó pode estar em decimal
                    inst.coordenadas[id_no] = (
                        float(partes[1]), 
                        float(partes[2])
                    ) # eg: {1: (82.0, 76.0)}
                
                elif modo == 'demanda':
                    # Demanda qnt inteira
                    partes = linha.split()
                    inst.demandas[int(partes[0])] = int(partes[1]) # eg: {2: 19}
                
                elif modo == 'deposito':
                    if linha != '-1':
                        inst.id_deposito = int(linha) # Um unico deposito

        # ids dos clientes (todos clientes exceto o depósito)
        inst.ids_clientes = [
            id_no for id_no in inst.coordenadas
            if id_no != inst.id_deposito
        ]

        # Lre arestas pré-calculadas e guarda na matriz de distancias da instancia
        inst.ler_arestas(caminho + "-arestas")

        return inst
    
    def ler_arestas(self, caminho_arestas:str):
        # Lê o arq -arestas gerado lá em Arestas.py e guarda num dicionario de distancias
        with open(caminho_arestas, 'r') as file:
            for linha in file:
                linha = linha.strip()
                
                # pula cabeçalho da seção NODE_LENGHT
                if not linha or linha == 'NODE_LENGHT':
                    continue

                partes = linha.split()
                i = int(partes[0])
                j = int(partes[1])
                dist = float(partes[2])

                # guarda a distancia entre os nós i e j, e também j e i (simetria)
                self.matriz[(i, j)] = dist
                self.matriz[(j, i)] = dist
    
    def dist(self, i:int, j:int) -> float:
        # Retorna a distancia entre nós i e j
        return self.matriz[(i, j)]
    
    # Instancia(A-n32-k5, n=31, Q=100)
    def __repr__(self): 
        return f"Instancia({self.nome}, n={len(self.ids_clientes)}, Q={self.capacidade})"