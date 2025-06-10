from dotenv import load_dotenv
load_dotenv()

import requests
import os
from datetime import datetime


API_KEY = os.getenv("OPENWEATHER_API_KEY")
CIUDAD = "Santiago,CL"

def obtener_clima_actual():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CIUDAD}&appid={API_KEY}&units=metric&lang=es"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error al obtener el clima")

    data = response.json()
    temperatura = data["main"]["temp"]
    pronostico = data["weather"][0]["description"].capitalize()
    fecha = datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d")

    return {
        "fecha": fecha,
        "temperatura": temperatura,
        "pronostico": pronostico
    }