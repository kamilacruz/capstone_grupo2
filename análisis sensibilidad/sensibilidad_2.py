from gurobipy import GRB, Model, quicksum, max_
from variables_parametros2 import ModeloVariablesParametros
import os
import pandas as pd 
import parametros as prm
from modelo_2 import correr_modelo, exportar_resultados_a_df, exportar_a_bbdd
import time
import matplotlib.pyplot as plt

## nuev función para hacer más fácil el cambio de parámetros
def correr_escenario(nombre_escenario, cambios_param={}, d_real_modificada=None):
    #nombre_escenario solo para ordenarse que es lo que se está corriendo
    #cambios_param es un diccionario para poner los cambios en los parámetros que se evaluan en ese escenario
    ## no se como tomar la demanda cambiada, el tercer argumento es eso
    modelo = ModeloVariablesParametros()

    # cambia los paámetros según el argumento de la función, así más fácil evaluar varias cosas y combinaciones
    if 'C_INV_cambio' in cambios_param:
        for i in modelo.C_INV:
            modelo.C_INV[i] *= cambios_param['C_INV_cambio']

    if 'C_FIJO_cambio' in cambios_param:
        for i in modelo.C_FIJO:
            modelo.C_FIJO[i] *= cambios_param['C_FIJO_cambio']
    
    if 'C_PROD_cambio' in cambios_param:
        for i in modelo.C_PROD:
            modelo.C_PROD[i] *= cambios_param['C_PROD_cambio']

    if 'C_DEM_INS_cambio' in cambios_param:
        for i in modelo.C_DEM_INS:
            modelo.C_DEM_INS[i] *= cambios_param['C_DEM_INS_cambio']



    if d_real_modificada:
        modelo.d = d_real_modificada


    obj, demanda_total, insatisfecha_total, proporcion_insatisfecha, df_resultados = correr_modelo_escenario(modelo)
    return obj, demanda_total, insatisfecha_total, proporcion_insatisfecha, df_resultados



## igual que correr_modelo(), pero no creo un nuevo modelo = ModeloVariablesParametros(), sino que uso el que ya tengo en el escenario

