from fastapi import FastAPI, HTTPException
from db import init_db, get_db
from clima_client import obtener_clima_actual, obtener_pronostico_maximas
from modelos import PrediccionClima, PrediccionInput

app = FastAPI()

init_db()

@app.get("/")
def root():
    return {"mensaje": "¡MVP Clima funcionando correctamente!"}

@app.post("/clima/registrar")
def registrar_prediccion(pred: PrediccionInput):
    db = get_db()
    try:
        db.execute('''INSERT INTO predicciones 
            (fecha, temperatura, pronostico, humedad, presion, viento, visibilidad, maxtemp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (pred.fecha, pred.temperatura, pred.pronostico,
            pred.humedad, pred.presion, pred.viento, pred.visibilidad, pred.temp_max))
        db.commit()
        return {"mensaje": "Registro exitoso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clima/actual", response_model=PrediccionClima)
def clima_actual():
    data = obtener_clima_actual()
    return PrediccionClima(**data)

@app.get("/clima/pronostico")
def obtener_pronostico():
    return obtener_pronostico_maximas()