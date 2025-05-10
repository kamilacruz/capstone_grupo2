import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from neuralforecast import NeuralForecast
from neuralforecast.models import NHITS

# 1) Carga y transformación wide→long (igual que antes)
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

# 2) Split 80/20 por serie usando iloc
h = 4  # horizonte de 4 semanas
train_df = (
    df_long
    .groupby("unique_id", group_keys=False)
    .apply(lambda g: g.iloc[:-h])
    .reset_index(drop=True)
)
test_df = (
    df_long
    .groupby("unique_id", group_keys=False)
    .apply(lambda g: g.iloc[-h:])
    .reset_index(drop=True)
)

print(f"Train rows: {len(train_df)}, Test rows: {len(test_df)}")

# 3) Instancia y configura N-HITS
model = NeuralForecast(
    models=[
        NHITS(
            h=h,                    # horizonte
            input_size=12+6,          # ventana autoregresiva (ajústalo)
            hist_exog_list=["price"],  # exógenas históricas
            futr_exog_list=["price"],  # exógenas futuras
            max_steps=100,          # pasos de predicción (ajústalo)
            mlp_units=			[[ 32, 64], [ 64, 128], [128, 256]],
            dropout_prob_theta=0.3,
            pooling_mode="AvgPool1d",
            step_size=4
            
        )
    ],
    freq="W-FRI",  # semanal anclado a viernes
)

# 4) Entrena el modelo
model.fit(df=train_df)

# 5) Predice las próximas h semanas
#    Si quieres pasar exógenas futuras explícitas:
# X_fut = test_df[["unique_id","ds","price"]]
# fcst = model.predict(df=train_df, X_df=X_fut)
futr_df = test_df[["unique_id","ds","price"]]

fcst = model.predict(
    df=train_df,
    futr_df=futr_df
)

# homogeneizar nombres
fcst = fcst.rename(columns={"NHITS":"yhat"})
fcst["ds"] = pd.to_datetime(fcst["ds"])

eval_df = test_df.merge(
    fcst[["unique_id", "ds", "yhat"]],
    on=["unique_id", "ds"],
    how="inner"
)

# 7) Cálculo de métricas
y_true = eval_df["y"].values
y_pred = eval_df["yhat"].values

mae  = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
bias = np.mean(y_pred - y_true)

print("=== Métricas 4-semanas (80/20 split) ===")
print(f"MAE : {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.2f}%")
print(f"Bias: {bias:.2f}")