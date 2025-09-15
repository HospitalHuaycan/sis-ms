from datetime import datetime

from sqlmodel import Field, SQLModel


class Consulta(SQLModel, table=True):
    """Modelo de consulta."""

    id: int | None = Field(default=None, primary_key=True)
    dni: str
    error: str | None
    estado: str | None
    tipo_seguro: str | None
    created_at: datetime = Field(default_factory=datetime.now)


# Code below omitted 👇
