# Autenticación: `POST /login`

Solicita un token de sesión válido al servicio SOAP del SIS. Este token es obligatorio para consumir el endpoint
`/consultar_afiliado`.

## Solicitud

- **Método:** `POST`
- **Cabeceras:** `Content-Type: application/json`
- **Body:**

```json
{
  "usuario": "string",
  "clave": "string"
}
```

| Campo    | Tipo   | Obligatorio | Descripción                                               |
| -------- | ------ | ----------- | --------------------------------------------------------- |
| `usuario`| string | Sí          | Usuario habilitado en el servicio SOAP del SIS.           |
| `clave`  | string | Sí          | Contraseña asociada al usuario SOAP.                      |

## Respuesta exitosa

- **Código HTTP:** `200 OK`
- **Cuerpo:**

```json
{
  "data": {
    "token": "abc123"
  },
  "status": "SUCCESS",
  "message": "Sesión obtenida exitosamente",
  "error_code": null,
  "description": null
}
```

El campo `token` corresponde al valor devuelto por la operación SOAP `GetSession`.

## Errores comunes

| Código | HTTP | Motivo                                                    |
| ------ | ---- | --------------------------------------------------------- |
| `API-401` | 401 | Credenciales inválidas o vencidas.                       |
| `API-503` | 503 | No fue posible conectarse al servicio SOAP del SIS.      |
| `API-505` | 503 | El SOAP devolvió un fault inesperado en `GetSession`.    |
| `API-422` | 500 | La respuesta del SOAP no tuvo el formato esperado.       |

En caso de error se devuelve `status = "FAIL"`, `data = null` y `description` puede incluir el mensaje original del SIS.
