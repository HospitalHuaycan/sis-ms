from pydantic import BaseModel
from sqlmodel import Field


class CredencialesRequest(BaseModel):
    """Request para autenticación de usuario."""

    usuario: str = Field(..., description="Usuario para autenticación")
    clave: str = Field(..., description="Clave para autenticación")


class ConsultaAfiliadoRequest(BaseModel):
    """Request para consulta de afiliado."""

    opcion: int = Field(..., description="Opción de consulta (entero)")
    dni: str = Field(..., description="DNI del responsable")  # 46118717
    tipo_documento: str = Field(..., description="Tipo de documento")
    nro_documento: str = Field(..., description="Número de documento")
    disa: str | None = Field(None, description="DISA")
    tipo_formato: str | None = Field(None, description="Tipo de formato")
    nro_contrato: str | None = Field(None, description="Número de contrato")
    correlativo: str | None = Field(None, description="Correlativo")
    usuario: str = Field(..., description="Usuario que realiza la consulta")
