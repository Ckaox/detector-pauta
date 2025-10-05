from pydantic import BaseModel
from typing import Optional


class DomainRequest(BaseModel):
    """Modelo para la solicitud de información de un dominio"""
    domain: str
    country_code: Optional[str] = "anywhere"


class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str
    message: str
    status_code: int