# Consulta de afiliados: `POST /consultar_afiliado`

Consulta la afiliación de una persona utilizando el servicio SOAP del SIS. Antes de invocar el SOAP, el microservicio obtiene un
token de sesión mediante las credenciales configuradas en variables de entorno.

## Solicitud

- **Método:** `POST`
- **Cabeceras:** `Content-Type: application/json`
- **Body:**

```json
{
  "opcion": 1,
  "dni": "46118717",
  "tipo_documento": "D",
  "nro_documento": "46118717",
  "disa": null,
  "tipo_formato": null,
  "nro_contrato": null,
  "correlativo": null
}
```

| Campo            | Tipo    | Obligatorio | Descripción                                                                 |
| ---------------- | ------- | ----------- | --------------------------------------------------------------------------- |
| `opcion`         | integer | Sí          | Parámetro `intOpcion` utilizado por el SIS para distinguir el tipo de búsqueda. |
| `dni`            | string  | Sí          | DNI del responsable de la consulta.                                         |
| `tipo_documento` | string  | Sí          | Tipo de documento del afiliado (por ejemplo `D`).                           |
| `nro_documento`  | string  | Sí          | Número de documento del afiliado.                                           |
| `disa`           | string  | No          | Código DISA utilizado por el SIS.                                           |
| `tipo_formato`   | string  | No          | Tipo de formato esperado en la respuesta.                                   |
| `nro_contrato`   | string  | No          | Número de contrato si aplica.                                               |
| `correlativo`    | string  | No          | Valor correlativo para contratos vigentes.                                  |

## Respuesta exitosa

- **Código HTTP:** `200 OK`
- **Cuerpo:**

```json
{
  "data": {
    "IdError": 0,
    "Resultado": "ASEGURADO ACTIVO",
    "TipoDocumento": 1,
    "NroDocumento": "46118717",
    "ApePaterno": "PEREZ",
    "ApeMaterno": "GARCIA",
    "Nombres": "JUAN CARLOS",
    "FecAfiliacion": "2024-01-01",
    "DescTipoSeguro": "SIS GENERAL",
    "Estado": "ACTIVO"
    // ... resto de campos del modelo `Afiliado`
  },
  "status": "SUCCESS",
  "message": "Consulta realizada correctamente",
  "error_code": null,
  "description": null
}
```

Además de entregar la respuesta al cliente, SIS-MS persiste la consulta en la tabla `consulta` registrando `dni`, `estado`,
`tipo_seguro` y, en caso de error, el mensaje proporcionado por el SIS.

## Errores comunes

| Código    | HTTP          | Motivo                                                                     |
| --------- | ------------- | -------------------------------------------------------------------------- |
| `API-401` | 401           | No se pudo obtener un token de sesión válido (credenciales inválidas).     |
| `API-505` | 503           | El SIS rechazó la operación `GetSession`.                                 |
| `API-503` | 503           | No fue posible inicializar el cliente SOAP (servicio no disponible).       |
| `API-422` | 422           | El SIS respondió con `IdError != 0`; el detalle se incluye en `description`. |
| `API-504` | 503 o 500     | `ConsultarAfiliadoFuaE` devolvió un Fault o lanzó una excepción inesperada.|

> **Nota:** `API-504` representa `CustomExceptionCode.CONSULTAR_AFILIADO_FUAE_ERROR`; revisa `description` para conocer el detalle específico.
