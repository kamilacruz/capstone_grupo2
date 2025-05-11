import matplotlib.pyplot as plt
import pandas as pd
import registros
import parametros as prm

tiempo_total = 0
utilidades = []
insatisfechas = []
demandas = []
proporciones_instatisfecha_demanda = []

iteraciones = 500
for iteracion in range(iteraciones):
    # Generamos la iteración
    registro = registros.generar_iteracion()
    # Anotamos los registros
    tiempo_total += registro[0]
    utilidad = registro[1][0] + registro[2][0]
    insatisfecha = registro[1][1] + registro[2][1]
    demanda = registro[1][2] + registro[2][2]
    proporcion_instatisfecha_demanda = round(insatisfecha / demanda, 2)
    # Se almacenan en el global
    utilidades.append(utilidad)
    insatisfechas.append(insatisfecha)
    demandas.append(insatisfecha)
    proporciones_instatisfecha_demanda.append(proporcion_instatisfecha_demanda)

print(f'Número de iteraciones: {iteraciones}')
print(f'Tiempo total de ejecución: {round(tiempo_total, 2)} segundos')
print(f'Simulaciones desde la semana {prm.T_INICIO} hasta la semana {prm.T_FINAL}')
print()

# Creamos Data Frame de las iteraciones para ver el resumen de los resultados
df_utilidad = pd.DataFrame(utilidades)
df_demanda_insatisfecha = pd.DataFrame(insatisfechas)
df_proporcion_insatisfecha_demanda = pd.DataFrame(proporciones_instatisfecha_demanda)
print("Resumen de la utilidad:")
print(df_utilidad.describe())
print()
print("Resumen de la demanda insatisfecha:")
print(df_demanda_insatisfecha.describe())
print()
print("Resumen de la proporción de demanda insatisfecha respecto a la demanda total:")
print(df_proporcion_insatisfecha_demanda.describe())
print()

# Se crea histograma que muestra las utilidades obtenidas
plt.hist(utilidades, color = 'navy', ec = 'black')
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

# Se crea histograma que muestra las proporciones de demanda insatisfecha versus demanda real
plt.hist(proporciones_instatisfecha_demanda, color = 'goldenrod', ec = 'black')
plt.xlabel('Proporción de demanda insatisfecha acumulada entre ambas tiendas respecto a la demanda total')
plt.ylabel('Frecuencia')
plt.title('Proporción')
plt.show()