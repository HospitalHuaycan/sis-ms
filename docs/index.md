# SIS-MS

SIS-MS es un microservicio escrito en FastAPI que abstrae la interacción con el
servicio SOAP oficial del Seguro Integral de Salud (SIS) del Perú. Expone
endpoints REST para autenticarse, consultar el estado de afiliación y registrar
cada transacción en PostgreSQL para efectos de trazabilidad y auditoría.

La aplicación está pensada para ejecutarse como un servicio independiente y
formar parte de arquitecturas orientadas a microservicios. El proyecto incluye
herramientas de calidad de código, scripts de base de datos y documentación
basada en MkDocs Material.

## Características principales

- **Integración con SOAP** mediante [`zeep`](https://docs.python-zeep.org/) para
  invocar los métodos `GetSession` y `ConsultarAfiliadoFuaE` del SIS, con
  serialización automática de respuestas.
- **API REST asincrónica** construida con FastAPI. Incluye documentación
  interactiva (Swagger UI y ReDoc), middleware CORS configurable y *lifespan*
  para validar dependencias al arranque.
- **Manejo uniforme de errores** gracias al paquete
  [`api_exception`](https://pypi.org/project/api-exception/). Todas las
  respuestas siguen la estructura `ResponseModel` y utilizan códigos declarados
  en `CustomExceptionCode`.
- **Persistencia de consultas** en PostgreSQL usando `SQLModel` y migraciones
  administradas por Alembic. Cada petición queda registrada con metadatos y
  marcas de error.
- **Estrategia de caché** en `AfiliadoService`: si el documento ya fue consultado
  el mismo día, la respuesta se atiende desde la base de datos y se vuelve a
  registrar la consulta como local.

## Endpoints expuestos

| Método | Ruta                   | Descripción                                                                 |
| ------ | ---------------------- | --------------------------------------------------------------------------- |
| GET    | `/`                    | Información básica del servicio y enlaces a las UI generadas por FastAPI.  |
| GET    | `/health`              | Verifica conectividad con PostgreSQL a través de `DatabaseConfig.test_connection()`. |
| POST   | `/login`               | Solicita un token de sesión del SIS usando las credenciales recibidas.      |
| POST   | `/consultar_afiliado`  | Consulta el afiliado mediante SOAP, aplica caché y registra la transacción. |

La [Referencia de la API](reference/index.md) detalla el contrato de peticiones
y respuestas, incluyendo códigos de error y ejemplos completos.

## Componentes destacados

| Componente                       | Ubicación                              | Descripción breve |
| -------------------------------- | -------------------------------------- | ----------------- |
| Aplicación FastAPI               | `app/main.py`                          | Define endpoints, ciclo de vida y middleware de CORS. |
| Modelos de entrada               | `app/api/requests.py`                  | Esquemas Pydantic utilizados para validar payloads JSON. |
| Servicio SOAP                    | `app/services/sis_service.py`          | Encapsula llamadas al SIS y transforma las respuestas SOAP. |
| Servicio de afiliados            | `app/services/afiliado_service.py`     | Orquesta caché, invocaciones SOAP y registro histórico. |
| Repositorios                     | `app/repositories/`                    | Acceso a datos para `Afiliado` y `Consulta`. |
| Configuración de base de datos   | `app/database.py`                      | Gestiona la conexión PostgreSQL y expone sesiones reutilizables. |
| Modelos persistentes             | `app/models/afiliado.py`, `app/models/consulta.py` | Esquemas `SQLModel` que representan tablas del dominio. |

## Persistencia y registro histórico

El modelo `Consulta` guarda cada solicitud ejecutada, independientemente del
resultado. Los campos disponibles son:

| Campo              | Tipo        | Descripción |
| ------------------ | ----------- | ----------- |
| `id`               | `integer`   | Identificador autoincremental. |
| `numero_documento` | `text`      | Documento consultado (`ConsultaAfiliadoRequest.nro_documento`). |
| `usuario`          | `text`      | Usuario responsable registrado en la petición. |
| `es_local`         | `boolean`   | Indica si la respuesta provino de caché local. |
| `error_code`       | `text`      | Código de error retornado por el servicio, en caso de falla. |
| `error_description`| `text`      | Descripción asociada al código de error, si existe. |
| `created_at`       | `timestamp` | Fecha y hora en la que se registró la consulta. |

`Afiliado` almacena la última versión conocida del asegurado utilizando un
esquema amplio que replica los campos devueltos por `ConsultarAfiliadoFuaE`.
`AfiliadoRepository.guardar_o_actualizar` realiza un *upsert* basándose en el
número de documento.

## Flujo resumido

1. El cliente realiza una solicitud HTTP hacia FastAPI.
2. `SISService` obtiene (o valida) el token de sesión SOAP.
3. Se invoca `ConsultarAfiliadoFuaE` y se traduce el resultado a `Afiliado`.
4. `AfiliadoService` decide si usar caché o actualizar la información persistente.
5. Se crea un registro en `Consulta` con el resultado y se responde mediante
   `ResponseModel`.

Para un detalle más profundo consulta la sección de [Arquitectura](architecture/index.md).

## Próximos pasos

- Sigue la [guía de inicio rápido](getting-started/index.md) para preparar el
  entorno local y ejecutar las migraciones iniciales.
- Revisa la [referencia de la API](reference/index.md) antes de integrar
  consumidores externos.
- Consulta la sección de [Operaciones](operations/index.md) para conocer tareas
  recurrentes, monitoreo y lineamientos de seguridad.
