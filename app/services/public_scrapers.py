import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import asyncio
from urllib.parse import quote
from fake_useragent import UserAgent
import time
import random


class FacebookAdLibraryScraper:
    """Scraper para la biblioteca pública de anuncios de Facebook"""
    
    def __init__(self):
        self.base_url = "https://www.facebook.com/ads/library"
        self.timeout = 15
        ua = UserAgent()
        self.user_agent = ua.random
        
    async def search_advertiser(self, domain: str) -> Dict:
        """Busca un anunciante en la biblioteca de anuncios de Facebook"""
        try:
            # Normalizar dominio
            clean_domain = self.normalize_domain(domain)
            
            # Construir URL de búsqueda
            search_url = f"{self.base_url}/?active_status=all&ad_type=all&country=ALL&q={quote(clean_domain)}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered"
            
            # Realizar búsqueda
            content = await self.fetch_content(search_url)
            if not content:
                return self.create_result(domain, False, "No se pudo acceder a Facebook Ad Library")
            
            # Analizar contenido
            analysis = self.analyze_search_results(content, clean_domain)
            
            return self.create_result(domain, analysis['has_ads'], analysis)
            
        except Exception as e:
            return self.create_result(domain, False, f"Error en scraping: {str(e)}")
    
    def normalize_domain(self, domain: str) -> str:
        """Normaliza el dominio para la búsqueda"""
        domain = domain.lower()
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")
        if domain.endswith("/"):
            domain = domain[:-1]
        return domain
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """Obtiene el contenido de la página"""
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # Agregar delay aleatorio para evitar rate limiting
            await asyncio.sleep(random.uniform(1, 3))
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
                
        except Exception:
            return None
    
    def analyze_search_results(self, html: str, domain: str) -> Dict:
        """Analiza los resultados de búsqueda de Facebook Ad Library"""
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            'has_ads': False,
            'advertiser_found': False,
            'page_names': [],
            'estimated_ads': 0,
            'indicators': []
        }
        
        # Buscar indicadores de que hay anuncios
        text_content = soup.get_text().lower()
        
        # Patrones que indican presencia de anuncios
        ad_indicators = [
            'ads from',
            'advertisement',
            'sponsored',
            'see all ads',
            'active ads',
            'inactive ads',
            f'{domain}',
            'advertiser',
            'page transparency'
        ]
        
        found_indicators = []
        for indicator in ad_indicators:
            if indicator in text_content:
                found_indicators.append(indicator)
        
        # Buscar nombres de páginas/advertisers
        page_links = soup.find_all('a', href=True)
        for link in page_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            if domain in href.lower() or domain in text.lower():
                if text and len(text) > 1:
                    analysis['page_names'].append(text)
                    analysis['advertiser_found'] = True
        
        # Buscar elementos específicos de la interfaz de Ad Library
        ad_elements = soup.find_all(['div', 'span'], class_=re.compile(r'.*ad.*|.*advertisement.*', re.I))
        
        # Buscar números que podrían indicar cantidad de anuncios
        numbers = re.findall(r'\b(\d+)\s*(?:ads?|advertisements?)\b', text_content, re.I)
        if numbers:
            try:
                analysis['estimated_ads'] = max([int(num) for num in numbers])
            except:
                pass
        
        # Determinar si hay anuncios basado en los indicadores encontrados
        analysis['has_ads'] = (
            len(found_indicators) >= 2 or 
            analysis['advertiser_found'] or 
            analysis['estimated_ads'] > 0 or
            any(keyword in text_content for keyword in ['active ads', 'see all ads', 'advertisement'])
        )
        
        analysis['indicators'] = found_indicators
        
        return analysis
    
    def create_result(self, domain: str, has_ads: bool, details) -> Dict:
        """Crea el resultado del análisis"""
        if isinstance(details, str):
            # Es un mensaje de error
            return {
                'domain': domain,
                'has_ads': has_ads,
                'source': 'Facebook Ad Library',
                'message': details,
                'confidence': 0
            }
        else:
            # Es un análisis completo
            confidence = self.calculate_confidence(details)
            
            return {
                'domain': domain,
                'has_ads': has_ads,
                'source': 'Facebook Ad Library',
                'advertiser_found': details.get('advertiser_found', False),
                'page_names': details.get('page_names', []),
                'estimated_ads': details.get('estimated_ads', 0),
                'indicators_found': details.get('indicators', []),
                'confidence': confidence,
                'message': self.generate_message(has_ads, details)
            }
    
    def calculate_confidence(self, analysis: Dict) -> int:
        """Calcula el nivel de confianza del resultado"""
        confidence = 0
        
        if analysis.get('advertiser_found'):
            confidence += 40
        
        if analysis.get('estimated_ads', 0) > 0:
            confidence += 30
        
        indicators_count = len(analysis.get('indicators', []))
        confidence += min(indicators_count * 10, 30)
        
        return min(confidence, 100)
    
    def generate_message(self, has_ads: bool, analysis: Dict) -> str:
        """Genera un mensaje descriptivo del resultado"""
        if has_ads:
            if analysis.get('estimated_ads', 0) > 0:
                return f"✅ {analysis['estimated_ads']} anuncios encontrados en Facebook Ad Library"
            elif analysis.get('advertiser_found'):
                return "✅ Anunciante encontrado en Facebook Ad Library"
            else:
                return "✅ Indicadores de anuncios encontrados en Facebook Ad Library"
        else:
            return "❌ No se encontraron anuncios en Facebook Ad Library"


