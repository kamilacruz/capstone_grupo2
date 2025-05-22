import os
import math
import time
import random
import numpy as np
import pandas as pd
import parametros as prm


# Ruta del archivo Excel
ruta = os.path.join('datos', prm.ARCHIVO)
# Ruta de los precios
ruta_precios_t1 = os.path.join('datos', prm.PRECIOS_T1)
ruta_precios_t2 = os.path.join('datos', prm.PRECIOS_T2)
# Creación del dataframe
df = pd.read_excel(ruta)

# Datos por tiendas
df1 = df[df['Tienda'] == 'Tienda 1']
df2 = df[df['Tienda'] == 'Tienda 2']
# Df por productos de tienda 1
df_tienda1 = {"1": df1[df1['Producto'] == 1],
           "2": df1[df1['Producto'] == 2],
           "3": df1[df1['Producto'] == 3],
           "4": df1[df1['Producto'] == 4],
           "5": df1[df1['Producto'] == 5],
           "6": df1[df1['Producto'] == 6],
           "7": df1[df1['Producto'] == 7],
           "8": df1[df1['Producto'] == 8],
           "9": df1[df1['Producto'] == 9],
           "10": df1[df1['Producto'] == 10]
           }
# Df por productos de tienda 2
df_tienda2 = {"1": df2[df2['Producto'] == 1],
           "2": df2[df2['Producto'] == 2],
           "3": df2[df2['Producto'] == 3],
           "4": df2[df2['Producto'] == 4],
           "5": df2[df2['Producto'] == 5],
           "6": df2[df2['Producto'] == 6],
           "7": df2[df2['Producto'] == 7],
           "8": df2[df2['Producto'] == 8],
           "9": df2[df2['Producto'] == 9],
           "10": df2[df2['Producto'] == 10]
           }

# Guardar política de precios por semana para ambas tiendas
precios_t1 = {"1": [],
           "2": [],
           "3": [],
           "4": [],
           "5": [],
           "6": [],
           "7": [],
           "8": [],
           "9": [],
           "10": []
           }

precios_t2 = {"1": [],
           "2": [],
           "3": [],
           "4": [],
           "5": [],
           "6": [],
           "7": [],
           "8": [],
           "9": [],
           "10": []
           }

# Se carga la política de precios del año para ambas tiendas
with open(ruta_precios_t1, 'r', encoding = 'utf-8') as archivo:
    for linea in archivo:
        linea = linea[:-1]
        linea = linea.split(",")
        producto, semana, precio = linea[0], int(linea[1]), int(linea[2])
        precios_t1[producto].append((semana, precio))

with open(ruta_precios_t2, 'r', encoding = 'utf-8') as archivo:
    for linea in archivo:
        linea = linea[:-1]
        linea = linea.split(",")
        producto, semana, precio = linea[0], int(linea[1]), int(linea[2])
        precios_t2[producto].append((semana, precio))


