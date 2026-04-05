# Este arquivo tem a função de ler a instancia e pre-calcular as arestas, ou seja, as distancias entre os nos,
# e salvar em um arquivo de texto de nome "NOME-INSTANCIA-arestas" para evitar que metodos de busca tenham que 
# calcular a distancia entre os nos a cada iteracao.

import math
class No:

    def __init__(self, x, y):
        self.x = x
        self.y = y

# formula de distancia euclidiana
def calc_comprimento(X1, Y1, X2, Y2):
    return math.sqrt((X2 - X1) ** 2 + (Y2 - Y1) ** 2)

# entrada de leitura do arquivo, onde é lido as coordenadas dos nos e calculada a distancia entre eles, e salva em um arquivo de texto
def read_file(Path):
    nos = {}
    with open(Path, 'r') as input_file:
        with open(Path + "-arestas", 'w') as output_file:
            reading = False
            for line in input_file:
                line = line.strip()
                if line == "NODE_COORD_SECTION":
                    reading = True
                    continue
                if line == "DEMAND_SECTION":
                    break

                if reading:
                    info = line.split()
                    id_no = int(info[0])
                    x = float(info[1])
                    y = float(info[2])
                    nos[id_no] = No(x, y)
            output_file.write(f"NODE_LENGHT\n")
            ids = list(nos.keys())
            for i in range(len(nos)):
                for j in range(i + 1, len(nos)):
                    no1 = nos[ids[i]]
                    no2 = nos[ids[j]]
                    comprimento = calc_comprimento(no1.x, no1.y, no2.x, no2.y)
                    output_file.write(f"{ids[i]} {ids[j]} {comprimento:.2f}\n")

read_file("Benchmark/A-n32-k5.vrp")