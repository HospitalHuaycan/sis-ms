# Consulta de afiliados: `POST /consultar_afiliado`

Consulta la afiliación de una persona utilizando el servicio SOAP del SIS. Antes
de invocar el SOAP, el microservicio obtiene un token de sesión con las
credenciales almacenadas en variables de entorno (`SOAP_USER`, `SOAP_PASSWORD`).

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
  "correlativo": null,
  "usuario": "operador-app"
}
```

| Campo            | Tipo    | Obligatorio | Descripción |
| ---------------- | ------- | ----------- | ----------- |
| `opcion`         | integer | Sí          | Parámetro `intOpcion` utilizado por el SIS para distinguir el tipo de búsqueda. |
| `dni`            | string  | Sí          | DNI del responsable de la consulta (para trazabilidad). |
| `tipo_documento` | string  | Sí          | Tipo de documento del afiliado (por ejemplo `D`). |
| `nro_documento`  | string  | Sí          | Número de documento del afiliado. |
| `disa`           | string  | No          | Código DISA utilizado por el SIS. |
| `tipo_formato`   | string  | No          | Tipo de formato esperado en la respuesta. |
| `nro_contrato`   | string  | No          | Número de contrato si aplica. |
| `correlativo`    | string  | No          | Valor correlativo para contratos vigentes. |
| `usuario`        | string  | Sí          | Usuario o sistema que ejecuta la consulta; se almacena en el historial. |

## Respuesta exitosa

- **Código HTTP:** `200 OK`
- **Cuerpo:**

```json
{
  "data": {
    "IdError": "0",
    "Resultado": "ASEGURADO ACTIVO",
    "TipoDocumento": "D",
    "NroDocumento": "46118717",
    "ApePaterno": "PEREZ",
    "ApeMaterno": "GARCIA",
    "Nombres": "JUAN CARLOS",
    "FecAfiliacion": "2024-01-01",
    "DescTipoSeguro": "SIS GENERAL",
    "Estado": "ACTIVO",
    "...": "Otros campos disponibles en app/models/afiliado.py"
  },
  "status": "SUCCESS",
  "message": "Consulta realizada correctamente",
  "error_code": null,
  "description": null
}
```

Además de entregar la respuesta al cliente:

1. `AfiliadoRepository` guarda o actualiza el registro del afiliado.
2. `ConsultaRepository` crea un historial con `numero_documento`, `usuario`,
   `es_local` y posibles códigos de error.
3. Si el documento ya fue consultado durante el día, la respuesta proviene del
   caché local (`es_local = True`).

## Errores comunes

| Código    | HTTP          | Motivo |
| --------- | ------------- | ------ |
| `API-401` | 401           | No se pudo obtener un token de sesión válido (credenciales inválidas). |
| `API-422` | 422           | El SIS respondió con `IdError != 0`; el detalle se incluye en `description`. |
| `API-503` | 503           | No fue posible inicializar o contactar el servicio SOAP. |
| `API-504` | 503 o 500     | `ConsultarAfiliadoFuaE` devolvió un fault o lanzó una excepción inesperada. |

Revisa `error_description` en el historial de la tabla `consulta` para conocer el
mensaje devuelto por el SIS cuando se produce una falla.
