import logging
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
from sqlmodel import Session

from .api.requests import ConsultaAfiliadoRequest, CredencialesRequest
from .database import db_config
from .models.afiliado import Afiliado
from .models.consulta import Consulta
from .services.sis_service import SISService

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
# Register exception handlers globally to have the consistent
# error handling and response structure
register_exception_handlers(app=app, use_fallback_middleware=True)


# Dependency injection para el servicio
def get_sis_service() -> SISService:
    """Dependencia para obtener el servicio SIS."""
    return SISService()


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
    session: Annotated[Session, Depends(db_config.get_session)],
    service: Annotated[SISService, Depends(get_sis_service)],
) -> ResponseModel[Afiliado]:
    """Consultar afiliado FuaE."""
    token = None
    match await service.get_session(
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

    match await service.consultar_afiliado_fuae(token, consulta):
        case Ok(value):
            consulta_model = Consulta(
                dni=consulta.dni,
                error=None,
                estado=value.Estado,
                tipo_seguro=value.DescTipoSeguro,
            )
            session.add(consulta_model)
            session.commit()
            return ResponseModel[Afiliado](
                data=value,
                message="Consulta realizada correctamente",
            )

        case Err((error_code, status_code, message)):
            consulta_model = Consulta(
                dni=consulta.dni,
                error=error_code.message,
                estado=None,
                tipo_seguro=None,
            )
            session.add(consulta_model)
            session.commit()
            raise APIException(
                error_code=error_code,
                http_status_code=status_code,
                log_exception=True,
                message=message,
            )
