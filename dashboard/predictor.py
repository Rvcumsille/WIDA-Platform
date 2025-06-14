import joblib
import numpy as np

# Cargar modelo entrenado
modelo = joblib.load("models/modelo_ventas_helados.pkl")

def predecir_ventas(temp_max_celsius: float) -> int:
    prediccion = modelo.predict(np.array([[temp_max_celsius]]))
    return int(round(prediccion[0]))
