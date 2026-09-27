from fastapi import Path, Query, FastAPI

from typing import Literal, Annotated

app = FastAPI() 

@app.get("/api/v1/reportes/{reporte_id}/evidencias")
def listar_evidencias(
    reporte_id: Annotated[int, Path(gt=0)],
    tipo: Literal["foto", "video", "enlace"] | None = None,
    orden: Literal["desc", "asc"] = "desc",
    tag: str | None = None):
    
    return {"reporte_id": reporte_id, "tipo": tipo, "orden": orden, "tag": tag}