from pydantic import BaseModel

class PrediccionInput(BaseModel):
    fecha: str
    temperatura: float
    pronostico: str

class PrediccionClima(PrediccionInput):
    pass