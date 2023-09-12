"""Photo model.""" ""
from uuid import UUID

from pydantic import BaseModel


class Photo(BaseModel):
    """Photo model."""

    id: UUID
    filename: str
    content: bytes


class PhotoOut(BaseModel):
    """Photo model."""

    id: UUID
    filename: str
