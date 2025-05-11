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
T_FINAL = 20

# Demanda fija TODO: cambiar después
DEMANDA_T1 = {"1": (1600, 3300),
              "2": (3500, 8500),
              "3": (4500, 5500),
              "4": (1200, 2100),
              "5": (6500, 12000),
              "6": (1600, 3200),
              "7": (3500, 6500),
              "8": (2700, 5500),
              "9": (3000, 6000),
              "10": (5000, 10000)
              }

DEMANDA_T2 = {"1": (2000, 4000),
              "2": (5000, 10000),
              "3": (2500, 5000),
              "4": (1000, 2000),
              "5": (5500, 9500),
              "6": (1600, 3200),
              "7": (4000, 7500),
              "8": (2500, 5000),
              "9": (3000, 5800),
              "10": (7000, 12500)
              }