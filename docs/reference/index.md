# Referencia de la API

La API REST de SIS-MS expone endpoints JSON que encapsulan la comunicación con el SOAP del SIS. Todos los endpoints devuelven
instancias de `ResponseModel`, garantizando un contrato uniforme entre respuestas exitosas y fallidas.

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
- `message`: texto breve orientado a usuarios finales.
- `error_code`: código único asociado a la excepción (por ejemplo `API-401`).
- `description`: detalles adicionales o mensajes devolvidos por el SIS.

Los códigos de error se definen en `CustomExceptionCode` y cubren situaciones como credenciales inválidas, errores en el SOAP y
respuestas inválidas del servicio externo.

## Endpoints disponibles

| Método | Ruta                  | Descripción                                     |
| ------ | --------------------- | ----------------------------------------------- |
| GET    | `/`                   | Información general del microservicio.          |
| GET    | `/health`             | Verifica conectividad con la base de datos.     |
| POST   | `/login`              | Obtiene un token de sesión válido del SIS.      |
| POST   | `/consultar_afiliado` | Consulta la afiliación utilizando el token SOAP.|

Las secciones siguientes describen en detalle los endpoints críticos.

- [Autenticación](autenticacion.md)
- [Consulta de afiliados](consultas.md)
