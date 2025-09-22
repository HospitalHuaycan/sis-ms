import os
import urllib.parse
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlmodel import Session, create_engine, select, text

from tools.logger import Logger

# Configurar logging
logger = Logger(__name__)


class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos."""

    def __init__(self, message: str) -> None:
        """Inicializar la excepción con un mensaje personalizado."""
        super().__init__(f" error de configuracion de base de datos: {message}")


class DatabaseConfig:
    """Configuración avanzada de conexión a la base de datos PostgreSQL."""

    def __init__(
        self,
    ) -> None:
        """Inicializar la configuración de conexión a PostgreSQL.

        Args:
            host: Servidor de base de datos
            port: Puerto de conexión
            database: Nombre de la base de datos
            username: Usuario de base de datos
            password: Contraseña de base de datos
            echo: Si mostrar las consultas SQL en logs
            pool_size: Tamaño del pool de conexiones
            max_overflow: Conexiones adicionales máximas
            pool_timeout: Tiempo de espera para obtener conexión
            pool_recycle: Tiempo para reciclar conexiones (segundos)
            pool_pre_ping: Verificar conexiones antes de usarlas

        """
        # Configuración de conexión
        self.host = os.getenv("DB_HOST", os.getenv("DB_SERVER", "localhost"))
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "sis_database")
        self.username = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")

        # Configuración del motor
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.pool_size = 10
        self.max_overflow = 20
        self.pool_timeout = 30
        self.pool_recycle = 3600
        self.pool_pre_ping = True

        # Validar configuración
        self._validate_config()

        # Construir la URL de conexión
        self.database_url = self._build_connection_string()

        # Motor de base de datos (se inicializa lazy)
        self._engine: Engine | None = None

    def _validate_config(self) -> None:
        """Validar la configuración de base de datos."""
        required_fields = {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
        }

        missing_fields = [
            field for field, value in required_fields.items() if not value
        ]
        if missing_fields:
            raise DatabaseError(", ".join(missing_fields))

    def _build_connection_string(self) -> str:
        """Construir la cadena de conexión para PostgreSQL."""
        # Codificar credenciales para manejar caracteres especiales
        encoded_username = urllib.parse.quote_plus(self.username)
        encoded_password = (
            urllib.parse.quote_plus(self.password) if self.password else ""
        )

        # Construir la URL base
        if encoded_password:
            auth_part = f"{encoded_username}:{encoded_password}"
        else:
            auth_part = encoded_username

        return f"postgresql://{auth_part}@{self.host}:{self.port}/{self.database}"

    @property
    def engine(self) -> Engine:
        """Obtener el motor de base de datos (inicialización lazy)."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> Engine:
        """Crear el motor de base de datos con configuración optimizada."""
        try:
            engine = create_engine(
                self.database_url,
                echo=self.echo,
                pool_pre_ping=self.pool_pre_ping,
                pool_recycle=self.pool_recycle,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                # Configuraciones adicionales para PostgreSQL
                connect_args={
                    "connect_timeout": 30,
                    "application_name": "SIS_Application",
                },
            )

            logger.info(
                "Motor de base de datos creado exitosamente para %s:%s/%s",
                self.host,
                self.port,
                self.database,
            )

        except Exception as e:
            logger.exception("Error creando motor de base de datos")
            message = "No se pudo crear el motor de base de datos"
            raise DatabaseError(message) from e
        else:
            return engine

    def get_session(self) -> Session:
        """Obtener una sesión de base de datos."""
        try:
            return Session(self.engine)
        except Exception as e:
            logger.exception("Error creando sesión")
            message = "No se pudo crear la sesión"
            raise DatabaseError(message) from e

    @contextmanager
    def get_session_context(self) -> Generator[Session]:
        """Context manager para manejo automático de sesiones."""
        session = None
        try:
            session = self.get_session()
            yield session
            session.commit()
        except Exception as e:
            if session:
                session.rollback()
            logger.exception("Error en sesión de base de datos")
            message = "Error en la sesión de base de datos"
            raise DatabaseError(message) from e
        finally:
            if session:
                session.close()

    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos.

        Args:
            timeout: Tiempo límite para la prueba de conexión

        Returns:
            bool: True si la conexión es exitosa, False en caso contrario

        """
        try:
            with self.get_session_context() as session:
                # Query para obtener la versión de PostgreSQL
                result = session.exec(select(text("version()"))).first()
                logger.info("Conexión exitosa. Versión PostgreSQL: %s", result)
                return True

        except OperationalError:
            logger.exception("Error de conexión operacional")
            return False
        except SQLAlchemyError:
            logger.exception("Error de SQLAlchemy")
            return False
        except Exception:
            logger.exception("Error inesperado en prueba de conexión")
            return False

    def health_check(self) -> dict:
        """Realizar un chequeo de salud de la base de datos.

        Returns:
            dict: Estado de salud de la base de datos

        """
        try:
            with self.get_session_context() as session:
                # Verificar conexión básica
                session.exec(select(text("SELECT 1"))).first()

                return {
                    "status": "healthy",
                    "database": self.database,
                    "host": self.host,
                    "port": self.port,
                    "timestamp": None,  # Se podría agregar timestamp si es necesario
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": self.database,
                "host": self.host,
                "port": self.port,
            }

    def close(self) -> None:
        """Cerrar el motor de base de datos."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Motor de base de datos cerrado")

    def __del__(self) -> None:
        """Cleanup automático del motor."""
        self.close()

    def __repr__(self) -> str:
        """Representación string de la configuración."""
        return (
            f"DatabaseConfig(host='{self.host}', port='{self.port}', "
            f"database='{self.database}', username='{self.username}')"
        )


# Singleton pattern para configuración global
@lru_cache(maxsize=1)
def get_database_config() -> DatabaseConfig:
    """Obtener instancia singleton de configuración de base de datos.

    Returns:
        DatabaseConfig: Instancia de configuración

    """
    return DatabaseConfig()


# Instancia global (retrocompatibilidad)
db_config = get_database_config()


def get_session() -> Generator[Session]:
    """Dependencia para FastAPI - Obtener sesión de base de datos.

    Yields:
        Session: Sesión de SQLModel

    """
    with db_config.get_session_context() as session:
        yield session


def get_engine() -> Engine:
    """Obtener el motor de base de datos.

    Returns:
        Engine: Motor de SQLAlchemy

    """
    return db_config.engine


# Funciones de utilidad adicionales
async def init_database() -> bool:
    """Inicializar y verificar la conexión a la base de datos.

    Returns:
        bool: True si la inicialización es exitosa

    """
    try:
        config = get_database_config()
        if config.test_connection():
            logger.info("Base de datos inicializada correctamente")
            return True
        logger.exception("Fallo en la inicialización de la base de datos")
    except Exception:
        logger.exception("Error en inicialización de base de datos")
        return False
    else:
        return False


async def close_database() -> None:
    """Cerrar conexiones de base de datos al finalizar la aplicación."""
    try:
        db_config.close()
        logger.info("Conexiones de base de datos cerradas")
    except Exception:
        logger.exception("Error cerrando base de datos")
