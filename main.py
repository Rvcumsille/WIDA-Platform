from fastapi import FastAPI, HTTPException
from db import init_db, get_db
from clima_client import obtener_clima_actual
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
        db.execute("INSERT INTO predicciones (fecha, temperatura, pronostico) VALUES (?, ?, ?)",
                   (pred.fecha, pred.temperatura, pred.pronostico))
        db.commit()
        return {"mensaje": "Registro exitoso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clima/actual", response_model=PrediccionClima)
def clima_actual():
    data = obtener_clima_actual()
    return PrediccionClima(**data)