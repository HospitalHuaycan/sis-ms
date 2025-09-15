import logging
import os
from functools import lru_cache
from typing import Any

from api.requests import ConsultaAfiliadoRequest, CredencialesRequest
from fastapi import HTTPException
from models.afiliado import Afiliado
from zeep import Client
from zeep.exceptions import Fault
from zeep.helpers import serialize_object

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@lru_cache
def get_soap_client() -> Client:
    """Crear cliente SOAP singleton para reutilizar la conexión."""
    try:
        logger.info("Cliente SOAP creado exitosamente")
        return Client(os.getenv("SOAP_SIS"))
    except Exception as e:
        logger.exception("Error al crear el cliente SOAP")
        raise HTTPException(
            status_code=500, detail=f"Error al conectar con el servicio SIS: {e!s}"
        ) from e


class SISService:
    """Clase para interactuar con el servicio SIS."""

    def __init__(self) -> None:
        """."""
        self.client = get_soap_client()
        self._session_token = None
        self._session_expires = None

    async def get_session(self, request: CredencialesRequest) -> tuple[int, Any]:
        """Obtener token de sesión del SIS."""
        try:
            response = self.client.service.GetSession(
                strUsuario=request.usuario, strClave=request.clave
            )
        except Fault as fault:
            logger.exception("SOAP Fault en GetSession")
            return 400, {  # Request Timeout
                "error": "Error SOAP",
                "detail": fault.message,
            }
        except Exception as e:
            logger.exception("Error en GetSession")
            return 500, {  # Request Timeout
                "error": "Error de Servidor",
                "detail": str(e),
            }
        else:
            status_code = 200
            response_data = response
            if "INVALIDO" in response:
                self._session_token = response
                logger.info("Sesión obtenida exitosamente")
                status_code = 422
                response_data = {
                    "error": "Error al obtener sesión",
                    "detail": response,
                }
            return status_code, response_data

    async def consultar_afiliado_fuae(
        self, autorizacion: str, consulta: ConsultaAfiliadoRequest
    ) -> tuple[int, Any]:
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
            serialized_response = serialize_object(response)

        except Fault as fault:
            logger.exception("SOAP Fault en ConsultarAfiliadoFuaE")
            return 400, {  # Request Timeout
                "error": "Error SOAP",
                "detail": fault.message,
            }
        except Exception as e:
            logger.exception("Error en ConsultarAfiliadoFuaE")
            return 500, {  # Request Timeout
                "error": "Error de Servidor",
                "detail": str(e),
            }
        else:
            status_code = 200
            response_data = Afiliado(**serialized_response)
            if response_data.IdError != 0:
                status_code = 422
                response_data = {
                    "error": "Error al obtener datos del Servicio",
                    "detail": response_data.Resultado,
                }

            return status_code, response_data
