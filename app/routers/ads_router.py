from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..services import AdsAggregatorService
from ..models import DomainAdsResponse, AdsSummary, ErrorResponse
from datetime import datetime

router = APIRouter(prefix="/api/v1/ads", tags=["ads"])

# Instancia del servicio agregador
ads_service = AdsAggregatorService()


@router.get("/domain/{domain}", response_model=DomainAdsResponse)
async def get_domain_ads(
    domain: str,
    country_code: Optional[str] = Query("anywhere", description="Código de país para la búsqueda")
):
    """
    Obtiene información de anuncios de Google Ads y Meta/Facebook para un dominio específico.
    
    - **domain**: El dominio a consultar (ej: nike.com, adidas.com)
    - **country_code**: Código de país para filtrar los anuncios (por defecto: anywhere)
    
    Retorna información completa incluyendo:
    - Google Ads: número total de anuncios, token de continuación
    - Meta/Facebook Ads: número de anuncios, estado activo, page ID
    """
    try:
        result = await ads_service.get_domain_ads_info(domain, country_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información de anuncios: {str(e)}")


@router.post("/domains", response_model=AdsSummary)
async def get_multiple_domains_ads(
    domains: List[str],
    country_code: Optional[str] = Query("anywhere", description="Código de país para la búsqueda")
):
    """
    Obtiene información de anuncios para múltiples dominios a la vez.
    
    - **domains**: Lista de dominios a consultar
    - **country_code**: Código de país para filtrar los anuncios
    
    Retorna un resumen con la información de todos los dominios consultados.
    """
    try:
        if not domains:
            raise HTTPException(status_code=400, detail="La lista de dominios no puede estar vacía")
        
        if len(domains) > 50:
            raise HTTPException(status_code=400, detail="No se pueden consultar más de 50 dominios a la vez")
        
        results = await ads_service.get_multiple_domains_info(domains, country_code)
        
        return AdsSummary(
            domains=results,
            total_domains_checked=len(results),
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información de múltiples dominios: {str(e)}")


@router.get("/domain/{domain}/google", response_model=dict)
async def get_google_ads_only(
    domain: str,
    country_code: Optional[str] = Query("anywhere", description="Código de país para la búsqueda")
):
    """
    Obtiene únicamente información de Google Ads para un dominio específico.
    """
    try:
        result = await ads_service.google_service.get_google_ads_info(domain, country_code)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información de Google Ads: {str(e)}")


@router.get("/domain/{domain}/meta", response_model=dict)
async def get_meta_ads_only(
    domain: str
):
    """
    Obtiene únicamente información de Meta/Facebook Ads para un dominio específico.
    """
    try:
        result = await ads_service.meta_service.get_meta_ads_info(domain)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información de Meta Ads: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud del servicio.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ads-checker-api",
        "version": "1.0.0"
    }