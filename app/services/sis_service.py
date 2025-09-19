import logging
import os
from functools import lru_cache

from api_exception import APIException, BaseExceptionCode
from fastapi import status
from result import Err, Ok, Result
from zeep import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

from app.api.exceptions import CustomExceptionCode
from app.api.requests import ConsultaAfiliadoRequest, CredencialesRequest
from app.models.afiliado import Afiliado

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@lru_cache
def get_soap_client() -> Client:
    """Crear cliente SOAP singleton para reutilizar la conexión."""
    try:
        return Client(os.getenv("SOAP_SIS"))
    except Exception as e:
        raise APIException(
            error_code=CustomExceptionCode.DISCONECTED_SIS_SERVICE,
            http_status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            log_exception=True,
        ) from e


class SISService:
    """Clase para interactuar con el servicio SIS."""

    def __init__(self) -> None:
        """."""
        self.client = get_soap_client()
        self._session_token = None
        self._session_expires = None

    async def get_session(
        self, request: CredencialesRequest
    ) -> Result[str, tuple[BaseExceptionCode, int]]:
        """Obtener token de sesión del SIS."""
        try:
            response: str = self.client.service.GetSession(
                strUsuario=request.usuario, strClave=request.clave
            )
            # TODO(davidreygu): Falta validar mas errores. Ver ticket #1
            error_messages = ["INVALIDO", "INCORRECTA"]
            if not isinstance(response, str):
                return Err(
                    (
                        CustomExceptionCode.BAD_RESPONSE,
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                )

            if any(msg in response for msg in error_messages):
                self._session_token = None
                logger.info("Credenciales inválidas")
                return Err(
                    (
                        CustomExceptionCode.INVALID_CREDENTIALS,
                        status.HTTP_401_UNAUTHORIZED,
                    )
                )

            return Ok(response)

        except Exception:
            logger.exception("Error en GetSession")
            return Err(
                (
                    CustomExceptionCode.GET_SESSION_ERROR,
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            )

    async def consultar_afiliado_fuae(
        self, autorizacion: str, consulta: ConsultaAfiliadoRequest
    ) -> Result[Afiliado, tuple[BaseExceptionCode, int, str | None]]:
        """Consultar afiliado FuaE."""
        try:
            # Realizar la consulta
            response = self.client.service.ConsultarAfiliadoFuaE(
                intOpcion=consulta.opcion,
                strAutorizacion=autorizacion,
                strDni=consulta.dni,
                strTipoDocumento=consulta.tipo_documento,
                strNroDocumento=consulta.nro_documento,
                strDisa=consulta.disa,
                strTipoFormato=consulta.tipo_formato,
                strNroContrato=consulta.nro_contrato,
                strCorrelativo=consulta.correlativo,
            )
            response_data = Afiliado(**serialize_object(response))
            # Convertir respuesta a modelo Pydantic
            if response_data.IdError == 0:
                return Err(
                    (
                        CustomExceptionCode.BAD_RESPONSE,
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        response_data.Resultado,
                    )
                )

            return Ok(response_data)

        except Fault as fault:
            return Err(
                (
                    CustomExceptionCode.CONSULTAR_AFILIADO_FUAE_ERROR,
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    fault.message,
                )
            )
        except Exception as e:
            return Err(
                (
                    CustomExceptionCode.CONSULTAR_AFILIADO_FUAE_ERROR,
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    str(e),
                )
            )
