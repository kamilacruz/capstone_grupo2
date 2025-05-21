# variables_parametros.py
from gurobipy import GRB, Model
import math
import numpy as np
from parametros import DEMANDA_T1, DEMANDA_T2, T_INICIO, T_FINAL

class ModeloVariablesParametros:
    def __init__(self):
        #indices, sus conjuntos
        self.I = 10  #productos
        self.J = 2   #tiendas
        self.T = 10  #horizonte de semanas

        #rangos 
        self.I_ = range(1, self.I + 1)
        self.J_ = range(1, self.J + 1)
        self.T_ = range(T_INICIO, T_FINAL + 1)

        # modelo
        self.m = Model("Modelo")

        # parametros

        # Costo de producto unitario
        self.C_PROD = {1: 28792,
                2: 20792,
                3: 31992,
                4: 52792,
                5: 25592,
                6: 44800,
                7: 62993,
                8: 46492.5,
                9: 32391.9,
                10: 17592}
        # Costo fijo por pedido
        self.C_FIJO = {1: 530000,
                2: 530000,
                3: 530000,
                4: 320000,
                5: 530000,
                6: 530000,
                7: 780000,
                8: 530000,
                9: 530000,
                10: 530000}
        # Costo de inventario unitario semanal
        self.PROPORCION_INVENTARIO = 0.1
        #self.C_INV = {1: self.C_PROD[1] * self.PROPORCION_INVENTARIO,
        #        2: self.C_PROD[2] * self.PROPORCION_INVENTARIO,
        #        3: self.C_PROD[3] * self.PROPORCION_INVENTARIO,
        #        4: self.C_PROD[4] * self.PROPORCION_INVENTARIO,
        #        5: self.C_PROD[5] * self.PROPORCION_INVENTARIO,
        #        6: self.C_PROD[6] * self.PROPORCION_INVENTARIO,
        #        7: self.C_PROD[7] * self.PROPORCION_INVENTARIO,
        #        8: self.C_PROD[8] * self.PROPORCION_INVENTARIO,
        #        9: self.C_PROD[9] * self.PROPORCION_INVENTARIO,
        #        10: self.C_PROD[10] * self.PROPORCION_INVENTARIO}
        # CREO QUE ESTA LÍNEA ES MEJOR PARA LO ANTERIOR, DEBERÍA HACER LO MISMO
        self.C_INV = {i: self.C_PROD[i] * self.PROPORCION_INVENTARIO for i in self.I_}

        # Límites de inventario
        self.CAPACIDAD_T1 = 175000
        self.CAPACIDAD_T2 = 163000

        self.CMO = {1: 300,
                2: 700,
                3: 500,
                4: 260,
                5: 900,
                6: 350,
                7: 1000,
                8: 450,
                9: 450,
                10: 900}
        

# AQUÍ SE INGRESA LO QUE NOS ENTREGARÍA EL MODELO ML DE A Y B

        self.d = {} #DEMANDA ESTIMADA POR ML
        # TEMPORALMENTE SERÍAN INSTANCIAS DE LAS DISTRIBUCIONES

        for j in self.J_:
            if j == 1:
                demanda_base = DEMANDA_T1
            else:
                demanda_base = DEMANDA_T2
            for i in self.I_:
                media, param = demanda_base[str(i)]
                for t in self.T_:
                    if i in [9, 10]:
                        val = np.random.weibull(media) * param
                    else:
                        val = np.random.normal(media, param)
                    self.d[i, j, t] = max(0, math.ceil(val))

        self.A = {}  # Demanda base
        self.B = {}  # Elasticidad

        for i in self.I_:
            for j in self.J_:
                for t in self.T_:
                    self.A[i, j, t] =  15000 ##CAMBIAR ESTE NUMERO  
                    self.B[i, j, t] = 0.6 ##CAMBIAR ESTE NUMERO

        # TEMPORALMENTE SERÍA EL RANDOOM DE LA DEMANDA DEL CASO BASE
        #
        #for j in self.J_:  # tiendas
        #    demanda_base = DEMANDA_T1 if j == 1 else DEMANDA_T2
        #    for i in self.I_:  # productos
        #        media, param = demanda_base[str(i)]
        #        for t in range(T_INICIO, T_FINAL + 1):  # semanas relevantes
        #            if i in [9, 10]:
        #                val = np.random.weibull(media) * param
        #            else:
        #                val = np.random.normal(media, param)
        #            self.d[i, j, t] = max(0, math.ceil(val))


        # d = self.A[i, j, t] - self.B[i, j, t] * self.p[i, j, t] 
        # LO ANTERIOR, (d) SE DEFINE COMO FUNCIÓN EN RESTRICCIONES


        # variables
        ## por ahora continuas para que corra más rápido
        self.q = self.m.addVars(self.I_, self.J_, self.T_, vtype=GRB.CONTINUOUS, name='q') #cantidad a pedir
        self.p = self.m.addVars(self.I_, self.J_, self.T_, vtype=GRB.CONTINUOUS, name='p') #precio
        self.z = self.m.addVars(self.I_, self.J_, self.T_, vtype=GRB.BINARY, name='z') #binaria si se pide
        self.v = self.m.addVars(self.I_, self.J_, self.T_, vtype=GRB.CONTINUOUS, name='v') #venta 
        self.inv = self.m.addVars(self.I_, self.J_, self.T_, vtype=GRB.CONTINUOUS, name='inv') #inventario
        self.di = self.m.addVars(self.I_, self.J_, self.T_, vtype=GRB.CONTINUOUS, name='di') #demanda insatisfecha

        # PARA LA NATURALEZA DE LAS VARIABLES EXISTE GRB.INTEGER PARA LOS ENTEROS NO NEGATIVOS (ENTEROS MAYORES O IGUALES A 0), sisee pero lee el comentario de arriba que corre más rapido si es continuo, para probar


    def obtener_modelo(self):
        return self.m

    def obtener_variables(self): ##ojo con el orden
        return self.q, self.p, self.z, self.v, self.inv, self.di
        

    def obtener_parametros(self):
        return self.C_PROD, self.C_FIJO, self.C_INV, self.CAPACIDAD_T1, self.CAPACIDAD_T2, self.CMO, self.d, self.A, self.B

    def obtener_rangos(self):
        return {
            'I_': self.I_,
            'J_': self.J_,
            'T_': self.T_
        }
