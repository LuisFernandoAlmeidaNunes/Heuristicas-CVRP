import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Entrada do connjunto de dados
df = pd.read_csv('dados_alunos.csv')
df 

# Selecao variaveis

x = df[['Horas_Estudo_Semana']]
y = df[['Nota_Matematica']]

# Graficos

plt.figure()
plt.scatter(x,y)
plt.xlabel("Nota_Matematica")
plt.title("Grafu=ico de Dispersao")
plt.show()

# calculoss r2

r2 = r2_score(y, y_pred)
print("\n Coeficiente de determiacao de r²:", r2)

plt.figure()
      
