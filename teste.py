import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Seus dados exatos de p-values (Wilcoxon)
data = {
    'CW': {'CW': 1.0, 'MJ': 0.000122, 'NN': 0.000122, 'SW': 0.000061},
    'MJ': {'CW': 0.000122, 'MJ': 1.0, 'NN': 0.000122, 'SW': 0.000061},
    'NN': {'CW': 0.000122, 'MJ': 0.000122, 'NN': 1.0, 'SW': 0.000061},
    'SW': {'CW': 0.000061, 'MJ': 0.000061, 'NN': 0.000061, 'SW': 1.0}
}

df_p_values = pd.DataFrame(data)


def gerar_heatmap_pvalues(df):
    plt.figure(figsize=(10, 8))

    # Criamos uma máscara para esconder a diagonal (comparações iguais)
    mask = np.eye(df.shape[0], dtype=bool)

    # Plot do Heatmap
    # Usamos uma escala logarítmica ou cores binárias para destacar p < 0.05
    ax = sns.heatmap(df, annot=True, fmt=".6f", cmap="YlGnBu_r",
                     mask=mask, cbar_kws={'label': 'p-value'})

    plt.title('Matriz de Significância (Teste de Wilcoxon)\nStatus: Todos Diferentes (p < 0.05)',
              fontsize=14, pad=20)
    plt.ylabel('Heurística A')
    plt.xlabel('Heurística B')

    # Adicionando nota de rodapé
    plt.figtext(0.5, 0, "Nota: Todos os pares apresentam diferença estatística significativa.",
                ha="center", fontsize=10, bbox={"facecolor": "orange", "alpha": 0.2, "pad": 5})

    plt.tight_layout()
    plt.savefig('resultados/heatmap_estatistico.png')
    plt.show()


if __name__ == "__main__":
    # Ajustando estilo para ficar profissional
    sns.set_theme(style="white")
    gerar_heatmap_pvalues(df_p_values)