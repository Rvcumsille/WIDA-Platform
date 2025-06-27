import streamlit as st
import requests
import pandas as pd
import sqlite3
from predictor import predecir_ventas
import altair as alt

# Configuración general de la página
st.set_page_config(page_title="Dashboard Heladino", layout="centered")
st.title("🌤️ Predicción de ventas de Heladino")

st.markdown("---")
st.header("📊 Clima actual en Santiago")

# Obtener datos del endpoint /clima/actual
try:
    response = requests.get("http://127.0.0.1:8000/clima/actual")
    if response.status_code == 200:
        data = response.json()
        
        st.metric(label="Fecha", value=data['fecha'])
        st.metric(label="Temperatura (°C)", value=data['temperatura'])
        st.metric(label="Pronóstico", value=data['pronostico'])

        col1, col2, col3 = st.columns(3)
        col1.metric(label="Humedad (%)", value=data['humedad'])
        col2.metric(label="Presión (hPa)", value=data['presion'])
        col3.metric(label="Viento (m/s)", value=data['viento'])

        col4, col5 = st.columns(2)
        col4.metric(label="Visibilidad (m)", value=data['visibilidad'])
        col5.metric(label="🌡️ Temp. Máxima (hoy °C)", value=data['temp_max'])

        # 🔮 Predicción de ventas según la temperatura máxima
        ventas_pred = predecir_ventas(data['temp_max'])
        st.markdown("### 🧁 Predicción de ventas de helados para hoy")
        st.success(f"🔮 Se estima que se venderán **{ventas_pred} helados** hoy en base a la temperatura máxima de {data['temp_max']}°C.")
    
    else:
        st.error("No se pudo obtener la predicción actual desde la API.")
except Exception as e:
    st.error(f"Error de conexión con la API: {e}")

st.markdown("---")
st.subheader("🌡️ Temperaturas máximas pronosticadas (próximos días)")

# Obtener pronóstico extendido
try:
    response_forecast = requests.get("http://127.0.0.1:8000/clima/pronostico")
    if response_forecast.status_code == 200:
        forecast_data = response_forecast.json()
        df_forecast = pd.DataFrame(forecast_data)

        from datetime import datetime

        # Convertir columna Fecha a datetime (por si viene como string)
        df_forecast["Fecha"] = pd.to_datetime(df_forecast["Fecha"]).dt.date

        # Filtrar: eliminar la predicción de hoy
        hoy = datetime.today().date()
        df_forecast = df_forecast[df_forecast["Fecha"] > hoy]

        from predictor import predecir_ventas
        df_forecast["Ventas_Predichas"] = df_forecast["Temp_Max_C"].apply(predecir_ventas)

        st.markdown("### 🔮 Predicción de ventas para los próximos días")
        st.dataframe(df_forecast)

        line_chart = alt.Chart(df_forecast).mark_line(point=True).encode(
            x=alt.X("Fecha:T", title="Fecha"),
            y=alt.Y("Ventas_Predichas:Q", title="Ventas estimadas"),
            tooltip=["Fecha", "Ventas_Predichas"]
        ).properties(
            title="Tendencia de ventas de helados (próximos días)"
        )

        st.altair_chart(line_chart, use_container_width=True)


    else:
        st.warning("No se pudo obtener el pronóstico extendido.")
except Exception as e:
    st.error(f"Error al conectar con el endpoint de pronóstico: {e}")

st.markdown("---")
st.header("📁 Registro de Predicciones Guardadas")

# Cargar predicciones desde la base de datos local SQLite
try:
    conn = sqlite3.connect("predicciones.db")
    df = pd.read_sql_query("SELECT * FROM predicciones ORDER BY fecha DESC", conn)
    st.dataframe(df)
    conn.close()
except Exception as e:
    st.warning("No hay predicciones almacenadas aún o ocurrió un error al cargarlas.")
