from pydantic import BaseModel


class Afiliado(BaseModel):
    """Modelo de afiliado."""

    IdError: int
    Resultado: str
    TipoDocumento: int | None = None
    NroDocumento: str | None = None
    ApePaterno: str | None = None
    ApeMaterno: str | None = None
    Nombres: str | None = None
    FecAfiliacion: str | None = None
    EESS: str | None = None
    DescEESS: str | None = None
    EESSUbigeo: str | None = None
    DescEESSUbigeo: str | None = None
    Regimen: int | None = None
    TipoSeguro: str | None = None
    DescTipoSeguro: str | None = None
    Contrato: str | None = None
    FecCaducidad: str | None = None
    Estado: str | None = None
    Tabla: int | None = None
    IdNumReg: int | None = None
    Genero: int | None = None
    FecNacimiento: str | None = None
    IdUbigeo: int | None = None
    Disa: int | None = None
    TipoFormato: int | None = None
    NroContrato: str | None = None
    Correlativo: str | None = None
    IdPlan: int | None = None
    IdGrupoPoblacional: int | None = None
    MsgConfidencial: str | None = None
