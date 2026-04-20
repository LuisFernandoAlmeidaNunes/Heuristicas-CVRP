# CVRP Solver - Heurísticas para o Problema de Roteamento de Veículos Capacitado

Este projeto implementa e compara quatro heurísticas clássicas para a resolução do **Problema de Roteamento de Veículos Capacitado (CVRP)**. O objetivo é analisar o desempenho de diferentes algoritmos construtivos em relação à qualidade da solução (Gap) e eficiência computacional (Runtime), validando os resultados através de testes estatísticos rigorosos.

## 🚀 Heurísticas Implementadas

O sistema conta com as seguintes estratégias de resolução:

* **CW (Clarke & Wright Savings):** Algoritmo paralelo baseado no conceito de economia de custo de oportunidade.
* **NN (Nearest Neighbor):** Heurística gulosa com estratégia de expansão bidirecional (Farthest Seed).
* **SW (Sweep):** Algoritmo geométrico de varredura angular (Cluster-first, Route-second).
* **MJ (Mole & Jameson):** Heurística de inserção sequencial baseada no critério de tensão (Strain).

## 📁 Estrutura do Projeto

* `core/`: Núcleo do sistema (Parser de instâncias TSPLIB e estrutura de Grafo vetorizada).
* `Heuristicas/`: Implementação detalhada de cada algoritmo.
* `Benchmark/`: Diretório contendo os arquivos `.vrp` das instâncias utilizadas.
* `Main.py`: Interface de linha de comando para execução individual de instâncias.
* `Benchmark.py`: Script para execução em lote e orquestração dos testes.
* `Statistics/`: Módulo de análise estatística (Testes de Friedman e Wilcoxon).
* `resultados/`: Gráficos gerados (Boxplots, Intervalos de Confiança) e logs de execução.

## 📊 Metodologia de Validação

Para garantir a validade científica das comparações, o projeto segue o protocolo de **Demšar (2006)**:
1.  **Execução Múltipla:** Cada instância é executada repetidas vezes para garantir a estabilidade estatística.
2.  **Teste de Friedman:** Teste global não-paramétrico para verificar se existe diferença significativa entre os algoritmos através de postos (ranks).
3.  **Teste de Wilcoxon (Post-hoc):** Comparação par a par com **Correção de Bonferroni** para identificar a hierarquia de dominância e significância entre os métodos.

## 💻 Como Executar

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Execução Individual (CLI)
```bash
python Main.py <arquivo.vrp> <saida.dat> <valor_bks> <SIGLA>
```
*Exemplo:* `python Main.py Benchmark/A-n80-k10.vrp resultados/resultados.dat 1763 CW`

### Execução do Benchmark Completo
Para rodar todas as instâncias e gerar os relatórios estatísticos e gráficos finais:
```bash
python Benchmark.py
```

## 🛠️ Tecnologias Utilizadas
* **NumPy:** Processamento vetorizado e broadcasting para cálculo de matrizes de distância.
* **Pandas:** Manipulação de dados e exportação de resultados.
* **SciPy:** Execução dos testes de hipótese estatísticos.
* **Matplotlib:** Geração de mapas de rotas e gráficos comparativos de desempenho.

## 📚 Referências

### Bases de Estudo e Implementação
* **VeRyPy:** Biblioteca de referência para heurísticas de roteamento. [Acesse aqui](https://github.com/yorak/VeRyPy/tree/master).
* **Statys:** Biblioteca de referência para implementação de testes de hipótese. [Acesse aqui](https://github.com/gugarosa/statys).
* **Literatura Base CVRP:** SOBREIRA, B. S. *Heurísticas para o problema de roteamento de veículos com restrições de tempo e capacidade*. UFMG. [Acesse aqui](https://repositorio.ufmg.br/server/api/core/bitstreams/fe7b2f7c-2dfc-47bf-a77c-b14436a80cd3/content).
* **Literatura Teste de Hipótese:** DEMŠAR, J. Statistical comparisons of classifiers over multiple data sets. *Journal of Machine Learning Research*, 2006. [Acesse aqui](https://www.jmlr.org/papers/volume7/demsar06a/demsar06a.pdf)


---
**Equipe:** Augusto, Luis, Maria e Raíssa.
*Trabalho de Heurísticas para o CVRP - 2026.1*