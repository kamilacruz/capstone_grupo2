# main.py
import time
import pandas as pd
import matplotlib.pyplot as plt
from modelo import correr_modelo

if __name__ == "__main__":
    tiempo = []
    utilidades = []
    insatisfechas = []
    proporciones = []
    iteraciones = 500
    for iteracion in range(iteraciones):
        inicio = time.time()
        valores = correr_modelo()
        utilidades.append(valores[0])
        insatisfechas.append(valores[2])
        proporciones.append(valores[3])
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

    # Creación del df de demanda insatisfecha
    df_insatisfecha = pd.DataFrame(insatisfechas)
    # Se imprime el resumen de la demanda insatisfecha acumulada en el periodo
    print()
    print("Resumen demanda insatisfecha:")
    print(df_insatisfecha.describe())

    # Creación del df de proporción de incumplimiento de demanda
    df_proporcion = pd.DataFrame(proporciones)
    # Se imprime el resumen de las proporciones de incumplimiento de demanda en el periodo
    print()
    print("Resumen de la proporción de inclumpliento de demanda:")
    print(df_proporcion.describe())
    
    # Se grafica la utilidad
    plt.hist(utilidades, color = 'navy', ec = 'black')
    plt.xlabel('Suma de utilidades entre ambas tiendas')
    plt.ylabel('Frecuencia')
    plt.title('Utilidad final ($)')
    plt.autoscale()
    plt.show()

    # Se grafica el tiempo
    plt.hist(tiempo, color = 'slategrey', ec = 'black')
    plt.xlabel('Tiempo de ejecución por iteración')
    plt.ylabel('Frecuencia')
    plt.title('Segundos (s)')
    plt.autoscale()
    plt.show()

    # Se grafica la demanda insatisfecha total
    plt.hist(insatisfechas, color = 'turquoise', ec = 'black')
    plt.xlabel('Demanda insatisfehca en el periodo')
    plt.ylabel('Frecuencia')
    plt.title('Unidades de demanda insatisfecha del periodo (u)')
    plt.autoscale()
    plt.show()

    # Se grafica la proporción de incumplimiento de demanda del periodo
    # Se grafica la utilidad
    plt.hist(proporciones, color = 'gold', ec = 'black')
    plt.xlabel('Proporción de incumplimiento de demanda en el periodo')
    plt.ylabel('Frecuencia')
    plt.title('Proporción de incumplimiento de la demanda en el periodo')
    plt.autoscale()
    plt.show()

