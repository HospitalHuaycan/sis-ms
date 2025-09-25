# Guía de inicio rápido

Esta guía explica cómo preparar un entorno local de desarrollo o pruebas para
SIS-MS. Se asume que cuentas con credenciales válidas del SIS y acceso a un
servidor PostgreSQL.

## Requisitos previos

- Python 3.10 o superior.
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) como gestor de
  dependencias y ejecución.
- PostgreSQL 13 o superior (local, en contenedor o administrado).
- Credenciales SOAP (`SOAP_SIS`, `SOAP_USER`, `SOAP_PASSWORD`).
- Opcional: Docker para levantar servicios auxiliares rápidamente.

## Configuración de variables de entorno

Define las variables que utiliza `DatabaseConfig` y `SISService`. Puedes
almacenarlas en `.env.local` y reutilizarlas tanto para ejecución local como
para contenedores.

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

> 💡 El código también acepta `DB_HOST`; si ambos (`DB_HOST` y `DB_SERVER`) están
> definidos, `DB_HOST` tiene prioridad.

Carga este archivo con tu gestor preferido (`direnv`, `doppler`, `docker compose`
o exportando las variables en la terminal).

## Instalación del proyecto

```bash
# Clonar el repositorio
git clone https://github.com/tu-organizacion/sis-ms.git
cd sis-ms

# Instalar dependencias (incluye extras de desarrollo)
uv sync
```

`uv` creará un entorno aislado en `.venv` (o en el directorio global configurado)
y resolverá las dependencias definidas en `pyproject.toml`.

## Base de datos y migraciones

Levanta PostgreSQL en tu entorno. Con Docker puedes iniciar un contenedor
mínimo ejecutando:

```bash
docker run --name sis-db \
  -e POSTGRES_DB=sis_ms \
  -e POSTGRES_USER=sis_user \
  -e POSTGRES_PASSWORD=sis_password \
  -p 5432:5432 \
  -d postgres:16
```

Aplica las migraciones iniciales con Alembic (utiliza la configuración de
`DatabaseConfig`):

```bash
uv run alembic upgrade head
```

Si la conexión es correcta verás en la base de datos las tablas `consulta` y
`afiliado` generadas a partir de los modelos `SQLModel`.

## Ejecutar el servicio en modo desarrollo

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Documentación interactiva: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Chequeo de salud: <http://localhost:8000/health>

`lifespan` realiza una prueba de conexión a PostgreSQL durante el arranque y
cierra el motor al finalizar la ejecución.

## Pruebas y calidad

Antes de publicar cambios ejecuta los siguientes comandos:

```bash
uv run pytest              # Pruebas unitarias
uv run ruff check .        # Linter
uv run ruff format .       # Formateo automático
uv run pyright             # Análisis estático de tipos
```

## Documentación

La documentación pública se genera con MkDocs Material. Para editarla y
visualizar cambios en caliente:

```bash
uv run mkdocs serve -a 0.0.0.0:8001
```

Para producir el sitio estático listo para despliegue:

```bash
uv run mkdocs build
```

## Limpieza

Cuando termines, puedes detener los contenedores auxiliares y borrar el entorno
virtual si lo deseas:

```bash
docker stop sis-db && docker rm sis-db
uv env remove  # elimina el entorno administrado por uv
```

Deja el repositorio con un `git status` limpio antes de abrir *pull requests*.
