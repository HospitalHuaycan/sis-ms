from pydantic import BaseModel


class Afiliado(BaseModel):
    """Modelo de afiliado."""

    IdError: int
    Resultado: str
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
