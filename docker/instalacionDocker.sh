#!/bin/bash

# Crear el directorio si no existe
mkdir -p ~/.docker/cli-plugins/

# Descargar Docker Compose desde el repositorio oficial de GitHub
curl -SL https://github.com/docker/compose/releases/download/v2.3.3/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose

# Dar permisos de ejecución al comando docker compose
chmod +x ~/.docker/cli-plugins/docker-compose

# Verificar la instalación
docker compose version
