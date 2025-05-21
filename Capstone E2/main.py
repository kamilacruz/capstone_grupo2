# main.py
import pandas as pd
import matplotlib.pyplot as plt
from modelo import correr_modelo

if __name__ == "__main__":
    utilidades = []
    for iteracion in range(100):
        utilidad = correr_modelo()
        utilidades.append(utilidad)
    # Creación del df
    df_utilidad = pd.DataFrame(utilidades)
    print("Resumen de la utilidad:")
    print(df_utilidad.describe())
    plt.hist(utilidades, color = 'navy', ec = 'black')
    plt.xlabel('Suma de utilidades entre ambas tiendas')
    plt.ylabel('Frecuencia')
    plt.title('Utilidad final')
    plt.show()