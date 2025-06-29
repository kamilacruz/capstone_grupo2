install.packages("readxl")
install.packages("dplyr")
install.packages("broom")
library(readxl)
library(dplyr)
library(broom)
library(tidyr)
library(purrr)
archivo <- file.choose() 
datos_t1 <- read_excel(archivo, sheet = "Datos Tienda 1")
datos_t2 <- read_excel(archivo, sheet = "Datos Tienda 2")

# Transformación a formato largo para Tienda 1
t1_largo <- datos_t1 %>%
  pivot_longer(cols = starts_with("demanda"), names_to = "var_demanda", values_to = "demanda") %>%
  bind_cols(
    datos_t1 %>%
      pivot_longer(cols = starts_with("precio"), names_to = "var_precio", values_to = "precio") %>%
      select(precio)
  ) %>%
  mutate(t1_producto = as.integer(gsub("demanda", "", var_demanda))) %>%
  select(idx, fecha, t1_producto, demanda, precio) %>%
  filter(!is.na(demanda), !is.na(precio))


# Generar los modelos y guardar coeficientes y métricas para Tienda 1
t1_modelos <- t1_largo %>%
  group_by(t1_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(demanda ~ precio, data = .x)),
    resumen = map(modelo, ~ tidy(.x)),
    ajuste   = map(modelo, ~ glance(.x))
  ) %>%
  mutate(
    B = map_dbl(resumen, ~ .x$estimate[.x$term == "precio"]),
    p_valor_B = map_dbl(resumen, ~ .x$p.value[.x$term == "precio"]),
    A = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared),
  ) %>%
  select(t1_producto, A, B, R2, p_valor_B)

print(t1_modelos)

# Modelo cuadrático para Tienda 1
t1_modelos_cuad <- t1_largo %>%
  group_by(t1_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(demanda ~ precio + I(precio^2), data = .x)),
    resumen = map(modelo, tidy),
    ajuste  = map(modelo, glance)
  ) %>%
  mutate(
    A = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    B1 = map_dbl(resumen, ~ .x$estimate[.x$term == "precio"]),
    B2 = map_dbl(resumen, ~ .x$estimate[.x$term == "I(precio^2)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared),
    p_B1 = map_dbl(resumen, ~ .x$p.value[.x$term == "precio"]),
    p_B2 = map_dbl(resumen, ~ .x$p.value[.x$term == "I(precio^2)"])
  ) %>%
  select(t1_producto, A, B1, B2, R2, p_B1, p_B2)

print(t1_modelos_cuad)

#########################################################################3

# Transformación a formato largo para Tienda 2
t2_largo <- datos_t2 %>%
  pivot_longer(cols = starts_with("demanda"), names_to = "var_demanda", values_to = "demanda") %>%
  bind_cols(
    datos_t2 %>%
      pivot_longer(cols = starts_with("precio"), names_to = "var_precio", values_to = "precio") %>%
      select(precio)
  ) %>%
  mutate(t2_producto = as.integer(gsub("demanda", "", var_demanda))) %>%
  select(idx, fecha, t2_producto, demanda, precio) %>%
  filter(!is.na(demanda), !is.na(precio))


# Generar los modelos y guardar coeficientes y métricas para Tienda 2
t2_modelos <- t2_largo %>%
  group_by(t2_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(demanda ~ precio, data = .x)),
    resumen = map(modelo, ~ tidy(.x)),
    ajuste   = map(modelo, ~ glance(.x))
  ) %>%
  mutate(
    B = map_dbl(resumen, ~ .x$estimate[.x$term == "precio"]),
    p_valor_B = map_dbl(resumen, ~ .x$p.value[.x$term == "precio"]),
    A = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared),
  ) %>%
  select(t2_producto, A, B, R2, p_valor_B)

print(t2_modelos)

