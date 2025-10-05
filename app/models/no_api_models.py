from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "Muy Alta"
    HIGH = "Alta"
    MEDIUM = "Media"
    LOW = "Baja"
    VERY_LOW = "Muy Baja"


class PriorityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class TrackingAnalysis(BaseModel):
    """Resultado del análisis de tracking en el sitio web"""
    domain: str
    likely_has_ads: bool
    probability_score: int
    facebook_tracking_detected: bool
    google_ads_tracking_detected: bool
    campaign_parameters_detected: bool
    analysis_details: Dict[str, Any]
    recommendation: str


class PublicLibraryResult(BaseModel):
    """Resultado de búsqueda en bibliotecas públicas de anuncios"""
    domain: str
    has_ads: bool
    source: str
    advertiser_found: Optional[bool] = False
    confidence: int
    message: str
    page_names: Optional[List[str]] = []
    estimated_ads: Optional[int] = 0
    indicators_found: Optional[List[str]] = []


class CombinedScore(BaseModel):
    """Score combinado de todos los métodos de análisis"""
    tracking_score: float
    facebook_score: float
    google_score: float
    final_score: float
    methods_detected: int
    strongest_indicator: str


class NoAPIAnalysisResult(BaseModel):
    """Resultado completo del análisis sin APIs"""
    domain: str
    likely_has_ads: bool
    probability_score: float
    confidence_level: ConfidenceLevel
    recommendation: str
    detailed_analysis: Dict[str, Any]
    summary: CombinedScore
    next_steps: List[str]


class BatchAnalysisRequest(BaseModel):
    """Solicitud para análisis en lote"""
    domains: List[str]
    max_concurrent: Optional[int] = 5


class BatchAnalysisSummary(BaseModel):
    """Resumen de análisis en lote"""
    total_domains_analyzed: int
    priority_distribution: Dict[str, int]
    api_candidates: List[NoAPIAnalysisResult]
    estimated_api_calls_needed: int
    potential_savings: str