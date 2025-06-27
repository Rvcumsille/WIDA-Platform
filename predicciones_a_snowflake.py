import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# --- Configuración inicial ---
load_dotenv()

# Cargar productos y ventas
df_productos = pd.read_csv("Productos_DIM.csv", encoding="latin-1")
df_ventas = pd.read_csv("Datos Heladino(HECHOS_VENTAS).csv", encoding="latin-1")

# Calcular promedio de unidades vendidas por producto y sucursal
df_promedios = df_ventas.groupby(['SK_SUCURSAL', 'SK_PRODUCTO'])['UNIDADES_REALES'].mean().reset_index()
df_promedios.rename(columns={'UNIDADES_REALES': 'PROMEDIO_UNIDADES'}, inplace=True)

# Conectar a Snowflake
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database="WIDA_PLATFORM",
    schema="CURATED"
)
cur = conn.cursor()

# Obtener clima
cur.execute("SELECT SK_CLIMA, FECHA, SK_SUCURSAL, TEMP_MAX FROM DIM_CLIMA")
rows = cur.fetchall()
df_clima = pd.DataFrame(rows, columns=["SK_CLIMA", "FECHA", "SK_SUCURSAL", "TEMP_MAX"])

# Parámetros de ajuste
alpha = 0.03
ajuste_realidad = 2.78

# Generar predicciones
registros = []
for _, clima in df_clima.iterrows():
    for _, producto in df_productos.iterrows():
        sk_producto = producto["SK_PRODUCTO"]
        sk_sucursal = clima["SK_SUCURSAL"]

        # Promedio histórico
        match = df_promedios[(df_promedios["SK_PRODUCTO"] == sk_producto) &
                             (df_promedios["SK_SUCURSAL"] == sk_sucursal)]
        if not match.empty:
            base = match["PROMEDIO_UNIDADES"].values[0]
        else:
            base = 10  # default

        # Ajuste por clima
        factor_clima = 1 + alpha * (clima["TEMP_MAX"] - 20)
        unidades_pred = max(int((base * factor_clima) / ajuste_realidad), 0)

        ingreso = unidades_pred * producto["PRECIO_UNITARIO"]
        costo = unidades_pred * producto["COSTO_UNITARIO"]
        margen = ingreso - costo

        registros.append((
            clima["FECHA"],
            sk_sucursal,
            clima["SK_CLIMA"],
            sk_producto,
            unidades_pred,
            ingreso,
            costo,
            margen,
            None
        ))

# Insertar en Snowflake
insert_query = '''
    INSERT INTO HECHOS_PREDICCION (
        SK_FECHA, SK_SUCURSAL, SK_CLIMA, SK_PRODUCTO,
        UNIDADES_PREDICHAS, INGRESO_PREDICHO,
        COSTO_PREDICHO, MARGEN_PREDICHO, ERROR
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
'''
for r in registros:
    cur.execute(insert_query, r)

conn.commit()
cur.close()
conn.close()

print("✅ Predicciones ajustadas por clima y realidad de ventas insertadas correctamente.")