def correr_modelo_escenario(modelo):

    m = modelo.obtener_modelo()

    #variables ----- ojo con el orden
    q, p, z, v, inv, di, DE = modelo.obtener_variables() ##DE de modelo_2

    #parametros 
    C_PROD, C_FIJO, C_INV, CAPACIDAD_T1, CAPACIDAD_T2, CMO, d, A, B1, B2, d_estimada, proporcion_maxima, C_DEM_INS = modelo.obtener_parametros()
    ## nuevo C_DEM_INS, cambio tmb en variables_parametros
    ## A, B1 y B2 según variables_parametros_2
    
    gamma = modelo.gamma ##nuevo de modelo_2

    M = 1000000
    rangos = modelo.obtener_rangos()
    I_ = rangos['I_']
    J_ = rangos['J_']
    T_ = rangos['T_']

    #funcion objetivo 
    FO = quicksum(p[i, j, t] * v[i, j, t] - C_INV[i] * inv[i, j, t] - C_PROD[i] * q[i, j, t] - C_FIJO[i] * z[i, j, t] - C_DEM_INS[i] * di[i, j, t] * p[i, j, t] for i in I_ for j in J_ for t in T_)
    m.setObjective(FO, GRB.MAXIMIZE) 

    # 1. Qijt <= M*zijt	
    m.addConstrs(q[i, j, t] <= M * z[i, j, t] for i in I_ for j in J_ for t in T_)

    # 2. Pijt >= 1.05(CPi)
    m.addConstrs(p[i, j, t] >= 1.05 * C_PROD[i] for i in I_ for j in J_ for t in T_)

    # 3. No arbitraje Pi1t – Pi2t <= 3.8, Pi2t – Pi1t <= 3.8
    m.addConstrs(p[i, 1, t] - p[i, 2, t] <= 3800 for i in I_ for t in T_)
    m.addConstrs(p[i, 2, t] - p[i, 1, t] <= 3800 for i in I_ for t in T_)

    # 4. Sum{i=1}_{N} Ii1t <= 175000 Sum{i=1}_{N} Ii2t <= 163000
    m.addConstrs(quicksum(inv[i, 1, t] for i in I_) <= CAPACIDAD_T1 for t in T_)
    m.addConstrs(quicksum(inv[i, 2, t] for i in I_) <= CAPACIDAD_T2 for t in T_)

    ## nuevo de modelo_2
    # 5. DE_ijt = (d_estimada)_ijt + gamma_ij * (P_ijt - P_ijt-1)
    # Para t = T_INICIO
    m.addConstrs(
        (DE[i, j, prm.T_INICIO] == d_estimada[f"{i},{j},{prm.T_INICIO}"]
        for i in I_ for j in J_), name="def_DE_inicio"
    )

    # Para t > T_INICIO
    m.addConstrs(
        (DE[i, j, t] == d_estimada[f"{i},{j},{t}"] + gamma[i, j] * (p[i, j, t] - p[i, j, t - 1])
        for i in I_ for j in J_ for t in T_ if t > prm.T_INICIO), name="def_DE_rest"
    )

    # 6. Qijt >= CMOi	* z_ijt	
    m.addConstrs(q[i, j, t] >= CMO[i] * z[i, j, t] for i in I_ for j in J_ for t in T_)


    # 7. Demanda insatisfecha  DIijt(Pijt) = Dijt(Pijt) – Vijt 
    m.addConstrs(di[i, j, t] == d[i, j, t] - v[i, j, t] for i in I_ for j in J_ for t in T_)

    # 8. Venta del producto Vijt <= Dijt(pijt), Vijt <= Iijt
    m.addConstrs(v[i, j, t] <= d[i, j, t] for i in I_ for j in J_ for t in T_)
    m.addConstrs(v[i, j, t] <= inv[i, j, t] for i in I_ for j in J_ for t in T_)    

    # 9. Iijt+1 = Iijt - Vijt + Qijt	
    m.addConstrs(inv[i, j, t] == inv[i, j, t-1] - v[i, j, t] + q[i, j, t-1] for i in I_ for j in J_ for t in T_[1:])
    m.addConstrs(inv[i, j, prm.T_INICIO] == 5000 for i in I_ for j in J_)   

    # 10 d = self.A[i, j, t] - self.B[i, j, t] * self.p[i, j, t]
    #m.addConstrs(p[i, j, t] <= max((A[i, j] - d_estimada[str(f'{i},{j},{t}')])/ B[i, j], (proporcion_maxima * C_PROD[i])) for i in I_ for j in J_ for t in T_)

    ## nueva 10 de modelo_2
        # 10 pijt = Aijt + B1ijt * DEijt + B2ijt * DEijt^2 
    # crea la variable auxiliar (esto va en tu clase de variables)
    p_max = m.addVars(I_, J_, T_, name="p_max")

    # define que sea el máximo
    m.addConstrs(
        (p_max[i, j, t] >= A[i, j] + B1[i, j] * DE[i, j, t] + B2[i, j] * DE[i, j, t] * DE[i, j, t]
        for i in I_ for j in J_ for t in T_),
        name="p_max_expr"
    )
    m.addConstrs(
        (p_max[i, j, t] >= proporcion_maxima * C_PROD[i]
        for i in I_ for j in J_ for t in T_),
        name="p_max_cap"
    )

    # finalmente, usa esa variable en la restricción original
    m.addConstrs(
        (p[i, j, t] <= p_max[i, j, t]
        for i in I_ for j in J_ for t in T_),
        name="p_limited_by_max"
    )

    m.update()

    m.setParam('MIPGap', 0.01) ## achicar este valor
    m.optimize()

    if m.Status != GRB.OPTIMAL and m.Status != GRB.SUBOPTIMAL:
        print(f" El modelo en el escenario no encontró solución (status {m.Status})")
        return None, None, None, None, None


    ##las funciones definidas en modelo.py
    df_resultados = exportar_resultados_a_df(modelo)
    exportar_a_bbdd(modelo)

    #kpis del modelo.py
    insatisfecha_total = df_resultados["DemandaInsatisfecha"].sum()
    demanda_total = df_resultados["DemandaInsatisfecha"].sum() + df_resultados["Venta"].sum()
    proporcion_insatisfecha = float(insatisfecha_total / demanda_total)

    return [m.ObjVal, demanda_total, insatisfecha_total, proporcion_insatisfecha, df_resultados]


