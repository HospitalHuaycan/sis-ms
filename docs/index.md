# SIS-MS

SIS-MS es un microservicio desarrollado con FastAPI que se conecta al servicio SOAP oficial del Seguro Integral de Salud (SIS) del
Perú. Expone una API REST sencilla para autenticar aplicaciones cliente y consultar la afiliación de asegurados utilizando el
método `ConsultarAfiliadoFuaE` publicado en `sis.gob.pe`. Toda la comunicación queda encapsulada en Python, por lo que los
consumidores sólo necesitan conocer contratos JSON.

## Características principales

- **Integración con SOAP** usando `zeep` para administrar sesiones y ejecutar las operaciones `GetSession` y `ConsultarAfiliadoFuaE`.
- **API REST** basada en FastAPI con documentación automática (Swagger UI y ReDoc) y middleware CORS configurable.
- **Respuestas normalizadas** mediante el paquete `api_exception`, garantizando un formato consistente para éxitos y errores.
- **Persistencia** de cada consulta en PostgreSQL con `SQLModel` y migraciones gestionadas con Alembic.
- **Estructura asíncrona** lista para despliegues productivos en Uvicorn/Gunicorn, con hooks de `lifespan` para verificar dependencias.

## Endpoints expuestos

| Método | Ruta                 | Descripción                                                                 |
| ------ | -------------------- | --------------------------------------------------------------------------- |
| GET    | `/`                  | Información básica del servicio y enlaces a la documentación generada por FastAPI. |
| GET    | `/health`            | Verifica el estado de la base de datos y del propio microservicio.          |
| POST   | `/login`             | Solicita un token de sesión del SIS a partir de credenciales SOAP válidas. |
| POST   | `/consultar_afiliado` | Consulta la afiliación de un asegurado y registra la transacción en la base de datos. |

Consulta la sección [Referencia de la API](reference/index.md) para conocer la estructura de peticiones y respuestas.

## Arquitectura en resumen

1. El cliente realiza una solicitud REST a FastAPI.
2. El servicio `SISService` solicita o reutiliza un *token* de sesión SOAP con `GetSession`.
3. Se ejecuta la operación SOAP correspondiente y la respuesta se transforma en el modelo Pydantic `Afiliado`.
4. Se registra la consulta en la tabla `consulta` mediante SQLModel y se devuelve un `ResponseModel` con la información.
5. Los errores se traducen en códigos controlados definidos en `CustomExceptionCode`.

## Persistencia

La base de datos PostgreSQL almacena el historial de solicitudes en la tabla `consulta`, con la siguiente estructura:

| Campo       | Tipo      | Descripción                                        |
| ----------- | --------- | -------------------------------------------------- |
| `id`        | `integer` | Identificador autoincremental de la consulta.      |
| `dni`       | `text`    | Documento consultado.                              |
| `error`     | `text`    | Mensaje de error devuelto por el SIS (si aplica).  |
| `estado`    | `text`    | Estado del asegurado reportado por el SIS.        |
| `tipo_seguro` | `text`  | Tipo de seguro asociado al afiliado.               |
| `created_at` | `timestamp` | Fecha y hora en la que se ejecutó la consulta. |

Las migraciones iniciales se encuentran en `app/migrations/versions` y pueden ejecutarse con Alembic.

## Próximos pasos

- Sigue la [guía de inicio](getting-started/index.md) para configurar el entorno local y levantar el microservicio.
- Revisa la [referencia de la API](reference/index.md) para integrar clientes.
- Consulta la [arquitectura](architecture/index.md) y la [operación diaria](operations/index.md) para conocer detalles internos.
