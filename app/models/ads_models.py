from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class AdStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class GoogleAdsResult(BaseModel):
    """Modelo para los resultados de Google Ads"""
    has_ads: bool
    total_ad_count: int
    continuation_token: Optional[str] = None
    country_code: str = "anywhere"
    message: str


class MetaAdsResult(BaseModel):
    """Modelo para los resultados de Meta/Facebook Ads"""
    has_ads: bool
    number_of_ads: int
    active_status: AdStatus
    page_id: Optional[str] = None
    message: str


class DomainAdsResponse(BaseModel):
    """Respuesta completa para un dominio específico"""
    normalized_url: str
    google_ads: GoogleAdsResult
    meta_ads: MetaAdsResult


class AdsSummary(BaseModel):
    """Resumen de ads para múltiples dominios"""
    domains: List[DomainAdsResponse]
    total_domains_checked: int
    timestamp: str