from sqlmodel import Session, select

from app.models.afiliado import Afiliado
from tools.logger import Logger

# Configurar logging
logger = Logger(__name__)


class AfiliadoRepository:
    """Repositorio para operaciones CRUD de afiliados."""

    def __init__(self, db_session: Session) -> None:
        """Inicializa el repositorio."""
        self.db_session = db_session

    def buscar_por_documento(self, numero_documento: str | None) -> Afiliado | None:
        """Busca un afiliado por número y tipo de documento."""
        statement = select(Afiliado).where(Afiliado.NroDocumento == numero_documento)
        return self.db_session.exec(statement).first()

    def guardar_o_actualizar(self, afiliado_data: Afiliado) -> Afiliado:
        """Guarda un nuevo afiliado o actualiza uno existente (upsert)."""
        afiliado_existente = self.buscar_por_documento(afiliado_data.NroDocumento)

        if afiliado_existente:
            # Actualizar registro existente
            for key, value in afiliado_data.model_dump(exclude_unset=True).items():
                setattr(afiliado_existente, key, value)

            self.db_session.add(afiliado_existente)
            logger.info("Afiliado en sesion para actualizar en la base de datos")
            return afiliado_existente
        # Crear nuevo registro
        self.db_session.add(afiliado_data)
        logger.info("Nuevo afiliado en sesion para guardar en la base de datos")
        return afiliado_data
