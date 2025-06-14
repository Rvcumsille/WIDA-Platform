import joblib
import numpy as np

# Cargar modelo previamente entrenado
modelo = joblib.load("models/modelo_ventas_helados.pkl")

from pydantic import BaseModel

class PrediccionInput(BaseModel):
    fecha: str
    temperatura: float
    pronostico: str
    humedad: int
    presion: int
    viento: float
    visibilidad: int
    temp_max: float

class PrediccionClima(PrediccionInput):
    pass
