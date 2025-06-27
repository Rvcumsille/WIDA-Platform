import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from math import sqrt


df = pd.read_csv("Datos_combinados_para_entrenamiento.csv")

# Selección de columnas relevantes
columnas_usadas = ["PRECIO_UNITARIO", "TEMP_MAX", "UNIDADES_REALES"]
if not all(col in df.columns for col in columnas_usadas):
    raise ValueError("❌ Faltan columnas requeridas para el entrenamiento.")

df = df[columnas_usadas].dropna()

X = df[["PRECIO_UNITARIO", "TEMP_MAX"]]
y = df["UNIDADES_REALES"]

# División entre entrenamiento y validación
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


print("🤖 Entrenando modelo de regresión lineal...")

modelo = LinearRegression()
modelo.fit(X_train, y_train)


y_pred = modelo.predict(X_test)
rmse = sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n📊 Resultados del modelo:")
print(f"Coeficientes: {modelo.coef_}")
print(f"Intercepto: {modelo.intercept_}")
print(f"RMSE (Error cuadrático medio): {rmse:.2f}")
print(f"R² (Coeficiente de determinación): {r2:.2f}")


ruta_modelo = "models/modelo_ventas_helados_entrenado.pkl"
joblib.dump(modelo, ruta_modelo)
print(f"\n✅ Modelo guardado correctamente en: {ruta_modelo}")
