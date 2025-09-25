# Autenticación: `POST /login`

Solicita un token de sesión válido al servicio SOAP del SIS. Este token puede
ser reutilizado por clientes que gestionen su propia cache; el endpoint
`/consultar_afiliado` solicita internamente un token usando las credenciales
configuradas en variables de entorno.

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

| Campo     | Tipo   | Obligatorio | Descripción |
| --------- | ------ | ----------- | ----------- |
| `usuario` | string | Sí          | Usuario habilitado en el servicio SOAP del SIS. |
| `clave`   | string | Sí          | Contraseña asociada al usuario SOAP. |

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

El campo `token` corresponde al valor devuelto por la operación SOAP
`GetSession`.

## Errores comunes

| Código    | HTTP | Motivo |
| --------- | ---- | ------ |
| `API-401` | 401  | Credenciales inválidas; el SIS respondió con un mensaje de error. |
| `API-422` | 500  | La respuesta del SOAP no tuvo el formato esperado (respuesta no es string). |
| `API-503` | 503  | No fue posible inicializar el cliente SOAP (`SOAP_SIS` inaccesible). |
| `API-505` | 503  | El SIS devolvió un fault durante `GetSession`. |

Cuando ocurre un error el servicio registra la excepción (`log_exception=True`)
y responde con `status = "FAIL"`, `data = null` y `description` cuando el SIS
retorna un mensaje adicional.
