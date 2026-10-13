Paso 1: instalar Ubuntu
En PowerShell:
wsl --list --online

Debe listar las distribuciones disponibles. Luego instala Ubuntu:
wsl --install -d Ubuntu

wsl --set-default Ubuntu
wsl -l -v

PASO 2: ENTRAR
wsl -d Ubuntu