class GoogleTransparencyScraper:
    """Scraper para Google Ads Transparency Center"""
    
    def __init__(self):
        self.base_url = "https://adstransparency.google.com"
        self.timeout = 15
        ua = UserAgent()
        self.user_agent = ua.random
    
    async def search_advertiser(self, domain: str) -> Dict:
        """Busca un anunciante en Google Ads Transparency Center"""
        try:
            clean_domain = self.normalize_domain(domain)
            
            # URL de búsqueda en Google Transparency
            search_url = f"{self.base_url}/advertiser?advertiser={quote(clean_domain)}"
            
            content = await self.fetch_content(search_url)
            if not content:
                return self.create_result(domain, False, "No se pudo acceder a Google Ads Transparency Center")
            
            analysis = self.analyze_search_results(content, clean_domain)
            
            return self.create_result(domain, analysis['has_ads'], analysis)
            
        except Exception as e:
            return self.create_result(domain, False, f"Error en scraping: {str(e)}")
    
    def normalize_domain(self, domain: str) -> str:
        """Normaliza el dominio"""
        domain = domain.lower()
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")
        if domain.endswith("/"):
            domain = domain[:-1]
        return domain
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """Obtiene el contenido de la página"""
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            await asyncio.sleep(random.uniform(1, 3))
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
                
        except Exception:
            return None
    
    def analyze_search_results(self, html: str, domain: str) -> Dict:
        """Analiza los resultados de Google Transparency"""
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            'has_ads': False,
            'advertiser_found': False,
            'campaigns': [],
            'indicators': []
        }
        
        text_content = soup.get_text().lower()
        
        # Indicadores de Google Ads
        indicators = [
            'advertiser',
            'campaign',
            'google ads',
            'advertisement',
            domain.lower(),
            'verified advertiser'
        ]
        
        found_indicators = []
        for indicator in indicators:
            if indicator in text_content:
                found_indicators.append(indicator)
        
        # Buscar información específica del advertiser
        if domain.lower() in text_content:
            analysis['advertiser_found'] = True
        
        # Determinar si hay anuncios
        analysis['has_ads'] = (
            len(found_indicators) >= 2 or 
            analysis['advertiser_found'] or
            'verified advertiser' in text_content
        )
        
        analysis['indicators'] = found_indicators
        
        return analysis
    
    def create_result(self, domain: str, has_ads: bool, details) -> Dict:
        """Crea el resultado del análisis"""
        if isinstance(details, str):
            return {
                'domain': domain,
                'has_ads': has_ads,
                'source': 'Google Ads Transparency',
                'message': details,
                'confidence': 0
            }
        else:
            confidence = len(details.get('indicators', [])) * 20
            confidence = min(confidence, 100)
            
            return {
                'domain': domain,
                'has_ads': has_ads,
                'source': 'Google Ads Transparency',
                'advertiser_found': details.get('advertiser_found', False),
                'indicators_found': details.get('indicators', []),
                'confidence': confidence,
                'message': "✅ Anunciante encontrado en Google Transparency" if has_ads else "❌ No encontrado en Google Transparency"
            }