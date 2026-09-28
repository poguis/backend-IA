from typing import Literal, Annotated
from fastapi import FastAPI, HTTPException, status, Response, Cookie
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
    incidente_existente = incidentes.get(incidente_id)
    if incidente_existente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    datos_actualizados = datos.model_dump()
    incidente_actualizado = incidente_existente.model_copy(update=datos_actualizados)
    incidentes[incidente_id] = incidente_actualizado
    return incidente_actualizado

@app.delete("/incidentes/{incidente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_incidente(incidente_id: int):
    incidente = incidentes.pop(incidente_id, None)
    if incidente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    return



@app.post("/sesion-demo")
def iniciar_sesion_demo(response: Response):
    response.set_cookie(
        key="usuario",
        value="carlos",
        max_age=300,        # 5 minutos
        httponly=True,
        samesite="lax",
    )
    return {"mensaje": "cookie enviada"}

@app.get("/quien-soy")
def quien_soy(usuario: Annotated[str | None, Cookie()] = None):
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="No has iniciado sesión (cookie no encontrada)"
        )
    
    # Si existe, devolvemos el valor
    return {"usuario": usuario}