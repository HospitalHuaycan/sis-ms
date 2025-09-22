import os
import urllib.parse
from collections.abc import Generator
from functools import lru_cache

from sqlmodel import Session, create_engine, select, text


class DatabaseConfig:
    """Configuración de conexión a la base de datos."""

    def __init__(self) -> None:
        """Inicializar la configuración de conexión."""
        # Configuración para PostgreSQL
        self.host = os.getenv("DB_SERVER", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "sis_database")
        self.username = os.getenv("DB_USER", "your_username")
        self.password = os.getenv("DB_PASSWORD", "your_password")

        # Construir la URL de conexión
        self.database_url = self._build_connection_string()

        # Crear el motor de base de datos
        self.engine = create_engine(
            self.database_url,
            echo=True,  # Cambiar a False en producción para reducir logs
            pool_pre_ping=True,  # Verificar conexiones antes de usarlas
            pool_recycle=3600,  # Reciclar conexiones cada hora
            pool_size=10,  # Tamaño del pool de conexiones
            max_overflow=20,  # Conexiones adicionales máximas
        )

    def _build_connection_string(self) -> str:
        """Construir la cadena de conexión para PostgreSQL."""
        # Codificar la contraseña para manejar caracteres especiales
        encoded_password = urllib.parse.quote_plus(self.password)

        # Construir la URL de conexión para PostgreSQL
        return (
            f"postgresql://{self.username}:{encoded_password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    def get_session(self) -> Session:
        """Obtener una sesión de base de datos."""
        return Session(self.engine)

    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos."""
        try:
            with self.get_session() as session:
                # Query específica para PostgreSQL
                version = session.exec(select(text("version()")))
                print("Conexión exitosa:", version)
                return True
        except Exception as e:
            print(f"Error de conexión a la base de datos: {e}")
            return False


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
    """Dependencia para obtener sesión de base de datos en FastAPI."""
    with db_config.get_session() as session:
        yield session
