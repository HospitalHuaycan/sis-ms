import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from api_exception import (
    APIException,
    APIResponse,
    ResponseModel,
    register_exception_handlers,
)
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from result import Err, Ok

from tools.logger import Logger

from .api.requests import ConsultaAfiliadoRequest, CredencialesRequest
from .database import db_config
from .models.afiliado import Afiliado
from .services.afiliado_service import AfiliadoService
from .services.sis_service import SISService

# Configurar logging
logger = Logger(__name__)


# Contexto de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
    """Contexto de vida de la aplicación."""
    # Startup
    logger.info("🚀 Iniciando aplicación SIS-MS...")

    # Probar conexión a la base de datos PostgreSQL
    if db_config.test_connection():
        logger.info("✅ Conexión a PostgreSQL establecida")
    else:
        logger.info("❌ Error al conectar con PostgreSQL")

    yield
    db_config.close()

    # Shutdown
    logger.info("🛑 Cerrando aplicación SIS-MS...")


# Crear la aplicación FastAPI
app = FastAPI(
    title="SIS API",
    description="API para gestionar el Sistema Integral de Salud (SIS)",
    version="1.0.0",
    lifespan=lifespan,
)
# Register exception handlers globally to have the consistent
# error handling and response structure
register_exception_handlers(app=app, use_fallback_middleware=True)


# Dependency injection para el servicio
def get_sis_service() -> SISService:
    """Dependencia para obtener el servicio SIS."""
    return SISService()


# Dependency injection para el servicio
def get_afiliado_service() -> AfiliadoService:
    """Dependencia para obtener el servicio de Afiliado."""
    return AfiliadoService(db_session=db_config.get_session())


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


# Endpoints
@app.post(
    "/login",
    tags=["SIS"],
    responses=APIResponse.default(),  # type: ignore
)
async def login(
    credenciales: CredencialesRequest,
    service: Annotated[SISService, Depends(get_sis_service)],
) -> ResponseModel[dict]:
    """Obtener token de sesión para autenticación con el SIS."""
    match await service.get_session(credenciales):
        case Ok(value):
            return ResponseModel[dict](
                data={"token": value},
                message="Sesión obtenida exitosamente",
            )

        case Err((error_code, status_code)):
            raise APIException(
                error_code=error_code,
                http_status_code=status_code,
                log_exception=True,
            )


@app.post(
    "/consultar_afiliado",
    tags=["SIS"],
    responses=APIResponse.default(),  # type: ignore
)
async def consultar_afiliado(
    consulta: ConsultaAfiliadoRequest,
    sis_service: Annotated[SISService, Depends(get_sis_service)],
    afiliado_service: Annotated[AfiliadoService, Depends(get_afiliado_service)],
) -> ResponseModel[Afiliado]:
    """Consultar afiliado FuaE."""
    token = None
    match await sis_service.get_session(
        CredencialesRequest(
            usuario=os.getenv("SOAP_USER", "sis_user"),
            clave=os.getenv("SOAP_PASSWORD", "sis_password"),
        )
    ):
        case Ok(value):
            token = value

        case Err((error_code, status_code)):
            raise APIException(
                error_code=error_code,
                http_status_code=status_code,
                log_exception=True,
            )

    match await afiliado_service.consultar_afiliado(token, consulta):
        case Ok(afiliado):
            return ResponseModel[Afiliado](
                data=afiliado,
                message="Consulta realizada correctamente",
            )

        case Err((error_code, status_code, message)):
            raise APIException(
                error_code=error_code,
                http_status_code=status_code,
                log_exception=True,
                message=message,
            )
