# ────────────────────────── IMPORTS ──────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import (
    train_test_split, TimeSeriesSplit, GridSearchCV
)
from sklearn.metrics import (
    mean_squared_error, r2_score,
    mean_absolute_error, make_scorer
)
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression

# ─────────────────────── UTILIDADES / SCORERS ────────────────
def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


mape_scorer = make_scorer(mape, greater_is_better=False)

# ───────────────────────── CONSTANTES ────────────────────────
ruta = (
    r"datav1.xlsx"
)



# ═════════════════════ 1. CARGA DE DATOS ═════════════════════
df = pd.read_csv(ruta, skiprows=4)
df.rename(columns={'Unnamed: 1': 'Semana'}, inplace=True)
fechas = df['Semana']

columnas_datos = df.columns.tolist()[2:]
pares_columnas = [
    (columnas_datos[i], columnas_datos[i + 1], f"Producto {i // 2 + 1}")
    for i in range(0, len(columnas_datos), 2)
]

datos_largos = []
for col_d, col_p, producto in pares_columnas:
    temp = df[[col_d, col_p]].copy()
    temp.columns = ['Demanda', 'Precio']
    temp['Producto'] = producto
    temp['Semana'] = fechas
    datos_largos.append(temp)

df_largo = pd.concat(datos_largos, ignore_index=True)

# ═════════════════════ 2. PREPROCESAMIENTO ═══════════════════
df_largo['Semana'] = pd.to_datetime(df_largo['Semana'], errors='coerce')
df_largo['Semana_num'] = df_largo['Semana'].dt.isocalendar().week.astype(float)
df_largo['Mes'] = df_largo['Semana'].dt.month

le = LabelEncoder()
df_largo['Producto_cod'] = le.fit_transform(df_largo['Producto'])

df_largo['Precio']  = pd.to_numeric(df_largo['Precio'],  errors='coerce')
df_largo['Demanda'] = pd.to_numeric(df_largo['Demanda'], errors='coerce')
df_largo = df_largo.dropna(subset=['Precio', 'Demanda', 'Semana_num'])

# Variables de contexto
df_largo['Precio_promedio']  = df_largo.groupby('Producto')['Precio'].transform('mean')
df_largo['Demanda_promedio'] = df_largo.groupby('Producto')['Demanda'].transform('mean')
df_largo['Precio_relativo']  = df_largo['Precio'] / df_largo['Precio_promedio']

# Orden cronológico 
df_largo = df_largo.sort_values(['Producto', 'Semana'])
df_largo['Demanda_lag1'] = df_largo.groupby('Producto')['Demanda'].shift(1)
df_largo['Demanda_roll4'] = (
    df_largo.groupby('Producto')['Demanda'].shift(1).rolling(4).mean()
    .reset_index(level=0, drop=True)
)
df_largo = df_largo.dropna(subset=['Demanda_lag1', 'Demanda_roll4'])

# Estacionalidad 
df_largo['sin_season'] = np.sin(2 * np.pi * df_largo['Semana_num'] / 52)
df_largo['cos_season'] = np.cos(2 * np.pi * df_largo['Semana_num'] / 52)
df_largo['Demanda_log'] = np.log1p(df_largo['Demanda'])
df_largo = df_largo[df_largo['Demanda_log'].notna() & np.isfinite(df_largo['Demanda_log'])]
# ═════════════════════ 3. MODELO GLOBAL ═════════════════════
X = df_largo[[
    'Precio', 'Semana_num', 'Mes',
    'Precio_relativo', 'Demanda_promedio',
    'Demanda_lag1', 'Demanda_roll4',
    'sin_season', 'cos_season'
]]
y = df_largo['Demanda_log']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

modelo = XGBRegressor()
modelo.fit(X_train, y_train)

y_pred = modelo.predict(X_test)
y_pred_lvl = np.expm1(y_pred)
y_test_lvl = np.expm1(y_test)
print(f"\n✅ RMSE: {mean_squared_error(y_test_lvl, y_pred_lvl) ** 0.5:.2f}")
print(f"✅ MAE:  {mean_absolute_error(y_test_lvl, y_pred_lvl):.2f}")
print(f"✅ R²:   {r2_score(y_test_lvl, y_pred_lvl):.4f}")


# ── Importancia de variables
plt.figure(figsize=(8, 5))
plt.bar(X.columns, modelo.feature_importances_, color='teal')
plt.title("Importancia de Variables - XGBoost")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
# plt.show()

# ═════════════════════ 4. GRID SEARCH GLOBAL ════════════════
xgb_base = XGBRegressor()
param_grid = {
    'learning_rate': [0.01, 0.03, 0.05],
    'max_depth':     [3, 5, 7],
    'n_estimators':  [300, 600, 900, 1200],
    'subsample':     [0.7, 1],
    'colsample_bytree': [0.7, 1]
}


grid_search = GridSearchCV(
    estimator=xgb_base,
    param_grid=param_grid,
    cv=3,
    scoring='neg_mean_absolute_error',
    verbose=1,
    n_jobs=-1
)
grid_search.fit(X_train, y_train)

print("\n✅ Mejor combinación de hiperparámetros:")
print(grid_search.best_params_)

modelo_optimo = grid_search.best_estimator_
modelo_optimo.fit(X_train, y_train)

