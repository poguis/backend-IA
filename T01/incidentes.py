from typing import Literal
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class IncidenteIn(BaseModel):
    titulo: str
    severidad: Literal["baja", "media", "alta"]

class Incidente(IncidenteIn):
    id: int

incidentes: dict[int, Incidente] = {}   # "base de datos" en memoria
siguiente_id = 1

@app.post("/incidentes", status_code=status.HTTP_201_CREATED)
def crear_incidente(datos: IncidenteIn) -> Incidente:
    global siguiente_id
    incidente = Incidente(id=siguiente_id, **datos.model_dump())
    incidentes[siguiente_id] = incidente
    siguiente_id += 1
    return incidente

@app.get("/incidentes")
def listar_incidentes() -> list[Incidente]:
    return list(incidentes.values())

@app.get("/incidentes/{incidente_id}")
def obtener_incidente(incidente_id: int) -> Incidente:
    incidente = incidentes.get(incidente_id)
    if incidente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    return incidente

@app.put("/incidentes/{incidente_id}")
def actualizar_incidente(incidente_id: int, datos: IncidenteIn) -> Incidente:
    incidente = incidentes.get(incidente_id)
    if incidente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    incidente.titulo = datos.titulo
    incidente.severidad = datos.severidad
    return incidente

@app.delete("/incidentes/{incidente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_incidente(incidente_id: int):
    incidente = incidentes.pop(incidente_id, None)
    if incidente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    return