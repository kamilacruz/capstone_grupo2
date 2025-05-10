import matplotlib.pyplot as plt
import pandas as pd
import registros
import parametros as prm

tiempo_total = 0
utilidades = []
insatisfechas = []

iteraciones = 100
for iteracion in range(iteraciones):
    # Generamos la iteración
    registro = registros.generar_iteracion()
    # Anotamos los registros
    tiempo_total += registro[0]
    utilidad = registro[1][0] + registro[2][0]
    insatisfecha = registro[1][1] + registro[2][1]
    # Se almacenan en el global
    utilidades.append(utilidad)
    insatisfechas.append(insatisfecha)

print(f'Número de iteraciones: {iteraciones}')
print(f'Tiempo total de ejecución: {round(tiempo_total, 2)} segundos')
print(f'Simulaciones desde la semana {prm.T_INICIO} hasta la semana {prm.T_FINAL}')
print()

# Creamos Data Frame de las iteraciones para ver el resumen de los resultados
df_utilidad = pd.DataFrame(utilidades)
df_demanda_insatisfecha = pd.DataFrame(insatisfechas)
print("Resumen de la utilidad:")
print(df_utilidad.describe())
print()
print("Resumen de la demanda insatisfecha:")
print(df_demanda_insatisfecha.describe())

# Se crea histograma que muestra las utilidades obtenidas
plt.hist(utilidades, color = 'grey', ec = 'black')
plt.xlabel('Suma de utilidades entre ambas tiendas')
plt.ylabel('Frecuencia')
plt.title('Utilidad final')
plt.show()

# Se crea histograma que muestra las demandas insatisfechas obtenidas
plt.hist(insatisfechas, color = 'grey', ec = 'black')
plt.xlabel('Suma de demanda insatisfecha acumulada entre ambas tiendas')
plt.ylabel('Frecuencia')
plt.title('Demanda insatisfecha acumulada')
plt.show()