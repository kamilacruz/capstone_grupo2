import pandas as pd
import matplotlib.pyplot as plt
import time
from modelo_2 import correr_modelo

if __name__ == "__main__":
    iteraciones = 50

    # Valores de incremento sobre los coeficientes B2
    deltas_b2 = [0.0, 1e-8, 5e-8, 1e-7, -1e-8, -5e-8]
    resultados_escenarios = []

    for delta in deltas_b2:
        nombre_escenario = f"DeltaB2_{delta:.0e}"
        print(f"\nCorriendo escenario: {nombre_escenario}")

        tiempos, utilidades, insatisfechas, proporciones = [], [], [], []

        for iteracion in range(iteraciones):
            inicio = time.time()
            result = correr_modelo(delta_B2=delta)
            if result is None or result[0] is None:
                continue

            obj, demanda_total, insatis_total, prop_insatis = result[:4]

            tiempos.append(time.time() - inicio)
            utilidades.append(obj)
            insatisfechas.append(insatis_total)
            proporciones.append(prop_insatis)

        if not utilidades:
            print(f"\n⚠️ No se obtuvieron soluciones para delta_B2 = {delta}")
            continue

        resultados_escenarios.append({
            "Escenario": nombre_escenario,
            "Delta_B2": delta,
            "Utilidad_media": sum(utilidades) / len(utilidades),
            "Tiempo_medio": sum(tiempos) / len(tiempos),
            "DemandaInsatisfecha_media": sum(insatisfechas) / len(insatisfechas),
            "ProporcionInsatisfecha_media": sum(proporciones) / len(proporciones)
        })

        print(f"\nResumen {nombre_escenario}")
        print(f"Utilidad: {pd.DataFrame(utilidades).describe()}")
        print(f"Tiempo: {pd.DataFrame(tiempos).describe()}")
        print(f"Demanda Insatisfecha: {pd.DataFrame(insatisfechas).describe()}")
        print(f"Proporci\u00f3n Insatisfecha: {pd.DataFrame(proporciones).describe()}")

        for data, titulo, xlabel, color in [
            (utilidades, "Utilidad final ($)", "Utilidad", "navy"),
            (tiempos, "Tiempo de ejecuci\u00f3n (s)", "Tiempo", "slategrey"),
            (insatisfechas, "Demanda insatisfecha total", "Unidades", "turquoise"),
            (proporciones, "Proporci\u00f3n de demanda insatisfecha", "Proporci\u00f3n", "gold")
        ]:
            plt.hist(data, color=color, edgecolor='black')
            plt.title(f"{titulo} - {nombre_escenario}")
            plt.xlabel(xlabel)
            plt.ylabel("Frecuencia")
            plt.tight_layout()
            # plt.show()

    df_resumen = pd.DataFrame(resultados_escenarios)
    df_resumen.to_csv("resumen_analisis_delta_B2.csv", index=False)
    print("\nResultados guardados en resumen_analisis_delta_B2.csv")
    print(df_resumen)
