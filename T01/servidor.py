import socket
import json
import http
import traceback
from urllib.parse import urlsplit, parse_qs
from dataclasses import dataclass, field

HOST, PORT = "127.0.0.1", 8080

class PeticionInvalida(Exception):
    pass

@dataclass
class Peticion:
    metodo: str
    ruta: str
    query: dict[str, list[str]]
    version: str
    headers: dict[str, str]
    body: bytes

@dataclass
class Respuesta:
    estado: int
    cuerpo: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)

# Diccionario para separar "¿existe la ruta?" de "¿existe el método?"
RUTAS = {
    "/": ["GET"],
    "/salud": ["GET"],
    "/fallo": ["GET"],
    "/eco": ["POST"]
}

def parsear_peticion(datos: bytes) -> Peticion:
    try:
        partes = datos.split(b"\r\n\r\n", 1)
        cabeceras_crudo = partes[0].decode("latin-1")
        body = partes[1] if len(partes) > 1 else b""

        lineas = cabeceras_crudo.split("\r\n")
        metodo, url_completa, version = lineas[0].split(" ")

        parsed_url = urlsplit(url_completa)
        ruta = parsed_url.path
        query = parse_qs(parsed_url.query)

        headers = {}
        for linea in lineas[1:]:
            if ":" in linea:
                clave, valor = linea.split(":", 1)
                headers[clave.strip().lower()] = valor.strip()

        return Peticion(metodo, ruta, query, version, headers, body)
    except (ValueError, UnicodeDecodeError) as e:
        raise PeticionInvalida("Formato HTTP inválido") from e

def enrutar(peticion: Peticion) -> Respuesta:
    # 1. ¿Existe la ruta?
    if peticion.ruta not in RUTAS:
        cuerpo = json.dumps({"detail": "No encontrado"}).encode("utf-8")
        return Respuesta(404, cuerpo, {"Content-Type": "application/json"})
        
    # 2. ¿El método está permitido?
    metodos_permitidos = RUTAS[peticion.ruta]
    if peticion.metodo not in metodos_permitidos:
        cuerpo = json.dumps({"detail": "Método no permitido"}).encode("utf-8")
        # El código 405 exige el header Allow
        return Respuesta(405, cuerpo, {
            "Content-Type": "application/json",
            "Allow": ", ".join(metodos_permitidos)
        })

    # 3. Lógica por endpoint
    if peticion.ruta == "/":
        html = "<h1>Hola Mundo</h1>".encode("utf-8")
        return Respuesta(200, html, {"Content-Type": "text/html; charset=utf-8"})
        
    elif peticion.ruta == "/salud":
        cuerpo = json.dumps({"estado": "ok"}).encode("utf-8")
        return Respuesta(200, cuerpo, {"Content-Type": "application/json"})
        
    elif peticion.ruta == "/fallo":
        1 / 0
        
    elif peticion.ruta == "/eco":
        try:
            # Decodificar y validar el JSON
            cuerpo_str = peticion.body.decode("utf-8")
            datos_json = json.loads(cuerpo_str)
            
            # Reempaquetar y responder 201 Created
            cuerpo_res = json.dumps(datos_json).encode("utf-8")
            return Respuesta(201, cuerpo_res, {"Content-Type": "application/json"})
            
        except json.JSONDecodeError as e:
            raise PeticionInvalida("JSON malformado") from e
        except UnicodeDecodeError as e:
            raise PeticionInvalida("El cuerpo no es UTF-8") from e

def serializar_respuesta(respuesta: Respuesta) -> bytes:
    frase = http.HTTPStatus(respuesta.estado).phrase
    linea_estado = f"HTTP/1.1 {respuesta.estado} {frase}\r\n"

    headers = respuesta.headers.copy()
    headers["Content-Length"] = str(len(respuesta.cuerpo))
    headers["Connection"] = "close"

    headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
    bloque_texto = (linea_estado + headers_str + "\r\n").encode("latin-1")
    return bloque_texto + respuesta.cuerpo

def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"Escuchando en http://{HOST}:{PORT}")

        while True:
            conexion, direccion = servidor.accept()
            with conexion:
                ip, puerto = direccion
                metodo, ruta, version = "-", "-", "-"
                
                try:
                    datos = conexion.recv(4096)
                    if not datos:
                        continue
                    
                    peticion = parsear_peticion(datos)
                    metodo, ruta, version = peticion.metodo, peticion.ruta, peticion.version
                    
                    # Leer el resto del body si es muy grande basándose en Content-Length
                    content_length = peticion.headers.get("content-length")
                    if content_length:
                        esperado = int(content_length)
                        while len(peticion.body) < esperado:
                            chunk = conexion.recv(4096)
                            if not chunk:
                                break
                            peticion.body += chunk
                    
                    respuesta = enrutar(peticion)
                    
                except PeticionInvalida as e:
                    # Envolvemos el string del error original en JSON
                    cuerpo = json.dumps({"detail": str(e)}).encode("utf-8")
                    respuesta = Respuesta(400, cuerpo, {"Content-Type": "application/json"})
                    
                except Exception:
                    traceback.print_exc()
                    cuerpo = json.dumps({"detail": "Error interno del servidor"}).encode("utf-8")
                    respuesta = Respuesta(500, cuerpo, {"Content-Type": "application/json"})
                    
                try:
                    bytes_res = serializar_respuesta(respuesta)
                    conexion.sendall(bytes_res)
                except ConnectionError:
                    # Cubre ConnectionResetError, ConnectionAbortedError, y BrokenPipeError
                    print(f"[{ip}:{puerto}] Cliente cerró la conexión prematuramente.")
                
                print(f'{ip}:{puerto} - "{metodo} {ruta} {version}" {respuesta.estado}')

if __name__ == "__main__":
    main()