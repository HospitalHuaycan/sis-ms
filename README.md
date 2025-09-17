# SIS-MS

SIS-MS es un microservicio construido con FastAPI para consultar el estado de afiliación de asegurados en el Seguro Integral de
Salud (SIS) del Perú. El servicio encapsula la integración con el SOAP oficial de `sis.gob.pe`, entrega respuestas JSON
estandarizadas y registra cada consulta en PostgreSQL para auditoría.

## Características clave

- Integración con los métodos SOAP `GetSession` y `ConsultarAfiliadoFuaE` mediante la librería `zeep`.
- API REST asincrónica basada en FastAPI, con documentación automática (`/docs`, `/redoc`).
- Manejo uniforme de errores y respuestas usando el paquete [`api_exception`](https://pypi.org/project/api-exception/).
- Persistencia del historial de consultas con `SQLModel` y migraciones gestionadas por Alembic.
- Preparado para despliegues en Docker o servidores ASGI (Uvicorn/Gunicorn).

## Arquitectura

```
[Cliente REST] --> [FastAPI] --> [Servicio SOAP SIS]
                      |              ^
                      |              |
                      +--> [PostgreSQL]
```

1. FastAPI recibe la solicitud y valida el payload con Pydantic.
2. `SISService` obtiene (o reutiliza) el token de sesión SOAP y ejecuta la operación correspondiente.
3. La respuesta se transforma en el modelo `Afiliado` y se devuelve dentro de un `ResponseModel`.
4. El resultado (éxito o error) se almacena en la tabla `consulta` para trazabilidad.

## Requisitos

- Python 3.10 o superior.
- [uv](https://docs.astral.sh/uv/) para instalar dependencias.
- PostgreSQL 13+.
- Credenciales válidas del servicio SOAP del SIS.

## Variables de entorno

| Variable        | Descripción                                                   | Valor por defecto |
| --------------- | ------------------------------------------------------------- | ----------------- |
| `SOAP_SIS`      | URL del WSDL del SIS.                                         | —                 |
| `SOAP_USER`     | Usuario habilitado para `GetSession`.                          | `sis_user`        |
| `SOAP_PASSWORD` | Contraseña asociada al usuario SOAP.                           | `sis_password`    |
| `DB_SERVER`     | Host de PostgreSQL.                                            | `localhost`       |
| `DB_PORT`       | Puerto de PostgreSQL.                                          | `5432`            |
| `DB_NAME`       | Nombre de la base de datos.                                    | `sis_database`    |
| `DB_USER`       | Usuario de base de datos.                                      | `your_username`   |
| `DB_PASSWORD`   | Contraseña del usuario de base de datos.                       | `your_password`   |

Guarda estos valores en un archivo `.env.local` y cárgalo antes de iniciar el servicio.

## Instalación y ejecución local

```bash
git clone https://github.com/tu-organizacion/sis-ms.git
cd sis-ms
uv sync            # instala dependencias
uv run alembic upgrade head  # crea la tabla consulta
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`.

## Endpoints principales

| Método | Ruta                  | Descripción                                       |
| ------ | --------------------- | ------------------------------------------------- |
| GET    | `/`                   | Información del microservicio y rutas útiles.     |
| GET    | `/health`             | Verifica conectividad con la base de datos.       |
| POST   | `/login`              | Solicita un token de sesión del SIS.              |
| POST   | `/consultar_afiliado` | Consulta la afiliación y registra la transacción. |

Consulta la [referencia completa de la API](docs/reference/index.md) para ejemplos detallados.

## Comandos útiles

```bash
uv run pytest                # pruebas unitarias
uv run ruff check .          # linter
uv run ruff format .         # formateo automático
uv run pyright               # análisis estático
uv run mkdocs serve          # previsualizar la documentación
```

## Docker

```bash
docker build -t sis-ms .
docker run --rm -p 8000:8000 --env-file .env.local sis-ms \
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Asegúrate de exponer la base de datos al contenedor o conectarlos mediante una red interna.

## Documentación

La documentación técnica se genera con MkDocs Material. Para verla localmente:

```bash
uv run mkdocs serve -a 0.0.0.0:8001
```

Para desplegarla:

```bash
uv run mkdocs build
```

## Licencia

Este proyecto se distribuye bajo los términos de la licencia [MIT](LICENSE).
