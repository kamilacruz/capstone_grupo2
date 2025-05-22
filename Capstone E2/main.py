# main.py
import time
import pandas as pd
import matplotlib.pyplot as plt
from modelo import correr_modelo

if __name__ == "__main__":
    tiempo = []
    utilidades = []
    iteraciones = 500
    for iteracion in range(iteraciones):
        inicio = time.time()
        utilidad = correr_modelo()
        utilidades.append(utilidad)
        fin = time.time()
        tiempo.append(round(fin - inicio, 2))

    # Creación del df utilidad
    df_utilidad = pd.DataFrame(utilidades)
    # Se imprime el resumen de la utilidad
    print()
    print("Resumen de la utilidad:")
    print(df_utilidad.describe())
    # Creación del df tiempo
    df_tiempo = pd.DataFrame(tiempo)
    # Se imprime un resumen del tiempo
    print()
    print("Resumen del tiempo:")
    print(df_tiempo.describe())
    print("Tiempo total de la simulación:", df_tiempo.sum())
    
    # Se grafica la utilidad
    plt.hist(utilidades, color = 'navy', ec = 'black')
    plt.xlabel('Suma de utilidades entre ambas tiendas')
    plt.ylabel('Frecuencia')
    plt.title('Utilidad final')
    plt.show()

    # Se grafica el tiempo
    plt.hist(utilidades, color = 'gold', ec = 'black')
    plt.xlabel('Tiempo de ejecución por iteración')
    plt.ylabel('Frecuencia')
    plt.title('Segundos')
    plt.show()