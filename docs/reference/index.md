# Referencia de la API

La API REST de SIS-MS encapsula la comunicación con el servicio SOAP del SIS y
normaliza las respuestas mediante `ResponseModel`. Todos los endpoints devuelven
el mismo contrato para facilitar el consumo por parte de clientes y manejar
errores de forma predecible.

## Formato de respuesta

```json
{
  "data": { "...": "..." },
  "status": "SUCCESS",
  "message": "Descripción corta",
  "error_code": null,
  "description": null
}
```

- `data`: carga útil principal. Puede ser `null` cuando ocurre un error.
- `status`: estado semántico (`SUCCESS`, `WARNING` o `FAIL`).
- `message`: texto breve orientado al usuario.
- `error_code`: identificador único definido en `CustomExceptionCode`.
- `description`: detalles adicionales (por ejemplo, el mensaje original del SIS).

## Endpoints disponibles

| Método | Ruta                   | Descripción |
| ------ | --------------------- | ----------- |
| GET    | `/`                   | Información general del microservicio. |
| GET    | `/health`             | Verifica conectividad con la base de datos. |
| POST   | `/login`              | Obtiene un token de sesión válido del SIS. |
| POST   | `/consultar_afiliado` | Consulta la afiliación utilizando el token SOAP. |

Las secciones siguientes describen los endpoints críticos y proporcionan
payloads de ejemplo:

- [Autenticación](autenticacion.md)
- [Consulta de afiliados](consultas.md)

## Códigos de error

`CustomExceptionCode` define los códigos y mensajes utilizados por la API. Los
más relevantes son:

| Código    | HTTP | Descripción |
| --------- | ---- | ----------- |
| `API-401` | 401  | Credenciales SOAP inválidas. |
| `API-422` | 422  | La respuesta del SIS indicó un error en la consulta. |
| `API-503` | 503  | No se pudo conectar al servicio SOAP. |
| `API-504` | 500/503 | Ocurrió un fault o excepción inesperada en `ConsultarAfiliadoFuaE`. |
| `API-505` | 503  | El SIS devolvió un fault al ejecutar `GetSession`. |

Cuando se produce un error, `status` pasa a `FAIL`, `data` es `null` y la respuesta
incluye `error_code` y `description` para facilitar el diagnóstico.