y_pred_opt = modelo_optimo.predict(X_test)
y_pred_opt_lvl = np.expm1(y_pred_opt)

rmse = mean_squared_error(y_test_lvl, y_pred_opt_lvl) ** 0.5
mae  = mean_absolute_error(y_test_lvl, y_pred_opt_lvl)
r2   = r2_score(y_test_lvl, y_pred_opt_lvl)
mape_val = (abs(y_test_lvl - y_pred_opt_lvl) / y_test_lvl).mean() * 100


print(f"\n✅ RMSE optimizado: {rmse:.2f}")
print(f"✅ MAE optimizado:  {mae:.2f}")
print(f"✅ R² optimizado:   {r2:.4f}")
print(f"✅ MAPE:            {mape_val:.2f}%")

# ════════════════ 5. MODELOS POR PRODUCTO ═══════════════════
print("\n📦 ENTRENANDO MODELO POR PRODUCTO...")
productos = df_largo['Producto'].unique()
mapes = []


for producto in productos:
    df_prod = df_largo[df_largo['Producto'] == producto].copy()
    df_prod = df_prod.sort_values('Semana')

    Xp = df_prod[[
        'Precio', 'Semana_num', 'Mes',
        'Precio_relativo', 'Demanda_promedio',
        'Demanda_lag1',       
        'Demanda_roll4',     
        'sin_season', 'cos_season'   
    ]]


    yp = df_prod['Demanda_log']
    

    
    mask = yp.notna() & np.isfinite(yp)
    Xp, yp = Xp.loc[mask], yp.loc[mask]

    cut = int(len(yp) * 0.8)              
    Xp_train, Xp_test = Xp.iloc[:cut], Xp.iloc[cut:]
    yp_train, yp_test = yp.iloc[:cut], yp.iloc[cut:]


    param_grid_prod = {
        'learning_rate': [0.01, 0.03, 0.05],
        'max_depth':     [3, 5, 7],
        'n_estimators':  [300, 600, 900, 1200],
        'subsample':     [0.7, 1],
        'colsample_bytree': [0.7, 1]
        }


    tscv = TimeSeriesSplit(n_splits=3)
    gs = GridSearchCV(
        estimator=XGBRegressor(
            objective='reg:squarederror',
            random_state=42,
            n_jobs=-1
        ),
        param_grid=param_grid_prod,
        scoring=mape_scorer,
        cv=tscv,
        verbose=0,
        n_jobs=-1
    )
    gs.fit(Xp_train, yp_train)

    best_model = gs.best_estimator_
    best_model.fit(Xp_train, yp_train)

    yp_pred_log = best_model.predict(Xp_test)
    yp_pred_lvl = np.expm1(yp_pred_log)
    yp_test_lvl = np.expm1(yp_test)
    mape_p = (abs(yp_test_lvl - yp_pred_lvl) / yp_test_lvl).mean() * 100

    mapes.append({
    "Producto":   producto,
    "MAPE_%":     round(mape_p, 2),
    "Profundidad": best_model.max_depth,
    "Árboles":     best_model.n_estimators
})

    print(f"📊 {producto} → MAPE: {mape_p:.2f}%")



# --------------- GUARDAR MÉTRICAS DEL SKU -----------------



# ==========================================================
# 6. PRESENTACIÓN RESUMIDA
# ==========================================================
df_resumen = (pd.DataFrame(mapes)
                .sort_values("MAPE_%")
                .reset_index(drop=True))

print("\n📋  RESUMEN DE ERRORES POR PRODUCTO")
print(df_resumen.to_string(index=False))

mape_simple = df_resumen["MAPE_%"].mean()
print(f"\n✅ MAPE PROMEDIO (simple): {mape_simple:5.2f}%")

# gráfico de barras
plt.figure(figsize=(10, 4))
plt.bar(df_resumen["Producto"], df_resumen["MAPE_%"], color="teal")
plt.axhline(30, ls="--", color="gray", lw=0.8)   
plt.title("MAPE por Producto (ordenado)")
plt.ylabel("MAPE %")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
# ════════════════ GRÁFICO GLOBAL: PRED. vs REAL ═══════════════
plt.figure(figsize=(6, 6))
plt.scatter(y_test_lvl, y_pred_opt_lvl, alpha=0.5, color='teal')
plt.plot([y_test_lvl.min(), y_test_lvl.max()],
        [y_test_lvl.min(), y_test_lvl.max()],
        ls='--', color='gray', lw=1)
plt.title("Demanda real vs Demanda estimada (modelo global)")
plt.xlabel("Demanda real")
plt.ylabel("Demanda estimada")
plt.grid(True, ls=':', lw=0.5)
plt.tight_layout()
plt.show()

###Demanda Promedio###
promedio_predicho = y_pred_opt_lvl.mean()
print(f"Demanda media estimada en el set de prueba: {promedio_predicho:,.0f} unidades por semana")

###Regresión lineal de la demanda###
lr = LinearRegression().fit(y_test_lvl.values.reshape(-1,1), y_pred_opt_lvl)
print(f"Línea estimada:  ŷ = {lr.coef_[0]:.3f}·y_real + {lr.intercept_:.0f}")
#except FileNotFoundError:
#print("\n❌ ERROR: No se encontró el archivo. Verifica la ruta.")
#except Exception as e:
#print(f"\n❌ ERROR inesperado: {e}")
