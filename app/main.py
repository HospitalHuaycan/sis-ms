import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import db_config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Contexto de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
    """Contexto de vida de la aplicación."""
    # Startup
    print("🚀 Iniciando aplicación SIS-MS...")

    # Probar conexión a la base de datos PostgreSQL
    if db_config.test_connection():
        print("✅ Conexión a PostgreSQL establecida")
    else:
        print("❌ Error al conectar con PostgreSQL")

    yield

    # Shutdown
    print("🛑 Cerrando aplicación SIS-MS...")


# Crear la aplicación FastAPI
app = FastAPI(
    title="SIS API",
    description="API para gestionar el Sistema Integral de Salud (SIS)",
    version="1.0.0",
    lifespan=lifespan,
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root() -> dict:
    """Endpoint raíz de la API."""
    return {
        "message": "API de SIS - Sistema Integral de Salud",
        "version": "1.0.0",
        "database": "PostgreSQL",
        "endpoints": [
            "/docs - Documentación Swagger",
            "/redoc - Documentación ReDoc",
            "/sis - Endpoints principales del SIS",
            # Agregar aquí tus endpoints específicos
        ],
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Endpoint para verificar el estado de la aplicación."""
    db_status = db_config.test_connection()

    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "service": "SIS-MS",
    }
