import os
import snowflake.connector
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dashboard.predictor import predecir_ventas  # si lo necesitas
import itertools

load_dotenv()

# === CONFIGURACIÓN ===
# Sucursales que comparten clima de "Santiago,CL"
SUCURSALES_SANTIAGO = [
    {"nombre": "Santiago,CL", "sk": 1},
    {"nombre": "La Florida,CL", "sk": 5},
    {"nombre": "Las Condes,CL", "sk": 6},
    {"nombre": "Maipu,CL", "sk": 7},
    {"nombre": "Ñuñoa,CL", "sk": 8},
    {"nombre": "Providencia,CL", "sk": 9}
]

# Otras sucursales con clima propio
SUCURSALES_OTRAS = [
    {"nombre": "La Serena,CL", "sk": 2},
    {"nombre": "Puerto Montt,CL", "sk": 3},
    {"nombre": "Valdivia,CL", "sk": 4}
]


API_KEY = os.getenv("OPENWEATHER_API_KEY")
URL_BASE = "http://api.openweathermap.org/data/2.5/forecast"

def obtener_pronostico(ciudad):
    params = {
        "q": f"{ciudad},CL",
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }
    response = requests.get(URL_BASE, params=params)
    if response.status_code != 200:
        raise Exception(f"No se pudo obtener el clima para {ciudad}")
    data = response.json()

    # Agrupar por día
    predicciones = {}
    for entrada in data["list"]:
        fecha = entrada["dt_txt"].split(" ")[0]
        temp = entrada["main"]["temp"]
        temp_min = entrada["main"]["temp_min"]
        lluvia = entrada.get("rain", {}).get("3h", 0.0)

        if fecha not in predicciones:
            predicciones[fecha] = {"temps": [], "mins": [], "lluvias": []}
        predicciones[fecha]["temps"].append(temp)
        predicciones[fecha]["mins"].append(temp_min)
        predicciones[fecha]["lluvias"].append(lluvia)

    # Promediar por día
    resultados = []
    for fecha, valores in predicciones.items():
        resultados.append({
            "fecha": fecha,
            "temp_max": max(valores["temps"]),
            "temp_min": min(valores["mins"]),
            "lluvia_mm": sum(valores["lluvias"])
        })

    return resultados[:6]  # hoy + 5 días

# === CONECTAR A SNOWFLAKE ===
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database="WIDA_PLATFORM",
    schema="CURATED"
)
cur = conn.cursor()

sk_clima = 10000

# Clima de Santiago una sola vez
datos_santiago = obtener_pronostico("Santiago,CL")
for suc in SUCURSALES_SANTIAGO:
    for d in datos_santiago:
        cur.execute("""
            INSERT INTO DIM_CLIMA (SK_CLIMA, FECHA, SK_SUCURSAL, TEMP_MAX, TEMP_MIN, LLUVIA_MM)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            sk_clima,
            d["fecha"],
            suc["sk"],
            d["temp_max"],
            d["temp_min"],
            d["lluvia_mm"]
        ))
        sk_clima += 1

# Otras ciudades normalmente
for sucursal in SUCURSALES_OTRAS:
    datos = obtener_pronostico(sucursal["nombre"])
    for d in datos:
        cur.execute("""
            INSERT INTO DIM_CLIMA (SK_CLIMA, FECHA, SK_SUCURSAL, TEMP_MAX, TEMP_MIN, LLUVIA_MM)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            sk_clima,
            d["fecha"],
            sucursal["sk"],
            d["temp_max"],
            d["temp_min"],
            d["lluvia_mm"]
        ))
        sk_clima += 1

conn.commit()
cur.close()
conn.close()
print("✅ Datos del clima insertados para todas las sucursales.")

