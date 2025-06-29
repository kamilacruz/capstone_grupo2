# main_sensibilidad_2.py
import pandas as pd
import matplotlib.pyplot as plt
import time
from sensibilidad_2 import correr_escenario

if __name__ == "__main__":
    tiempo = []
    utilidades = []
    insatisfechas = []
    proporciones = []
    iteraciones = 50

    ## acá hay que inventar los escenarios de sensibilidad que queremoss
    ##ejemplo cambio costo inventario y otro de cambio costo pedido
    escenarios = [
        ("Normal", {}, None),

        ("Costo_Inventario_mas20", {"C_INV_cambio": 1.20}, None), ## ptobar 
        ("Costo_Inventario_menos20",  {"C_INV_cambio": 0.80}, None),

        ("Costo_Inventario_mas10", {"C_INV_cambio": 1.10}, None), ## ptobar 
        ("Costo_Inventario_menos10",  {"C_INV_cambio": 0.90}, None),

        ("Costo_Inventario_mas05", {"C_INV_cambio": 1.05}, None), ## ptobar 
        ("Costo_Inventario_menos05",  {"C_INV_cambio": 0.95}, None),


        ("CostoFijo_Pedido_mas20", {"C_FIJO_cambio": 1.2}, None),
        ("CostoFijo_Pedido_menos20", {"C_FIJO_cambio": 0.8}, None),

        ("CostoFijo_Pedido_mas10", {"C_FIJO_cambio": 1.1}, None),
        ("CostoFijo_Pedido_menos10", {"C_FIJO_cambio": 0.9}, None),

        ("CostoFijo_Pedido_mas05", {"C_FIJO_cambio": 1.05}, None),
        ("CostoFijo_Pedido_menos05", {"C_FIJO_cambio": 0.95}, None),


        ("CostoProducto_mas015", {"C_PROD_cambio": 1.015}, None), ##no puede ser más que         self.PROPORCION_MAXIMA = 1.051
        ("CostoProducto_menos20", {"C_PROD_cambio": 0.8}, None),

        ("CostoProducto_menos10", {"C_PROD_cambio": 0.9}, None),

        ("CostoProducto_menos05", {"C_PROD_cambio": 0.95}, None),


        ("CostoDemandaIns_mas20", {"C_DEM_INS_cambio": 1.2}, None),
        ("CostoDemandaINs_menos20", {"C_DEM_INS_cambio": 0.8}, None),

        ("CostoDemandaIns_mas10", {"C_DEM_INS_cambio": 1.1}, None),
        ("CostoDemandaINs_menos10", {"C_DEM_INS_cambio": 0.9}, None),

        ("CostoDemandaIns_mas05", {"C_DEM_INS_cambio": 1.05}, None),
        ("CostoDemandaINs_menos05", {"C_DEM_INS_cambio": 0.95}, None),

    ]

    resultados_escenarios = []

    for nombre, cambios, demanda_modificada in escenarios:
        print(f"\n Corriendo escenario: {nombre}")
        tiempos, utilidades, insatisfechas, proporciones = [], [], [], []

        for iteracion in range(iteraciones):
            inicio = time.time()
            #obj, demanda_total, insatis_total, prop_insatis, _ = correr_escenario(nombre, cambios, demanda_modificada)
            result = correr_escenario(nombre, cambios, demanda_modificada)
            if result[0] is None:
                continue

            obj, demanda_total, insatis_total, prop_insatis, _ = result

            tiempos.append(time.time() - inicio)
            utilidades.append(obj)
            insatisfechas.append(insatis_total)
            proporciones.append(prop_insatis)
            # Se calcula el tiempo de ejecución
            fin = time.time()
            tiempo.append(round(fin - inicio, 2))

        # Métricas agregadas
        resultados_escenarios.append({
            "Escenario": nombre,
            "Utilidad_media": sum(utilidades)/len(utilidades),
            "Tiempo_medio": sum(tiempos)/len(tiempos),
            "DemandaInsatisfecha_media": sum(insatisfechas)/len(insatisfechas),
            "ProporcionInsatisfecha_media": sum(proporciones)/len(proporciones)
        })

        # Mostrar estadísticos
        print(f"\nResumen {nombre}")
        print(f"Utilidad: {pd.DataFrame(utilidades).describe()}")
        print(f"Tiempo: {pd.DataFrame(tiempos).describe()}")
        print(f"Demanda Insatisfecha: {pd.DataFrame(insatisfechas).describe()}")
        print(f"Proporción Insatisfecha: {pd.DataFrame(proporciones).describe()}")

        # Graficar histogramas
        for data, titulo, xlabel, color in [
            (utilidades, "Utilidad final ($)", "Utilidad", "navy"),
            (tiempos, "Tiempo de ejecución (s)", "Tiempo", "slategrey"),
            (insatisfechas, "Demanda insatisfecha total", "Unidades", "turquoise"),
            (proporciones, "Proporción de demanda insatisfecha", "Proporción", "gold")
        ]:
            plt.hist(data, color=color, edgecolor='black')
            plt.title(f"{titulo} - {nombre}")
            plt.xlabel(xlabel)
            plt.ylabel("Frecuencia")
            plt.tight_layout()
            #plt.show()

    # Consolidar resultados finales
    df_resumen = pd.DataFrame(resultados_escenarios)
    df_resumen.to_csv("resumen_escenarios_final.csv", index=False)
    print("\n Resultados finales guardados en resumen_escenarios_final.csv")
    print(df_resumen)


