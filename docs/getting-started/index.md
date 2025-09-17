# Guía de inicio rápido

Esta guía explica cómo levantar SIS-MS en un entorno local para desarrollo o pruebas internas. Se asume que cuentas con acceso a
las credenciales SOAP provistas por el SIS.

## Requisitos previos

- Python 3.10 o superior.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) como gestor de dependencias.
- Docker (opcional) para levantar PostgreSQL rápidamente.
- Credenciales válidas para el servicio SOAP del SIS (`SOAP_USER`, `SOAP_PASSWORD` y la URL del WSDL expuesta en `SOAP_SIS`).

## Variables de entorno

Configura las siguientes variables antes de ejecutar el servicio:

| Variable         | Descripción                                                                                     | Valor por defecto |
| ---------------- | ----------------------------------------------------------------------------------------------- | ----------------- |
| `SOAP_SIS`       | URL del WSDL publicado por `sis.gob.pe`.                                                        | —                 |
| `SOAP_USER`      | Usuario autorizado para el método `GetSession`.                                                 | `sis_user`        |
| `SOAP_PASSWORD`  | Contraseña asociada al usuario SOAP.                                                            | `sis_password`    |
| `DB_SERVER`      | Host de PostgreSQL.                                                                             | `localhost`       |
| `DB_PORT`        | Puerto de PostgreSQL.                                                                           | `5432`            |
| `DB_NAME`        | Base de datos donde se registran las consultas.                                                 | `sis_database`    |
| `DB_USER`        | Usuario de la base de datos.                                                                    | `your_username`   |
| `DB_PASSWORD`    | Contraseña del usuario de base de datos.                                                        | `your_password`   |

> **Tip:** guarda esta configuración en un archivo `.env` y cárgala con tu gestor de procesos (por ejemplo, `direnv` o Docker Compose).

Ejemplo de archivo `.env.local`:

```bash
SOAP_SIS=https://ws.sis.gob.pe/SiSConsultasWS/Service.asmx?wsdl
SOAP_USER=usuario-demo
SOAP_PASSWORD=clave-segura
DB_SERVER=localhost
DB_PORT=5432
DB_NAME=sis_ms
DB_USER=sis_user
DB_PASSWORD=sis_password
```

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-organizacion/sis-ms.git
cd sis-ms

# Instalar dependencias (incluye dev si estás en desarrollo)
uv sync
```

## Base de datos

Levanta PostgreSQL de la forma que prefieras. Con Docker puedes usar:

```bash
docker run --name sis-db \
  -e POSTGRES_DB=sis_ms \
  -e POSTGRES_USER=sis_user \
  -e POSTGRES_PASSWORD=sis_password \
  -p 5432:5432 \
  -d postgres:16
```

Una vez configurada la conexión, aplica las migraciones iniciales:

```bash
uv run alembic upgrade head
```

## Ejecución del servicio

```bash
# Ejecutar en modo desarrollo con autoreload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API quedará disponible en `http://localhost:8000`.

- Documentación Swagger UI: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`
- Verificación rápida de estado: `http://localhost:8000/health`

## Ejecutar con Docker

El repositorio incluye un `Dockerfile` basado en la imagen oficial de Python y `uv`.

```bash
# Construir la imagen
docker build -t sis-ms .

# Ejecutar el contenedor (requiere que la base de datos sea accesible)
docker run --rm -p 8000:8000 \
  --env-file .env.local \
  sis-ms \
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Recuerda publicar el puerto de la base de datos o conectar el contenedor a la misma red que PostgreSQL.
