from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.api.requests import ConsultaAfiliadoRequest
from app.models.consulta import Consulta


class ConsultaRepository:
    """Maneja la lógica de caché para consultas de afiliados."""

    def __init__(self, db_session: Session) -> None:
        """Inicializa el repositorio de consultas."""
        self.db_session = db_session
        self.tz = ZoneInfo("America/Lima")

    def verificar_consulta_hoy(self, numero_documento: str) -> bool:
        """Verifica si ya se realizó una consulta hoy para el DNI dado."""
        hoy = datetime.now(self.tz).date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())

        statement = select(Consulta).where(
            Consulta.numero_documento == numero_documento,
            Consulta.created_at >= inicio_dia,
            Consulta.error_code == None,
        )

        historial = self.db_session.exec(statement).first()
        return historial is not None

    def registrar_consulta(
        self,
        consulta: ConsultaAfiliadoRequest,
        *,
        es_local: bool = False,
        error_code: str | None = None,
        error_description: str | None = None,
    ) -> None:
        """Registra una nueva consulta en el historial."""
        historial_consulta = Consulta(
            numero_documento=consulta.nro_documento,
            usuario=consulta.usuario,
            es_local=es_local,
            error_code=error_code,
            error_description=error_description,
        )
        self.db_session.add(historial_consulta)
