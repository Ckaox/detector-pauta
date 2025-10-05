from .google_ads_service import GoogleAdsService
from .meta_ads_service import MetaAdsService
from ..models.ads_models import DomainAdsResponse
from datetime import datetime
import asyncio


class AdsAggregatorService:
    """Servicio que agrega la información de Google Ads y Meta Ads"""
    
    def __init__(self):
        self.google_service = GoogleAdsService()
        self.meta_service = MetaAdsService()
    
    async def get_domain_ads_info(self, domain: str, country_code: str = "anywhere") -> DomainAdsResponse:
        """
        Obtiene información completa de anuncios para un dominio específico
        """
        # Normalizar el dominio
        normalized_domain = self.google_service.normalize_domain(domain)
        
        # Ejecutar ambas consultas en paralelo
        google_result, meta_result = await asyncio.gather(
            self.google_service.get_google_ads_info(domain, country_code),
            self.meta_service.get_meta_ads_info(domain)
        )
        
        return DomainAdsResponse(
            normalized_url=normalized_domain,
            google_ads=google_result,
            meta_ads=meta_result
        )
    
    async def get_multiple_domains_info(self, domains: list, country_code: str = "anywhere") -> list:
        """
        Obtiene información de anuncios para múltiples dominios
        """
        tasks = [self.get_domain_ads_info(domain, country_code) for domain in domains]
        results = await asyncio.gather(*tasks)
        return results