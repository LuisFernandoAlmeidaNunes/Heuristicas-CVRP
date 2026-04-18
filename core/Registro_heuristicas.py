from Heuristicas.clarke_wright        import ClarkeWright
from Heuristicas.nearest_neighbor     import NearestNeighbor
from Heuristicas.sweep                import Sweep
from Heuristicas.sequential_insertion import MoleJameson

HEURISTICAS = {
    "CW": ClarkeWright(),
    "NN": NearestNeighbor(),
    "SW": Sweep(),
    "Mj": MoleJameson(),
}

MELHORES = {
    "A-n32-k5":       784.0,
    "A-n33-k5":       661.0,
    "A-n80-k10":      1763.0,
    "F-n72-k4":       237.0,
    "E-n101-k14":     1067.0,
    "F-n135-k7":      1162.0,
    "M-n151-k12":     1015.0,
    "Golden_18":      995.13,
    "CMT10":          1395.85,
    "tai150b":        2727.03,
    "Golden_3":       10997.80,
    "Loggi-n601-k42": 347046.0,
}