import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from config import nixtla_client

# 1) Carga y wide→long (igual que antes)
df = pd.read_excel("datav2.xlsx", sheet_name=0)
df_long = pd.wide_to_long(
    df, stubnames=["demanda","precio"],
    i="fecha", j="product_num", sep="", suffix=r"\d+"
).reset_index().rename(columns={
    "fecha":"ds","product_num":"unique_id",
    "demanda":"y","precio":"price"
})
df_long["unique_id"] = "prod_"+df_long["unique_id"].astype(str)
df_long["ds"] = pd.to_datetime(df_long["ds"])
df_long = df_long.sort_values(["unique_id","ds"])

# 2) Split 80/20 por serie usando iloc
h = 4   # siempre 4 últimas para test
train_df = df_long.groupby("unique_id", group_keys=False).apply(lambda g: g.iloc[:-h]).reset_index(drop=True)
test_df  = df_long.groupby("unique_id", group_keys=False).apply(lambda g: g.iloc[-h:]).reset_index(drop=True)

print(len(train_df))
print(len(test_df))

X_fut = test_df[["unique_id","ds","price"]]

# 2) Lanza forecast con los hiperparámetros ajustables:
fcst = nixtla_client.forecast(
    df=train_df,                   # tu serie histórica
    X_df=X_fut,                    # exógenas futuras
    h=4,                           # horizonte de 4 semanas
    freq="W-FRI",                  # mismo anclaje semanas-viernes
    target_col="y",                # (opcional, por defecto 'y')
    model="timegpt-1",             # o "timegpt-1-long-horizon"
    finetune_steps=300,             # prueba 10, 30, 50, 100…
    finetune_loss="mae",          # directo a reducir % de error
    finetune_depth=4,              # entre 1 y 5
)

# 3) Homogeneiza la fecha y renombra:
fcst["ds"] = pd.to_datetime(fcst["ds"])
fcst = fcst.rename(columns={"TimeGPT":"yhat"})

# 4) Merge + métricas como ya lo tenías:
eval_df = test_df.merge(fcst[["unique_id","ds","yhat"]], on=["unique_id","ds"])


# 5) Métricas
if len(eval_df):
    y_true = eval_df["y"].values
    y_pred = eval_df["yhat"].values

    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import numpy as np

    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    bias = np.mean(y_pred - y_true)

    print("=== Métricas 4-semanas (split 80/20) ===")
    print(f"MAE : {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"Bias: {bias:.2f}")
else:
    print("Sigue sin haber fechas comunes: revisa tu ‘ds’ en test_df y fcst.")
