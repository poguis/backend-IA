from urllib.parse import urlsplit, parse_qs

url = "https://tienda.com/api/v1/clientes/7/pedidos?estado=pagado&limite=10#resumen"
url2 = "https://admin:secreto@inspecciones.ejemplo.com:8080/api/v1/evidencias/15/evidencias?tipo=foto&orden=desc&tag=soldadura%20fallida#comentarios"

partes = urlsplit(url2)          # divide la URL en sus componentes

print(partes)                   # muestra el objeto completo
print("scheme:  ", partes.scheme)
print("netloc:  ", partes.netloc)
print("host:  ", partes.hostname)
print("port:  ", partes.port)
print("username:  ", partes.username)
print("passwod:  ", partes.password)
print("path:    ", partes.path)
print("query:   ", partes.query)            # texto crudo
print("params:  ", parse_qs(partes.query))  # convertido a diccionario
print(dir(partes))
print("fragment:", partes.fragment)


from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/clientes/{cliente_id}/pedidos")
def listar_pedidos(cliente_id: int, 
                   estado: str | None = None, 
                   limite: int = 10):
    return {"cliente": cliente_id, "estado": estado, "limite": limite}


from typing import Literal

@app.get("/api/v1/clientes/{cliente_id}/pedidos")
def listar_pedidos(
    cliente_id: int,
    estado: Literal["pagado", "pendiente", "anulado"] | None = None,
    limite: int = 10
):
    return {"cliente": cliente_id, "estado": estado, "limite": limite}