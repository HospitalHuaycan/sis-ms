from datetime import datetime

from sqlmodel import Field, SQLModel


class Consulta(SQLModel, table=True):
    """Modelo de consulta."""

    id: int | None = Field(default=None, primary_key=True)
    numero_documento: str = Field(index=True, max_length=8)
    usuario: str
    es_local: bool = False
    error_code: str | None = None
    error_description: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
