# Parámetros.py
## del codigo de caso base

# Datos
ARCHIVO = 'Tiendas.xlsx'
HOJA = 'Tiendas'
PRECIOS_T1 = 'Precios_T1.txt' 
PRECIOS_T2 = 'Precios_T2.txt'

# Política de inventario
# Costo de producto unitario
C_PROD = {"1": 28792,
          "2": 20792,
          "3": 31992,
          "4": 52792,
          "5": 25592,
          "6": 44800,
          "7": 62993,
          "8": 46492.5,
          "9": 32391.9,
          "10": 17592}
# Costo fijo por pedido
C_FIJO = {"1": 530000,
          "2": 530000,
          "3": 530000,
          "4": 320000,
          "5": 530000,
          "6": 530000,
          "7": 780000,
          "8": 530000,
          "9": 530000,
          "10": 530000}
# Costo de inventario unitario semanal
PROPORCION_INVENTARIO = 0.1
C_INV = {"1": C_PROD["1"] * PROPORCION_INVENTARIO,
          "2": C_PROD["2"] * PROPORCION_INVENTARIO,
          "3": C_PROD["3"] * PROPORCION_INVENTARIO,
          "4": C_PROD["4"] * PROPORCION_INVENTARIO,
          "5": C_PROD["5"] * PROPORCION_INVENTARIO,
          "6": C_PROD["6"] * PROPORCION_INVENTARIO,
          "7": C_PROD["7"] * PROPORCION_INVENTARIO,
          "8": C_PROD["8"] * PROPORCION_INVENTARIO,
          "9": C_PROD["9"] * PROPORCION_INVENTARIO,
          "10": C_PROD["10"] * PROPORCION_INVENTARIO}
# Costo de inventario unitario anual
C_INV_ANUAL = {}
for producto in C_INV:
    C_INV_ANUAL[producto] = C_INV[producto] * 52

# Límites de inventario
CAPACIDAD_T1 = 175000
CAPACIDAD_T2 = 163000
# Para determinar cuántas veces la media pedir
PROPORCION = 1

# Operación
# Cambia mucho las semanas de inicio y final que se eligen para el resultado
# Las primeras semanas son las que tienen los precios menores para cada producto
T_INICIO = 10
T_FINAL = 13

# Demanda fija TODO: cambiar después
DEMANDA_T1 = {"1": (2383.17, 778.05),
              "2": (6254.16, 1878.55),
              "3": (3945.55, 1360.32),
              "4": (1647.19, 429.46),
              "5": (8653.99, 3251.91),
              "6": (2454.59, 733.34),
              "7": (4828.2, 1452.01),
              "8": (3522.1, 1244.45),
              "9": (3.21, 4868.81),
              "10": (3.1, 8327.46)
              }

DEMANDA_T2 = {"1": (2947.03, 893.03),
              "2": (7401.28, 2162.27),
              "3": (3616.79, 1145.49),
              "4": (1273.27, 341.28),
              "5": (7033.34, 2161.95),
              "6": (2335.03, 691.55),
              "7": (5498.86, 1606.57),
              "8": (3402.73, 1258.09),
              "9": (3.64, 4649.04),
              "10": (3.01, 10694.94)
              }