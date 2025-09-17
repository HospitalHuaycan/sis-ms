from api_exception import BaseExceptionCode


class CustomExceptionCode(BaseExceptionCode):
    """Excepciones personalizadas para el API."""

    CONSULTAR_AFILIADO_FUAE_ERROR = (
        "API-504",
        "SOAP Fault en ConsultarAfiliadoFuaE",
        "Error al consultar afiliado",
    )
    GET_SESSION_ERROR = (
        "API-505",
        "SOAP Fault en GetSession.",
        "Error al conectar con el servicio SIS.",
    )
    DISCONECTED_SIS_SERVICE = (
        "API-503",
        "Error al conectar con el servicio SIS.",
        "Porfavor intente mas tarde.",
    )
    BAD_RESPONSE = (
        "API-422",
        "Respuesta del servicio invalida.",
        "Porfavor intente mas tarde.",
    )
    INVALID_CREDENTIALS = (
        "API-401",
        "Credenciales inválidas",
        "Porfavor intente mas tarde.",
    )
    PERMISSION_DENIED = (
        "PERM-403",
        "Permission denied.",
        "Access to this resource is forbidden.",
    )
