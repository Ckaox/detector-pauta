from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from ..services import NoAPIAdsDetector
from ..models import (
    NoAPIAnalysisResult, BatchAnalysisRequest, BatchAnalysisSummary,
    TrackingAnalysis, PublicLibraryResult
)
from datetime import datetime

router = APIRouter(prefix="/api/v1/no-api", tags=["no-api-detection"])

# Instancia del detector sin APIs
no_api_detector = NoAPIAdsDetector()


@router.get("/analyze/{domain}", response_model=NoAPIAnalysisResult)
async def analyze_domain_without_apis(
    domain: str,
    include_details: Optional[bool] = Query(True, description="Incluir análisis detallado")
):
    """
    Analiza un dominio para detectar anuncios SIN usar APIs de Google Ads o Meta.
    
    Utiliza múltiples métodos:
    - Análisis de tracking pixels y scripts en el sitio web
    - Búsqueda en Facebook Ad Library público
    - Búsqueda en Google Ads Transparency Center
    
    Retorna un score de probabilidad y recomendaciones.
    """
    try:
        result = await no_api_detector.analyze_domain_comprehensive(domain)
        
        if not include_details:
            # Remover detalles para respuesta más liviana
            result.pop('detailed_analysis', None)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al analizar dominio sin APIs: {str(e)}"
        )


@router.post("/batch-analyze", response_model=List[NoAPIAnalysisResult])
async def batch_analyze_domains(
    request: BatchAnalysisRequest
):
    """
    Analiza múltiples dominios en lote SIN usar APIs.
    
    Perfecto para filtrar bases de datos grandes antes de usar APIs costosas.
    - Máximo 100 dominios por solicitud
    - Procesamiento en paralelo controlado
    - Resultados ordenados por probabilidad
    """
    try:
        if len(request.domains) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Máximo 100 dominios por solicitud"
            )
        
        if len(request.domains) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Debe proporcionar al menos un dominio"
            )
        
        results = await no_api_detector.batch_analyze_domains(
            request.domains, 
            request.max_concurrent
        )
        
        # Ordenar por probabilidad descendente
        results.sort(key=lambda x: x.get('probability_score', 0), reverse=True)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en análisis en lote: {str(e)}"
        )


@router.post("/batch-summary", response_model=BatchAnalysisSummary)
async def get_batch_analysis_summary(
    request: BatchAnalysisRequest
):
    """
    Obtiene un resumen estadístico del análisis en lote.
    
    Útil para entender la distribución de probabilidades y 
    planificar el uso de APIs pagadas.
    """
    try:
        if len(request.domains) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Máximo 100 dominios por solicitud"
            )
        
        results = await no_api_detector.batch_analyze_domains(
            request.domains, 
            request.max_concurrent
        )
        
        summary = no_api_detector.generate_summary_report(results)
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al generar resumen: {str(e)}"
        )


@router.get("/tracking/{domain}")
async def analyze_website_tracking_only(domain: str):
    """
    Analiza únicamente el tracking del sitio web (método más rápido).
    
    Solo analiza pixels, scripts y elementos de tracking en el sitio web.
    No consulta bibliotecas públicas externas.
    """
    try:
        result = await no_api_detector.tracking_detector.analyze_website(domain)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al analizar tracking: {str(e)}"
        )


@router.get("/facebook-library/{domain}")
async def search_facebook_library_only(domain: str):
    """
    Busca únicamente en Facebook Ad Library público.
    """
    try:
        result = await no_api_detector.facebook_scraper.search_advertiser(domain)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al buscar en Facebook Ad Library: {str(e)}"
        )


@router.get("/google-transparency/{domain}")
async def search_google_transparency_only(domain: str):
    """
    Busca únicamente en Google Ads Transparency Center.
    """
    try:
        result = await no_api_detector.google_scraper.search_advertiser(domain)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al buscar en Google Transparency: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Verificación de salud del servicio de detección sin APIs.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "no-api-ads-detector",
        "version": "1.0.0",
        "methods_available": [
            "website_tracking_analysis",
            "facebook_ad_library_search",
            "google_transparency_search"
        ]
    }