import socket
import ssl

host = "untrusted-root.badssl.com"
contexto = ssl.create_default_context()   # usa las CA en las que confía tu sistema

with socket.create_connection((host, 443), timeout=5) as sock:
    with contexto.wrap_socket(sock, server_hostname=host) as tls:
        cert = tls.getpeercert()
        print("Versión TLS:", tls.version())
        print("Cifrado:    ", tls.cipher())
        print("Emitido a:  ", cert["subject"])
        print("Emisor (CA):", cert["issuer"])
        print("Expira:     ", cert["notAfter"])