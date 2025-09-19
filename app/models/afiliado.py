from datetime import datetime

from sqlmodel import Field, SQLModel


class Afiliado(SQLModel, table=True):
    """Modelo de afiliado."""

    id: int | None = Field(default=None, primary_key=True)
    IdError: int | None = None
    Resultado: str | None = None
    TipoDocumento: str | None = None
    NroDocumento: str | None = None
    ApePaterno: str | None = None
    ApeMaterno: str | None = None
    Nombres: str | None = None
    FecAfiliacion: str | None = None
    EESS: str | None = None
    DescEESS: str | None = None
    EESSUbigeo: str | None = None
    DescEESSUbigeo: str | None = None
    Regimen: str | None = None
    TipoSeguro: str | None = None
    DescTipoSeguro: str | None = None
    Contrato: str | None = None
    FecCaducidad: str | None = None
    Estado: str | None = None
    Tabla: str | None = None
    IdNumReg: str | None = None
    Genero: str | None = None
    FecNacimiento: str | None = None
    IdUbigeo: str | None = None
    Disa: str | None = None
    TipoFormato: str | None = None
    NroContrato: str | None = None
    Correlativo: str | None = None
    IdPlan: str | None = None
    IdGrupoPoblacional: str | None = None
    MsgConfidencial: str | None = None
    ServerError: str | None
    CreatedAt: datetime = Field(default_factory=datetime.now)
