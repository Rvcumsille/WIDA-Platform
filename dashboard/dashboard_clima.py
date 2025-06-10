import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Dashboard Clima - MVP", layout="centered")
st.title("🌤️ Dashboard Clima - WIDA Platform")

st.markdown("---")

st.header("📊 Clima actual en Snatiago")

# Obtener datos del endpoint /clima/actual
try:
    response = requests.get("http://127.0.0.1:8000/clima/actual")
    if response.status_code == 200:
        data = response.json()
        st.metric(label="Fecha", value=data['fecha'])
        st.metric(label="Temperatura (°C)", value=data['temperatura'])
        st.metric(label="Pronóstico", value=data['pronostico'])
    else:
        st.error("No se pudo obtener la predicción actual.")
except Exception as e:
    st.error(f"Error de conexión con la API: {e}")

st.markdown("---")

st.header("📁 Registro de Predicciones Guardadas")

# Cargar predicciones desde SQLite
import sqlite3
conn = sqlite3.connect("predicciones.db")
try:
    df = pd.read_sql_query("SELECT * FROM predicciones ORDER BY fecha DESC", conn)
    st.dataframe(df)
except Exception as e:
    st.warning("No hay predicciones almacenadas aún o ocurrió un error al cargarlas.")

conn.close()