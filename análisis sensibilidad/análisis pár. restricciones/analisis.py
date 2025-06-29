import matplotlib.pyplot as plt
import pandas as pd
from modelo_2 import correr_modelo
from variables_parametros2 import ModeloVariablesParametros
import parametros as prm

# ===============================
# CONFIGURACIONES DE EXPERIMENTO
# ===============================

# 1. Elasticidad¿ (gamma)
gamma_escalas = [0.0, 0.5, 1.0, 1.5, 2.0] # No coloque gammas negativos porque no tiene sentido en este contexto

# 2. Capacidad
t1_capacidades = [100000, 150000, 175000, 200000, 250000]
t2_capacidades = [90000, 130000, 163000, 180000, 200000]

# 3. Horizonte temporal (semanas)
horizontes = [6, 8, 10, 12]


# ===============================
# FUNCIONES AUXILIARES
# ===============================

def ajustar_gamma(escalar):
    modelo = ModeloVariablesParametros()
    nueva_gamma = {k: v * escalar for k, v in modelo.gamma.items()}
    modelo.gamma = nueva_gamma
    return modelo

def ajustar_capacidades(cap1, cap2):
    prm.CAPACIDAD_T1 = cap1
    prm.CAPACIDAD_T2 = cap2

def ajustar_horizonte(semanas):
    prm.T_ = list(range(1, semanas + 1))
    prm.T_INICIO = 1


# ===============================
# EXPERIMENTO 1: Variar gamma
# ===============================

def sensibilidad_gamma():
    resultados = []
    for escalar in gamma_escalas:
        print(f"Corriendo con gamma = {escalar}x")
        modelo = ajustar_gamma(escalar)
        resultado = correr_modelo()
        resultados.append((escalar, *resultado))
    df = pd.DataFrame(resultados, columns=["Escala_gamma", "Utilidad", "DemandaTotal", "DemandaInsatisfecha", "ProporcionInsatisfecha"])
    df.to_csv("sensibilidad_gamma.csv", index=False)
    df.plot(x="Escala_gamma", y="Utilidad", kind="line", marker='o', title="Utilidad vs. Elasticidad")
    plt.show()


# ===============================
# EXPERIMENTO 2: Variar capacidad
# ===============================

def sensibilidad_capacidad():
    resultados = []
    for c1, c2 in zip(t1_capacidades, t2_capacidades):
        print(f"Corriendo con capacidades T1={c1}, T2={c2}")
        ajustar_capacidades(c1, c2)
        resultado = correr_modelo()
        resultados.append(((c1, c2), *resultado))
    df = pd.DataFrame(resultados, columns=["Capacidades", "Utilidad", "DemandaTotal", "DemandaInsatisfecha", "ProporcionInsatisfecha"])
    df.to_csv("sensibilidad_capacidad.csv", index=False)
    df.plot(x="Capacidades", y="Utilidad", kind="line", marker='o', title="Utilidad vs. Capacidad")
    plt.xticks(rotation=45)
    plt.show()


# ===============================
# EXPERIMENTO 3: Variar horizonte
# ===============================

def sensibilidad_horizonte():
    resultados = []
    for semanas in horizontes:
        print(f"Corriendo con horizonte de {semanas} semanas")
        ajustar_horizonte(semanas)
        resultado = correr_modelo()
        resultados.append((semanas, *resultado))
    df = pd.DataFrame(resultados, columns=["Semanas", "Utilidad", "DemandaTotal", "DemandaInsatisfecha", "ProporcionInsatisfecha"])
    df.to_csv("sensibilidad_horizonte.csv", index=False)
    df.plot(x="Semanas", y="Utilidad", kind="line", marker='o', title="Utilidad vs. Horizonte")
    plt.show()


# ===============================
# CORRER TODOS
# ===============================
if __name__ == "__main__":
    sensibilidad_gamma()
    sensibilidad_capacidad()
    sensibilidad_horizonte()
