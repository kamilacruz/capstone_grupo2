import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

# 1) Carga y transformación wide→long (tienda 1 en sheet 0)
df = pd.read_excel("datav2.xlsx", sheet_name=0)

df_long = pd.wide_to_long(
    df,
    stubnames=["demanda", "precio"],
    i="fecha",
    j="product_num",
    sep="",
    suffix=r"\d+"
).reset_index().rename(columns={
    "fecha":       "ds",
    "product_num": "unique_id",
    "demanda":     "y",
    "precio":      "price"
})
df_long["unique_id"] = "prod_" + df_long["unique_id"].astype(str)
df_long["ds"] = pd.to_datetime(df_long["ds"])
df_long = df_long.sort_values(["unique_id", "ds"]).reset_index(drop=True)

# 2) Feature engineering: lags 1–4 de la demanda
for lag in range(1, 5):
    df_long[f"y_lag{lag}"] = df_long.groupby("unique_id")["y"].shift(lag)

# 3) Eliminamos filas con lags faltantes
df_feat = df_long.dropna(subset=[f"y_lag{lag}" for lag in range(1,5)]).reset_index(drop=True)

# 4) Split 80/20 por serie (últimas 4 semanas de cada producto)
h = 4
train_df = (
    df_feat
    .groupby("unique_id", group_keys=False)
    .apply(lambda g: g.iloc[:-h])
    .reset_index(drop=True)
)
test_df = (
    df_feat
    .groupby("unique_id", group_keys=False)
    .apply(lambda g: g.iloc[-h:])
    .reset_index(drop=True)
)

# 5) Preparamos X e y
features = ["price", "y_lag1", "y_lag2", "y_lag3", "y_lag4"]

# convertimos unique_id a numérico
le = LabelEncoder()
train_df["prod_id"] = le.fit_transform(train_df["unique_id"])
test_df["prod_id"]  = le.transform(test_df["unique_id"])
features.append("prod_id")

X_train = train_df[features]
y_train = train_df["y"]
X_test  = test_df[features]
y_test  = test_df["y"]

# 6) Entrenamos XGBoost
model = XGBRegressor(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    verbosity=0
)
model.fit(X_train, y_train)

# 7) Predicción y métricas
y_pred = model.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
bias = np.mean(y_pred - y_test)

print("=== Métricas 4-semanas (split 80/20) ===")
print(f"MAE : {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.2f}%")
print(f"Bias: {bias:.2f}")
