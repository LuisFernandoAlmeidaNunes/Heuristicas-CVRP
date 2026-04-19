from Heuristicas.clarke_wright import ClarkeWright
from Heuristicas.nearest_neighbor import NearestNeighbor
from Heuristicas.sweep import Sweep
from Heuristicas.sequential_insertion import MoleJameson

# nome do arquivo de resultados
ARQUIVO_DAT = "resultados/resultados.dat"

# Set de instancias e seus melhores valores para funcao obj (KBS) e numero de veiculos(k)
# INSTANCIAS{ (nome, melhor_conhecido, melhor_k) }
INSTANCIAS = [
    ("A-n80-k10",       1763.00,    10),
    ("F-n72-k4",        237.00,     4),
    ("E-n101-k14",      1071.00,    14), 
    ("M-n151-k12",      1015.00,    12),
    ("Golden_18",       995.13,     27),
    ("CMT10",           1395.85,    18),
    ("tai150b",         2727.03,    14),
    ("tai385",          24366.41,   46),
    ("Golden_3",        10997.80,   9),
    ("Li_21",           16212.83,   10),
    ("X-n502-k39",      69226.00,   39),
    ("Loggi-n601-k42",  347046.00,  42),
    ("XL-n1701-k562",   521136.00,  562),
    ("XL-n2541-k121",   146390.00,  121),
]

HEURISTICAS = {
    "CW": ClarkeWright(),
    "NN": NearestNeighbor(),
    "SW": Sweep(),
    "ML": MoleJameson(),
}

