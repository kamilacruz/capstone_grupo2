library(readxl)
library(tidyr)
library(dplyr)
library(MASS)         
library(fitdistrplus)
library(GGally)
library(ggplot2)
library(mclust) # clusters
library(writexl)
library(lubridate)
library(broom)

######################## MANEJO DE DATA
general <- read_excel("/Users/kamilacruz/Desktop/Universidad/Industrial/Capstone Industrial/Datos v1.xlsx", sheet = 1)

data1 <- read_excel("/Users/kamilacruz/Desktop/Universidad/Industrial/Capstone Industrial/Datos v1.xlsx", sheet = 2, skip = 5)
data2 <- read_excel("/Users/kamilacruz/Desktop/Universidad/Industrial/Capstone Industrial/Datos v1.xlsx", sheet = 3, skip = 5)

data1 <- data1[-1,]
data1 <- data1[,-1]

data2 <- data2[-1,]
data2 <- data2[,-1]

colnames(data1) <- c("fecha", "demanda1", "precio1", 
                     "demanda2", "precio2",
                     "demanda3", "precio3",
                     "demanda4", "precio4",
                     "demanda5", "precio5",
                     "demanda6", "precio6",
                     "demanda7", "precio7",
                     "demanda8", "precio8",
                     "demanda9", "precio9",
                     "demanda10", "precio10")
colnames(data2) <- c("fecha", "demanda1", "precio1", 
                     "demanda2", "precio2",
                     "demanda3", "precio3",
                     "demanda4", "precio4",
                     "demanda5", "precio5",
                     "demanda6", "precio6",
                     "demanda7", "precio7",
                     "demanda8", "precio8",
                     "demanda9", "precio9",
                     "demanda10", "precio10")
data1 <- data1 %>%
  pivot_longer(cols = -fecha, 
               names_to = c(".value", "producto"), 
               names_pattern = "([a-zA-Z]+)(\\d+)") 

colnames(data1) <- c("Fecha", "Producto", "Demanda", "Precio")
# head(data1)
data2 <- data2 %>%
  pivot_longer(cols = -fecha, 
               names_to = c(".value", "producto"), 
               names_pattern = "([a-zA-Z]+)(\\d+)") 

colnames(data2) <- c("Fecha", "Producto", "Demanda", "Precio")
# head(data2)

costo_producto <- as.numeric(general[2, 2:11])
costo_fijo <- as.numeric(general[3, 2:11])
minimo_orden <- as.numeric(general[23, 2:11])

costo_inventario <- costo_producto*0.1
## falta ver precio demanda insatisfecha!! 
## 10% de precio de venta, que fluctúa

costo_transporte <- 3.8

capacidad1 <- 175000
capacidad2 <- 163000

margen <- 0.05 #MINIMO

# diferencia precios entre 2 tiendas no debe
# ser mayor al costo de transporte


####
# exporto el excel

# write_xlsx(data1, "data1.xlsx")
# write_xlsx(data2, "data2.xlsx")
# getwd()


#### MULTIPLICO POR 1000

data1 <- data1 %>%
  mutate(
    Demanda = as.numeric(Demanda) * 1000,
    Precio = as.numeric(Precio) * 1000
  )

####
################################### VEO POSIBLES DISTRIBUCIONES
# Eliminar posibles comas, puntos innecesarios o espacios
data1$Demanda <- gsub(",", "", data1$Demanda)
data1$Demanda <- gsub(" ", "", data1$Demanda)

data1$Precio <- gsub(",", "", data1$Precio)
data1$Precio <- gsub(" ", "", data1$Precio)

data1$Demanda <- as.numeric(data1$Demanda)
data1$Precio <- as.numeric(data1$Precio)

data2$Demanda <- gsub(",", "", data2$Demanda)
data2$Demanda <- gsub(" ", "", data2$Demanda)

data2$Precio <- gsub(",", "", data2$Precio)
data2$Precio <- gsub(" ", "", data2$Precio)

data2$Demanda <- as.numeric(data2$Demanda)
data2$Precio <- as.numeric(data2$Precio)

########
######
###### 

data1$Fecha <- as.Date(data1$Fecha)
data1$Semana <- as.numeric(format(data1$Fecha, "%U")) + 1
data1$Año <- as.numeric(format(data1$Fecha, "%Y"))

regresion_total <- data1 %>%
  group_by(Producto) %>%
  group_modify(~ tidy(lm(Demanda ~ Precio, data = .x))) %>%
  ungroup()

regresion_total <- regresion_total %>%
  filter(term %in% c("(Intercept)", "Precio")) %>%
  pivot_wider(
    id_cols = Producto,
    names_from = term,
    values_from = c(estimate, p.value),
    names_glue = "{.value}_{term}"
  ) %>%
  rename(
    a = `estimate_(Intercept)`,
    b = `estimate_Precio`,
    p_value_b = `p.value_Precio`
  )




