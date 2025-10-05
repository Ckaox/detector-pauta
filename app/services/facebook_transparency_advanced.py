import asyncio
import aiohttp
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

class FacebookTransparencyAdvanced:
    """
    Scraper avanzado para la sección de transparencia de Facebook
    Busca la información que aparece en las páginas de Facebook como Apple
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = "https://www.facebook.com"
        
    async def search_page_transparency(self, domain: str) -> dict:
        """
        Busca la página de Facebook del dominio y verifica la sección de transparencia
        que muestra "Esta página tiene anuncios en circulación"
        """
        try:
            # Estrategias de búsqueda múltiples
            search_strategies = [
                f"{domain}",  # Nombre exacto del dominio
                f"{domain.replace('.com', '').replace('.', '')}",  # Sin .com
                f"{domain.split('.')[0]}",  # Solo primera parte
                f"{domain.replace('-', '').replace('_', '')}"  # Sin guiones
            ]
            
            best_result = None
            max_confidence = 0
            
            for search_term in search_strategies:
                result = await self._search_facebook_page(search_term, domain)
                if result and result.get('confidence', 0) > max_confidence:
                    best_result = result
                    max_confidence = result.get('confidence', 0)
                
                # Si encontramos alta confianza, no seguir buscando
                if max_confidence >= 80:
                    break
                    
                await asyncio.sleep(1)  # Rate limiting
            
            return best_result or {
                'domain': domain,
                'has_ads_in_circulation': False,
                'page_found': False,
                'confidence': 0,
                'source': 'facebook_transparency_advanced',
                'message': 'No se encontró página de Facebook o información de transparencia'
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda de transparencia de Facebook para {domain}: {e}")
            return {
                'domain': domain,
                'error': str(e),
                'confidence': 0,
                'source': 'facebook_transparency_advanced'
            }
    
    async def _search_facebook_page(self, search_term: str, original_domain: str) -> dict:
        """Busca la página específica en Facebook"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # URL de búsqueda en Facebook
            search_url = f"{self.base_url}/search/pages/?q={quote(search_term)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        return None
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Buscar enlaces a páginas que coincidan con nuestro dominio
                    page_links = self._extract_page_links(soup, search_term, original_domain)
                    
                    for page_link in page_links:
                        transparency_info = await self._check_page_transparency(page_link, original_domain)
                        if transparency_info:
                            return transparency_info
                        
                        await asyncio.sleep(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando página de Facebook: {e}")
            return None
    
    def _extract_page_links(self, soup: BeautifulSoup, search_term: str, domain: str) -> list:
        """Extrae enlaces de páginas relevantes de los resultados de búsqueda"""
        page_links = []
        
        # Buscar enlaces que apunten a páginas de Facebook
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            
            # Enlaces que apuntan a páginas de Facebook
            if '/pages/' in href or any(term in href.lower() for term in [search_term.lower(), domain.split('.')[0].lower()]):
                if href.startswith('/'):
                    href = self.base_url + href
                elif href.startswith('http'):
                    pass
                else:
                    continue
                
                # Verificar que el enlace sea relevante
                link_text = link.get_text().lower()
                if any(term.lower() in link_text for term in [search_term, domain.split('.')[0]]):
                    page_links.append(href)
        
        return list(set(page_links))[:5]  # Máximo 5 enlaces únicos
    
    async def _check_page_transparency(self, page_url: str, domain: str) -> dict:
        """Verifica la sección de transparencia de una página específica"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Referer': 'https://www.facebook.com/'
            }
            
            async with aiohttp.ClientSession() as session:
                # Ir a la página principal
                async with session.get(page_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        return None
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Buscar la sección de transparencia
                    transparency_indicators = [
                        'tiene anuncios en circulación',
                        'anuncios en circulación',
                        'ads are running',
                        'transparencia de la página',
                        'page transparency',
                        'información de anuncios',
                        'ad information'
                    ]
                    
                    confidence = 0
                    has_ads = False
                    evidence = []
                    
                    # Buscar indicadores en el texto
                    page_text = soup.get_text().lower()
                    for indicator in transparency_indicators:
                        if indicator in page_text:
                            has_ads = True
                            confidence += 20
                            evidence.append(f"Encontrado: '{indicator}'")
                    
                    # Buscar elementos específicos de transparencia
                    transparency_sections = soup.find_all(text=re.compile(r'transparencia|transparency|anuncios|ads', re.IGNORECASE))
                    if transparency_sections:
                        confidence += 15
                        evidence.append(f"Sección de transparencia detectada")
                    
                    # Verificar que sea la página correcta (mencione el dominio)
                    domain_confidence = 0
                    domain_parts = [domain, domain.replace('.com', ''), domain.split('.')[0]]
                    for part in domain_parts:
                        if part.lower() in page_text:
                            domain_confidence += 25
                            evidence.append(f"Dominio '{part}' mencionado")
                    
                    # Solo considerar válido si hay cierta confianza de que es la página correcta
                    if domain_confidence < 25:
                        return None
                    
                    total_confidence = min(100, confidence + domain_confidence)
                    
                    return {
                        'domain': domain,
                        'page_url': page_url,
                        'has_ads_in_circulation': has_ads,
                        'page_found': True,
                        'confidence': total_confidence,
                        'evidence': evidence,
                        'source': 'facebook_transparency_advanced',
                        'message': '✅ Página encontrada con información de transparencia' if has_ads else '❌ No se detectaron anuncios en circulación'
                    }
                    
        except Exception as e:
            logger.error(f"Error verificando transparencia en {page_url}: {e}")
            return None
    
    async def search_by_page_id(self, page_id: str, domain: str) -> dict:
        """Busca información de transparencia usando el ID de página de Facebook"""
        try:
            # URL directa a la página de transparencia
            transparency_url = f"{self.base_url}/{page_id}/about"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(transparency_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_transparency_section(content, domain)
            
            return {
                'domain': domain,
                'page_id': page_id,
                'has_ads_in_circulation': False,
                'confidence': 0,
                'source': 'facebook_page_id_search'
            }
            
        except Exception as e:
            return {
                'domain': domain,
                'error': str(e),
                'confidence': 0,
                'source': 'facebook_page_id_search'
            }
    
    def _parse_transparency_section(self, content: str, domain: str) -> dict:
        """Parsea la sección de transparencia específica"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Buscar elementos específicos de la sección de transparencia
        transparency_patterns = [
            r'esta\s+página\s+tiene\s+anuncios\s+en\s+circulación',
            r'anuncios\s+en\s+circulación',
            r'ads\s+are\s+running',
            r'active\s+ads'
        ]
        
        content_text = soup.get_text().lower()
        has_ads = False
        confidence = 0
        evidence = []
        
        for pattern in transparency_patterns:
            matches = re.findall(pattern, content_text, re.IGNORECASE)
            if matches:
                has_ads = True
                confidence += 30
                evidence.append(f"Patrón detectado: {pattern}")
        
        return {
            'domain': domain,
            'has_ads_in_circulation': has_ads,
            'confidence': min(100, confidence),
            'evidence': evidence,
            'source': 'facebook_transparency_section',
            'message': '✅ Anuncios en circulación detectados' if has_ads else '❌ No se detectaron anuncios en circulación'
        }