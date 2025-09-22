from api_exception import BaseExceptionCode
from result import Err, Ok, Result
from sqlmodel import Session

from app.api.exceptions import CustomExceptionCode
from app.api.requests import ConsultaAfiliadoRequest
from app.models.afiliado import Afiliado
from app.repositories.afiliado_repository import AfiliadoRepository
from app.repositories.consulta_repository import ConsultaRepository
from tools.logger import Logger

from .sis_service import SISService

# Configurar logging
logger = Logger(__name__)


class AfiliadoService:
    """Servicio de negocio para la consulta de afiliados.

    Implementa una estrategia de caché que:
    1. Verifica si ya se consultó el afiliado hoy
    2. Si existe caché, lo retorna
    3. Si no, consulta el servicio externo
    4. Guarda/actualiza los datos y registra la consulta
    """

    def __init__(self, db_session: Session) -> None:
        """Inicializa el servicio."""
        self.db_session = db_session
        self.cache_manager = ConsultaRepository(db_session)
        self.repository = AfiliadoRepository(db_session)
        self.sis_service = SISService()

    async def consultar_afiliado(
        self, token: str, consulta: ConsultaAfiliadoRequest
    ) -> Result[Afiliado, tuple[BaseExceptionCode, int, str | None]]:
        """Consulta un afiliado utilizando estrategia de caché.

        Args:
            token: Token de autorización para el servicio externo
            consulta: Datos de la consulta (DNI, tipo documento)

        Returns:
            Afiliado si es exitoso, o error si falla

        """
        try:
            # Verificar si ya se consultó hoy
            if self.cache_manager.verificar_consulta_hoy(consulta.nro_documento):
                return await self._consultar_desde_cache(consulta)

            # Si no hay caché, consultar servicio externo
            return await self._consultar_servicio_externo(token, consulta)

        except Exception as e:
            logger.exception("Error inesperado consultando afiliado")
            return Err((CustomExceptionCode.CONSULTAR_AFILIADO_FUAE_ERROR, 500, str(e)))

    async def _consultar_desde_cache(
        self, consulta: ConsultaAfiliadoRequest
    ) -> Result[Afiliado, tuple[BaseExceptionCode, int, str | None]]:
        """Consulta un afiliado desde el caché local."""
        afiliado = self.repository.buscar_por_documento(consulta.nro_documento)
        self.cache_manager.registrar_consulta(consulta, es_local=True)
        self.db_session.commit()
        self.db_session.refresh(afiliado)
        if afiliado is None:
            return Err((CustomExceptionCode.CONSULTAR_AFILIADO_FUAE_ERROR, 404, None))
        logger.info("Datos de afiliado obtenidos desde caché")
        logger.info("Consulta registrada.")
        return Ok(afiliado)

    async def _consultar_servicio_externo(
        self, token: str, consulta: ConsultaAfiliadoRequest
    ) -> Result[Afiliado, tuple[BaseExceptionCode, int, str | None]]:
        """Consulta el servicio externo y actualiza la base de datos."""
        logger.info("Consultando servicio SIS para afiliado")

        match await self.sis_service.consultar_afiliado_fuae(token, consulta):
            case Ok(afiliado):
                afiliado_guardado = self.repository.guardar_o_actualizar(afiliado)
                self.cache_manager.registrar_consulta(consulta)

                self.db_session.commit()
                self.db_session.refresh(afiliado_guardado)
                return Ok(afiliado_guardado)

            case Err((error_code, status_code, message)):
                self.cache_manager.registrar_consulta(
                    consulta,
                    error_code=error_code.error_code,
                    error_description=error_code.message,
                )
                self.db_session.commit()
                return Err(
                    (
                        error_code,
                        status_code,
                        message,
                    )
                )