regresion_total2 <- data2 %>%
  group_by(Producto) %>%
  group_modify(~ tidy(lm(Demanda ~ Precio, data = .x))) %>%
  ungroup()

regresion_total2 <- regresion_total2 %>%
  filter(term %in% c("(Intercept)", "Precio")) %>%
  pivot_wider(
    id_cols = Producto,
    names_from = term,
    values_from = c(estimate, p.value),
    names_glue = "{.value}_{term}"
  ) %>%
  rename(
    a = `estimate_(Intercept)`,
    b = `estimate_Precio`,
    p_value_b = `p.value_Precio`
  )


######### tienda 1
data1020 <- data1 %>%
  filter(Semana %in% c(10, 20))

regresion1020 <- data1020 %>%
  group_by(Producto) %>%
  group_modify(~ tidy(lm(Demanda ~ Precio, data = .x))) %>%
  ungroup()

regresion_ab_t1 <- regresion1020 %>%
  filter(term %in% c("(Intercept)", "Precio")) %>%
  pivot_wider(
    id_cols = Producto,
    names_from = term,
    values_from = c(estimate, p.value),
    names_glue = "{.value}_{term}"
  ) %>%
  rename(
    a = `estimate_(Intercept)`,
    b = `estimate_Precio`,
    p_value_b = `p.value_Precio`
  )

write_xlsx(regresion_ab_t1, "regresion_t1.xlsx")
getwd()
####### tienda 2

data2$Fecha <- as.Date(data2$Fecha)
data2$Semana <- as.numeric(format(data2$Fecha, "%U")) + 1
data2$Año <- as.numeric(format(data2$Fecha, "%Y"))

data1020_t2 <- data2 %>%
  filter(Semana %in% c(10, 20))

regresion1020_t2 <- data1020_t2 %>%
  group_by(Producto) %>%
  group_modify(~ tidy(lm(Demanda ~ Precio, data = .x))) %>%
  ungroup()

regresion_ab_t2 <- regresion1020_t2 %>%
  filter(term %in% c("(Intercept)", "Precio")) %>%
  pivot_wider(
    id_cols = Producto,
    names_from = term,
    values_from = c(estimate, p.value),
    names_glue = "{.value}_{term}"
  ) %>%
  rename(
    a = `estimate_(Intercept)`,
    b = `estimate_Precio`,
    p_value_b = `p.value_Precio`
  )

write_xlsx(regresion_ab_t2, "regresion_tie2.xlsx")
getwd()


########## PARA X E Y SEMANAS

semanas_xy1 <- function(data1, semanas, nombre_archivo) {
  data_filtrada1 <- data1 %>%
    filter(Semana %in% semanas)
  
  modelo_xy1 <- data_filtrada1 %>%
    group_by(Producto) %>%
    group_modify(~ tidy(lm(Demanda ~ Precio, data = .x))) %>%
    ungroup()
  
  regresion_ab1 <- modelo_xy %>%
    filter(term %in% c("(Intercept)", "Precio")) %>%
    pivot_wider(
      id_cols = Producto,
      names_from = term,
      values_from = c(estimate, p.value),
      names_glue = "{.value}_{term}"
    ) %>%
    rename(
      a = `estimate_(Intercept)`,
      b = `estimate_Precio`,
      p_value_b = `p.value_Precio`
    )
  
  write.csv(regresion_ab, nombre_archivo, row.names = FALSE)
  message("Archivo guardado como: ", nombre_archivo)
}


###### GRAFICOS
regresion_ab_t1$Tienda <- "Tienda 1"
regresion_ab_t2$Tienda <- "Tienda 2"

regresion_general <- bind_rows(regresion_ab_t1, regresion_ab_t2)

ggplot(regresion_general, aes(x = factor(Producto), y = a, fill = Tienda)) +
  geom_col(position = "dodge") +
  labs(title = "A por Producto y Tienda",
       x = "Producto", y = "A") +
  theme(axis.text.y = element_text(angle = 45, hjust = 1))
  theme_minimal()

ggplot(regresion_general, aes(x = factor(Producto), y = b, fill = Tienda)) +
  geom_col(position = "dodge") +
  labs(title = "B por Producto y Tienda",
       x = "Producto", y = "B") +
  theme_minimal()

regresion_total$Tienda <- "Tienda 1"
regresion_total2$Tienda <- "Tienda 2"

regresion_general2 <- bind_rows(regresion_total, regresion_total2)

ggplot(regresion_general2, aes(x = factor(Producto), y = a, fill = Tienda)) +
  geom_col(position = "dodge") +
  labs(title = "A por Producto y Tienda",
       x = "Producto", y = "A") +
  theme(axis.text.y = element_text(angle = 45, hjust = 1))
theme_minimal()

ggplot(regresion_general2, aes(x = factor(Producto), y = b, fill = Tienda)) +
  geom_col(position = "dodge") +
  labs(title = "B por Producto y Tienda",
       x = "Producto", y = "B") +
  theme_minimal()

