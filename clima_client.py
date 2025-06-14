from dotenv import load_dotenv
load_dotenv()

import requests
import os
from datetime import datetime,timedelta
import pandas as pd

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CIUDAD = "Santiago,CL"

def obtener_clima_actual():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CIUDAD}&appid={API_KEY}&units=metric&lang=es"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error al obtener el clima actual")

    data = response.json()
    temperatura = data["main"]["temp"]
    pronostico = data["weather"][0]["description"].capitalize()
    fecha = datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d")
    humedad = data["main"]["humidity"]
    presion = data["main"]["pressure"]
    viento = data["wind"]["speed"]
    visibilidad = data.get("visibility", 0)
    temp_max = data["main"]["temp_max"]

    return {
        "fecha": fecha,
        "temperatura": temperatura,
        "pronostico": pronostico,
        "humedad": humedad,
        "presion": presion,
        "viento": viento,
        "visibilidad": visibilidad,
        "temp_max": temp_max
    }

def obtener_pronostico_maximas():
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={CIUDAD}&appid={API_KEY}&units=metric&lang=es"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error al obtener el pronóstico extendido")

    data = response.json()
    datos = []

    for item in data["list"]:
        # Ajustar a zona horaria local: Santiago está en UTC-4
        dt = datetime.utcfromtimestamp(item["dt"]) - timedelta(hours=4)
        fecha_local = dt.date()

        temp_max = item["main"]["temp_max"]
        datos.append({"Fecha": fecha_local, "Temp_Max_C": temp_max})

    df = pd.DataFrame(datos)
    df_max = df.groupby("Fecha", as_index=False)["Temp_Max_C"].max()
    return df_max.to_dict(orient="records")