# Creación de clase con los dataframe respectivos
class DataFrame:
    def __init__(self, df, limite_inventario, precios):
        self.df = df
        self.inventario = {}
        self.ocupacion_inventario = 0
        self.limite_inventario = limite_inventario
        self.utilidad = 0
        self.precios = precios
        self.acumulado_insatisfecha = 0
        self.acumulado_demanda = 0

    # Determina el EOQ del producto
    def eoq(self):
        dict_eoq = {}
        for producto in self.df:
            demanda = self.df[producto]["Demanda"].mean()
            c_fijo = prm.C_FIJO[producto]
            c_inv = prm.C_INV_ANUAL[producto]
            eoq = math.sqrt(2 * demanda * 52 * c_fijo / c_inv)
            dict_eoq[producto] = round(eoq, 0)
        return dict_eoq
    
    # Determina el inventario inicial y cuánto pedir semanalmente por producto
    def pedido_semanal(self):
        dict_pedidos = {}
        for producto in self.df:
            demanda = self.df[producto]["Demanda"].mean()
            desv_est = self.df[producto]["Demanda"].std()
            inventario_inicial = round((demanda + desv_est) * prm.PROPORCION_INICIAL, 0)
            pedido_semanal = round(demanda * prm.PROPORCION_PEDIDO, 0)
            dict_pedidos[producto] = (inventario_inicial, pedido_semanal)
        return dict_pedidos
    
    # Carga el inventario inicial, se cobra el monto respectivo
    def cargar_inventario_inicial(self):
        pedidos = self.pedido_semanal()
        costo = 0
        for producto in pedidos:
            self.inventario[producto] = pedidos[producto][0]
            self.ocupacion_inventario += pedidos[producto][0]
            # El inventario inicial se cobra
            costo_fijo = prm.C_FIJO[producto]
            costo_variable = pedidos[producto][0] * prm.C_PROD[producto]
            costo += costo_fijo + costo_variable
        self.utilidad -= costo

    # Carga el inventario semanal, revisando la capacidad
    def cargar_inventario(self):
        pedidos = self.pedido_semanal()
        for producto in pedidos:
            pedido = pedidos[producto][1]
            if self.ocupacion_inventario + pedido <= self.limite_inventario:
                # Revisar que no haya más de lo que había inicialmente para no pedir
                if self.inventario[producto] <= pedidos[producto][0]:
                    self.inventario[producto] += pedido
                    self.ocupacion_inventario += pedido
    
    # Se paga el pedido
    def pagar_pedido(self):
        pedidos = self.pedido_semanal()
        costo = 0
        for producto in pedidos:
            pedido = pedidos[producto][1]
            if self.ocupacion_inventario + pedido <= self.limite_inventario:
                if self.inventario[producto] <= pedidos[producto][0]:
                    costo_variable = pedidos[producto][1] * prm.C_PROD[producto]
                    costo_fijo = prm.C_FIJO[producto]
                    costo += costo_variable + costo_fijo
        self.utilidad -= costo
    
    # Se paga al final de la semana el monto de inventario
    def pagar_inventario(self):
        costo = 0
        for producto in self.inventario:
            costo += self.inventario[producto] * prm.C_INV[producto]
        self.utilidad -= costo
    
    # Se vende según la demanda de cada producto y se cobra lo correspondiente
    def vender(self, semana, demanda):
        ingreso = 0
        for producto in self.inventario:
            venta = min(self.inventario[producto], demanda[producto])
            self.inventario[producto] -= venta
            self.ocupacion_inventario -= venta
            ingreso += venta * self.precios[producto][semana - 1][1]
            self.acumulado_demanda += demanda[producto]
        self.utilidad += ingreso


    # Se revisa si hay demanda insatisfecha y se cobra en caso de haber
    def cobrar_demanda_insatisfecha(self, semana, demanda):
        costo = 0
        for producto in self.inventario:
            if self.inventario[producto] < demanda[producto]:
                demanda_insatisfecha = demanda[producto] - self.inventario[producto]
                costo += demanda_insatisfecha * self.precios[producto][semana - 1][1] * 0.1
                self.acumulado_insatisfecha += demanda_insatisfecha
        self.utilidad -= costo
    
    # Imprime el EOQ, Inventario inicial y Pedido semanal estimado por producto
    def imprimir_politica(self):
        texto = ''
        eoq = self.eoq()
        pedidos = self.pedido_semanal()
        for producto in self.df:
            texto += f'EOQ del producto {producto}: {eoq[producto]}\n'
            texto += f'Inventario inicial del producto {producto}: {pedidos[producto][0]} \n'
            texto += f'Pedido semanal del producto {producto}: {pedidos[producto][1]} \n\n'
        return print(texto)
    
    # Imprime un resumen del estado de la tienda
    def __str__(self):
        texto = ''
        texto += f'Resultado de la operación\n'
        texto += f'Utilidad acumulada: {round(self.utilidad, 0)}\n'
        texto += f'Demanda insatisfecha acumulada: {self.acumulado_insatisfecha}\n'
        texto += f'Ocupación final del inventario: {self.ocupacion_inventario}\n\n'
        return texto

# Generador de demanda
# Corresponde a una instancia según la distribución ajustada de cada producto en cada tienda
# Se toma el entero superior al valor demandado, para que sea un valor entero
def demandado(demanda):
    demandado = {"1": 0,
                 "2": 0,
                 "3": 0,
                 "4": 0,
                 "5": 0,
                 "6": 0,
                 "7": 0,
                 "8": 0,
                 "9": 0,
                 "10": 0
                 }
    for producto in demandado:
        if producto != "9" and producto != "10":
            demandado[producto] = np.random.normal(demanda[producto][0], demanda[producto][1])
        else:
            demandado[producto] = np.random.weibull(demanda[producto][0]) * demanda[producto][1]
        demandado[producto] = math.ceil(demandado[producto])
    return demandado



# Ejecución del problema del caso base
# TODO: Que solo cobre en la semana t y que el inventario se cargue en la t+1.
# De momento se cobra y carga al final de la semana t

def generar_iteracion():

    # Inicio
    inicio = time.time()
    semana = 0

    # Creación de ambas tiendas con sus respectivos datos
    Tienda1 = DataFrame(df_tienda1, prm.CAPACIDAD_T1, precios_t1)
    Tienda2 = DataFrame(df_tienda2, prm.CAPACIDAD_T2, precios_t2)

    # Se carga el inventario inicial
    Tienda1.cargar_inventario_inicial()
    Tienda2.cargar_inventario_inicial()

    # Se genera la iteración para ambas tiendas 
    for t in range(prm.T_INICIO, prm.T_FINAL + 1):
        semana = t
        demanda_1 = demandado(prm.DEMANDA_T1)
        Tienda1.cobrar_demanda_insatisfecha(semana, demanda_1)
        Tienda1.pagar_inventario()
        Tienda1.vender(semana, demanda_1)
        Tienda1.pagar_pedido()
        Tienda1.cargar_inventario()
        demanda_2 = demandado(prm.DEMANDA_T2)
        Tienda2.cobrar_demanda_insatisfecha(semana, demanda_2)
        Tienda2.pagar_inventario()
        Tienda2.vender(semana, demanda_2)
        Tienda2.pagar_pedido()
        Tienda2.cargar_inventario()
    
    # Fin
    fin = time.time()

    duracion = round(fin - inicio, 3)
    resumen_t1 = [round(float(Tienda1.utilidad), 2),
                  float(Tienda1.acumulado_insatisfecha),
                  float(Tienda1.acumulado_demanda)]
    resumen_t2 = [round(float(Tienda2.utilidad), 2),
                  float(Tienda2.acumulado_insatisfecha),
                  float(Tienda1.acumulado_demanda)]

    return [duracion, resumen_t1, resumen_t2]