# Modelo cuadrático para Tienda 2
t2_modelos_cuad <- t2_largo %>%
  group_by(t2_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(demanda ~ precio + I(precio^2), data = .x)),
    resumen = map(modelo, tidy),
    ajuste  = map(modelo, glance)
  ) %>%
  mutate(
    A = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    B1 = map_dbl(resumen, ~ .x$estimate[.x$term == "precio"]),
    B2 = map_dbl(resumen, ~ .x$estimate[.x$term == "I(precio^2)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared),
    p_B1 = map_dbl(resumen, ~ .x$p.value[.x$term == "precio"]),
    p_B2 = map_dbl(resumen, ~ .x$p.value[.x$term == "I(precio^2)"])
  ) %>%
  select(t2_producto, A, B1, B2, R2, p_B1, p_B2)

print(t2_modelos_cuad)

############################################################################

# Modelo cuadrático para Tienda 1 en función de la demanda
t1_modelos_cuad_dem <- t1_largo %>%
  group_by(t1_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(precio ~ demanda + I(demanda^2), data = .x)),
    resumen = map(modelo, tidy),
    ajuste  = map(modelo, glance)
  ) %>%
  mutate(
    a = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    b1 = map_dbl(resumen, ~ .x$estimate[.x$term == "demanda"]),
    b2 = map_dbl(resumen, ~ .x$estimate[.x$term == "I(demanda^2)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared),
    p_b1 = map_dbl(resumen, ~ .x$p.value[.x$term == "demanda"]),
    p_b2 = map_dbl(resumen, ~ .x$p.value[.x$term == "I(demanda^2)"])
  ) %>%
  select(t1_producto, a, b1, b2, R2, p_b1, p_b2)

print(t1_modelos_cuad_dem)

# Modelo lineal en función de la demanda para la Tienda 1

t1_modelos_dem <- t1_largo %>%
  group_by(t1_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(precio ~ demanda, data = .x)),  
    resumen = map(modelo, ~ tidy(.x)),
    ajuste   = map(modelo, ~ glance(.x))
  ) %>%
  mutate(
    b = map_dbl(resumen, ~ .x$estimate[.x$term == "demanda"]),
    p_valor_b = map_dbl(resumen, ~ .x$p.value[.x$term == "demanda"]),
    a = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared)
  ) %>%
  select(t1_producto, a, b, R2, p_valor_b)

print(t1_modelos_dem)

###################################################################3

# Modelo lineal en función de la demanda para la Tienda 2

t2_modelos_dem <- t2_largo %>%
  group_by(t2_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(precio ~ demanda, data = .x)),  
    resumen = map(modelo, ~ tidy(.x)),
    ajuste   = map(modelo, ~ glance(.x))
  ) %>%
  mutate(
    b = map_dbl(resumen, ~ .x$estimate[.x$term == "demanda"]),
    p_valor_b = map_dbl(resumen, ~ .x$p.value[.x$term == "demanda"]),
    a = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared)
  ) %>%
  select(t2_producto, a, b, R2, p_valor_b)

print(t2_modelos_dem)

# Modelo cuadrático para Tienda 2 en función de la demanda
t2_modelos_cuad_dem <- t2_largo %>%
  group_by(t2_producto) %>%
  nest() %>%
  mutate(
    modelo = map(data, ~ lm(precio ~ demanda + I(demanda^2), data = .x)),
    resumen = map(modelo, tidy),
    ajuste  = map(modelo, glance)
  ) %>%
  mutate(
    a = map_dbl(resumen, ~ .x$estimate[.x$term == "(Intercept)"]),
    b1 = map_dbl(resumen, ~ .x$estimate[.x$term == "demanda"]),
    b2 = map_dbl(resumen, ~ .x$estimate[.x$term == "I(demanda^2)"]),
    R2 = map_dbl(ajuste, ~ .x$r.squared),
    p_b1 = map_dbl(resumen, ~ .x$p.value[.x$term == "demanda"]),
    p_b2 = map_dbl(resumen, ~ .x$p.value[.x$term == "I(demanda^2)"])
  ) %>%
  select(t2_producto, a, b1, b2, R2, p_b1, p_b2)

print(t2_modelos_cuad_dem)

