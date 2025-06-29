import pandas as pd
import matplotlib.pyplot as plt
import time
from modelo_2 import correr_modelo

if __name__ == "__main__":
    iteraciones = 50

    # Definir los incrementos que se aplicarán a gamma (no valores absolutos)
    deltas_gamma = [0.0, 10.0, 20.0, 50.0, 100.0]  # Puedes ajustar según magnitud esperada

    resultados_escenarios = []

    for delta in deltas_gamma:
        nombre_escenario = f"DeltaGamma_{int(delta)}"
        print(f"\nCorriendo escenario: {nombre_escenario}")

        tiempos, utilidades, insatisfechas, proporciones = [], [], [], []

        for iteracion in range(iteraciones):
            inicio = time.time()
            result = correr_modelo(delta_gamma=delta)
            if result is None or result[0] is None:
                continue

            obj, demanda_total, insatis_total, prop_insatis = result[:4]

            tiempos.append(time.time() - inicio)
            utilidades.append(obj)
            insatisfechas.append(insatis_total)
            proporciones.append(prop_insatis)

        if not utilidades:
            print(f"\n⚠️ No se obtuvieron soluciones para delta_gamma = {delta}")
            continue

        resultados_escenarios.append({
            "Escenario": nombre_escenario,
            "Delta_gamma": delta,
            "Utilidad_media": sum(utilidades) / len(utilidades),
            "Tiempo_medio": sum(tiempos) / len(tiempos),
            "DemandaInsatisfecha_media": sum(insatisfechas) / len(insatisfechas),
            "ProporcionInsatisfecha_media": sum(proporciones) / len(proporciones)
        })

        print(f"\nResumen {nombre_escenario}")
        print(f"Utilidad: {pd.DataFrame(utilidades).describe()}")
        print(f"Tiempo: {pd.DataFrame(tiempos).describe()}")
        print(f"Demanda Insatisfecha: {pd.DataFrame(insatisfechas).describe()}")
        print(f"Proporción Insatisfecha: {pd.DataFrame(proporciones).describe()}")

        for data, titulo, xlabel, color in [
            (utilidades, "Utilidad final ($)", "Utilidad", "navy"),
            (tiempos, "Tiempo de ejecución (s)", "Tiempo", "slategrey"),
            (insatisfechas, "Demanda insatisfecha total", "Unidades", "turquoise"),
            (proporciones, "Proporción de demanda insatisfecha", "Proporción", "gold")
        ]:
            plt.hist(data, color=color, edgecolor='black')
            plt.title(f"{titulo} - {nombre_escenario}")
            plt.xlabel(xlabel)
            plt.ylabel("Frecuencia")
            plt.tight_layout()
            # plt.show()  # descomenta si quieres ver gráficos al momento

    df_resumen = pd.DataFrame(resultados_escenarios)
    df_resumen.to_csv("resumen_analisis_delta_gamma.csv", index=False)
    print("\nResultados guardados en resumen_analisis_gamma.csv")
    print(df_resumen)
