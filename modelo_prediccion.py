# Cargar el dataset de entrenamiento histórico: Ice Cream Sales - temperatures
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Dataset con temperatura en °F y ganancias (USD)
df = pd.read_csv("Ice Cream Sales - temperatures (1).csv")

# Convertir la temperatura a Celsius
df["Temp_C"] = (df["Temperature"] - 32) * 5 / 9

# Asumir un precio promedio de $1.50 por helado para estimar cantidad de ventas
df["Ventas_estimadas"] = df["Ice Cream Profits"] / 1

# Entrenar modelo de regresión lineal: Temp_C → Ventas_estimadas
X = df[["Temp_C"]]
y = df["Ventas_estimadas"]

modelo = LinearRegression()
modelo.fit(X, y)

# Mostrar coeficiente e intercepto
print("Coeficiente:", modelo.coef_[0])
print("Intercepto:", modelo.intercept_)

# Guardar el modelo
joblib.dump(modelo, "models/modelo_ventas_helados.pkl")