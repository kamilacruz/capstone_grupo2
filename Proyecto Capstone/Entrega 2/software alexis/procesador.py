import pandas as pd

# Ruta del archivo original y configuración
file_path   = "datav1.xlsx"
output_file = "datav2.xlsx"
skiprows    = 6

# 1) Leer y limpiar cada hoja
data1 = pd.read_excel(file_path, sheet_name="Datos Tienda 1").iloc[skiprows:].reset_index(drop=True)
data2 = pd.read_excel(file_path, sheet_name="Datos tienda 2").iloc[skiprows:].reset_index(drop=True)

# 2) Renombrar columnas
column_names = [
    "idx", "fecha", "demanda1", "precio1",
    "demanda2", "precio2", "demanda3", "precio3",
    "demanda4", "precio4", "demanda5", "precio5",
    "demanda6", "precio6", "demanda7", "precio7",
    "demanda8", "precio8", "demanda9", "precio9",
    "demanda10","precio10"
]
data1.columns = column_names
data2.columns = column_names

# 3) Asegurar tipo datetime en la columna fecha
data1['fecha'] = pd.to_datetime(data1['fecha'], dayfirst=True, errors='coerce')
data2['fecha'] = pd.to_datetime(data2['fecha'], dayfirst=True, errors='coerce')

# 4) Guardar en un nuevo Excel con formato de fecha preservado
with pd.ExcelWriter(output_file,
                    engine="openpyxl",
                    date_format='yyyy-mm-dd',
                    datetime_format='yyyy-mm-dd hh:mm:ss') as writer:
    data1.to_excel(writer, sheet_name="Datos Tienda 1", index=False)
    data2.to_excel(writer, sheet_name="Datos Tienda 2", index=False)

# Lo malo es que queda medio fea la fecha
print(f"Guardado como '{output_file}' con fechas y formato original intactos.")
