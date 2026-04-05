
''' Heuristica de construção DSN (Distance Savings Nearest) 
Ideia geral:
    1. ordena clientes por distância do depósito (mais distante primeiro)
    2. começa cluster pelo mais distante = fartherest
    3. cresce o cluster pelo vizinho mais próximo
    4. quando capacidade estourar → fecha rota, começa nova
    5. calcula custo total
'''

def DSN(inst):

    # 1. Calculo da distancia euclidiana entre dois nós i e j  
    distancias_do_deposito = {}

    for id_no in inst.ids_clientes:
        # para cada id do cliente, id_no, guardo a distancia entre depo. e cliente
        distancias_do_deposito[id_no] = inst.dist(inst.id_deposito, id_no)

    # 2. Ordenar os clientes do decrescente pela distância do depósito
    clientes_desalocados = list(inst.ids_clientes)

    # Uso do Bubble Sort para ordenar os clientes por distância do depósito (do mais distante para o mais próximo)
    for i in range(len(clientes_desalocados)):
       for j in range(i + 1, len(clientes_desalocados)):
         if distancias_do_deposito[clientes_desalocados[i]] < distancias_do_deposito[clientes_desalocados[j]]:

            # se a dist do cliente i ate o deposito for menor que a do cliente j, troca de posição
            clientes_desalocados[i], clientes_desalocados[j] = clientes_desalocados[j], clientes_desalocados[i]

    # CLUSTERING - grupo de clientes que é recepcionado por um mesmo veiculo
    # 1 SET C = 1
    rotas = []
    C = 1

    while len(clientes_desalocados) > 0:

        # 2. cliente mais distante do deposito = fartherest
        fartherest = clientes_desalocados[0]
        cluster = [fartherest]
        carga = inst.demandas[fartherest]
        clientes_desalocados.remove(fartherest) # remove o cliente mais distante do deposito da lista de desalocados

        # 3. cresce o cluster pelo vizinho mais próximo dps de comecar uma rota
        while len(clientes_desalocados) > 0:

            melhor = None
            melhor_dist = float('inf')

            for id_no in clientes_desalocados:
                for id_cluster in cluster:
                    dist = inst.dist(id_no, id_cluster)
                    if dist < melhor_dist: # pega o mais proximo
                        melhor_dist = dist
                        melhor = id_no

            # 4. quando capacidade estourar → fecha rota, começa nova
            if carga + inst.demandas[melhor] <= inst.capacidade:
                cluster.append(melhor)
                carga += inst.demandas[melhor]
                clientes_desalocados.remove(melhor)

            else:
                break

        rotas.append(cluster)
        C += 1

    # 5. calcula custo total
    custo_total = 0
    for rota in rotas:
        custo_total += inst.dist(inst.id_deposito, rota[0]) # distancia do deposito ate o primeiro cliente da rota
        for i in range(len(rota) - 1):
            custo_total += inst.dist(rota[i], rota[i + 1]) # distancia entre os clientes da rota
        custo_total += inst.dist(rota[-1], inst.id_deposito) # distancia do ultimo cliente da rota ate o deposito

    return rotas, custo_total, C-1

