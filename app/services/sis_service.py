import logging
import os
from functools import lru_cache

from api_exception import APIException, BaseExceptionCode
from fastapi import status
from result import Err, Ok, Result
from zeep import Client

from app.api.exceptions import CustomExceptionCode
from app.api.requests import CredencialesRequest

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
    ) -> Result[str, BaseExceptionCode]:
        """Obtener token de sesión del SIS."""
        try:
            response: str = self.client.service.GetSession(
                strUsuario=request.usuario, strClave=request.clave
            )

            error_messages = ["INVALIDO", "INCORRECTA"]
            if not isinstance(response, str):
                return Err(CustomExceptionCode.BAD_RESPONSE)

            if any(msg in response for msg in error_messages):
                self._session_token = None
                logger.info("Credenciales inválidas")
                return Err(CustomExceptionCode.INVALID_CREDENTIALS)

            return Ok(response)

        except Exception:
            logger.exception("Error en GetSession")
            return Err(CustomExceptionCode.GET_SESSION_ERROR)
