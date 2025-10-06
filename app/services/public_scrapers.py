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
        
        # Patrones que indican presencia de anuncios (MÁS PATRONES)
        ad_indicators = [
            'ads from',
            'advertisement', 
            'sponsored',
            'see all ads',
            'active ads',
            'inactive ads',
            f'{domain}',
            f'{domain.replace(".com", "")}',     # Sin .com
            f'{domain.split(".")[0]}',           # Solo primera parte
            'advertiser',
            'page transparency',
            'campaign',
            'promotion',
            'marketing'
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
        
        # Determinar si hay anuncios basado en los indicadores encontrados (CRITERIOS RELAJADOS)
        analysis['has_ads'] = (
            len(found_indicators) >= 1 or          # Reducido: solo 1 indicador necesario
            analysis['advertiser_found'] or 
            analysis['estimated_ads'] > 0 or
            any(keyword in text_content for keyword in ['active ads', 'see all ads', 'advertisement', 'sponsored', 'ads from']) or
            domain.replace('.com', '') in text_content  # Más flexible con nombres
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
        """
        NUEVA IMPLEMENTACIÓN: Detección alternativa de Google Ads
        Ya que Google Transparency Center requiere JS/autenticación,
        usamos métodos más efectivos
        """
        try:
            total_score = 0
            evidence = []
            
            # Método 1: Verificar ads.txt
            ads_txt_score = await self._check_ads_txt(domain)
            total_score += ads_txt_score.get('score', 0)
            if ads_txt_score.get('evidence'):
                evidence.extend(ads_txt_score['evidence'])
            
            # Método 2: Verificar scripts de Google Ads
            scripts_score = await self._check_google_ads_scripts(domain)
            total_score += scripts_score.get('score', 0)
            if scripts_score.get('evidence'):
                evidence.extend(scripts_score['evidence'])
            
            # Método 3: Verificar dominios de DoubleClick
            doubleclick_score = await self._check_doubleclick_domains(domain)
            total_score += doubleclick_score.get('score', 0)
            if doubleclick_score.get('evidence'):
                evidence.extend(doubleclick_score['evidence'])
            
            # Determinar si tiene Google Ads (threshold más realista)
            has_ads = total_score >= 20  # Reducido de 30 para ser más sensible
            confidence = min(100, total_score)
            
            analysis = {
                'has_ads': has_ads,
                'advertiser_found': has_ads,
                'indicators': evidence,
                'total_score': total_score
            }
            
            return self.create_result(domain, has_ads, analysis)
            
        except Exception as e:
            return self.create_result(domain, False, f"Error en detección alternativa: {str(e)}")

    async def _check_ads_txt(self, domain: str) -> dict:
        """Verifica archivo ads.txt para entradas de Google"""
        try:
            url = f"https://{domain}/ads.txt"
            content = await self.fetch_content(url)
            
            if content:
                google_patterns = [
                    r'google\.com',
                    r'googlesyndication\.com', 
                    r'doubleclick\.net',
                    r'googleadservices\.com'
                ]
                
                google_entries = []
                for pattern in google_patterns:
                    matches = re.findall(f".*{pattern}.*", content, re.IGNORECASE)
                    google_entries.extend(matches[:2])  # Max 2 per pattern
                
                if google_entries:
                    return {
                        'score': 40,  # High score for ads.txt
                        'evidence': [f"ads.txt: {entry[:60]}..." for entry in google_entries]
                    }
            
            return {'score': 0}
            
        except Exception:
            return {'score': 0}

    async def _check_google_ads_scripts(self, domain: str) -> dict:
        """Busca scripts de Google Ads en la página principal"""
        try:
            url = f"https://{domain}"
            content = await self.fetch_content(url)
            
            if content:
                google_ads_patterns = [
                    r'googleadservices\.com',
                    r'googlesyndication\.com',
                    r'doubleclick\.net',
                    r'google_ad_client',
                    r'gtag\s*\(\s*[\'"]config[\'"].*[\'"]AW-',
                    r'_gac_',
                    r'_gcl_'
                ]
                
                found_patterns = []
                for pattern in google_ads_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_patterns.append(pattern)
                
                if found_patterns:
                    score = min(30, len(found_patterns) * 6)  # Max 30 points
                    return {
                        'score': score,
                        'evidence': [f"Script: {p[:30]}..." for p in found_patterns]
                    }
            
            return {'score': 0}
            
        except Exception:
            return {'score': 0}

    async def _check_doubleclick_domains(self, domain: str) -> dict:
        """Verifica conexiones a dominios de Google/DoubleClick"""
        try:
            url = f"https://{domain}"
            content = await self.fetch_content(url)
            
            if content:
                doubleclick_domains = [
                    'googletagmanager.com',
                    'googletagservices.com',
                    'google-analytics.com',
                    'googleadservices.com',
                    'googlesyndication.com',
                    'doubleclick.net'
                ]
                
                found_domains = []
                for domain_check in doubleclick_domains:
                    if domain_check in content:
                        found_domains.append(domain_check)
                
                if found_domains:
                    score = min(25, len(found_domains) * 5)
                    return {
                        'score': score,
                        'evidence': [f"Connected: {d}" for d in found_domains]
                    }
            
            return {'score': 0}
            
        except Exception:
            return {'score': 0}
    
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
        
        # Indicadores de Google Ads (MÁS INDICADORES)
        indicators = [
            'advertiser',
            'campaign',
            'google ads',
            'advertisement',
            domain.lower(),
            domain.replace('.com', '').lower(),    # Sin .com
            domain.split('.')[0].lower(),          # Solo primera parte  
            'verified advertiser',
            'ads by',
            'sponsored',
            'promotion'
        ]
        
        found_indicators = []
        for indicator in indicators:
            if indicator in text_content:
                found_indicators.append(indicator)
        
        # Buscar información específica del advertiser
        if domain.lower() in text_content:
            analysis['advertiser_found'] = True
        
        # Determinar si hay anuncios (CRITERIOS RELAJADOS)
        analysis['has_ads'] = (
            len(found_indicators) >= 1 or         # Solo 1 indicador necesario
            analysis['advertiser_found'] or
            'verified advertiser' in text_content or
            domain.replace('.com', '').lower() in text_content
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
                'source': 'Google Ads Detection (Alternative)',
                'advertiser_found': details.get('advertiser_found', False),
                'indicators_found': details.get('indicators', []),
                'total_score': details.get('total_score', 0),
                'confidence': confidence,
                'message': f"✅ Google Ads detectados (Score: {details.get('total_score', 0)}%)" if has_ads else f"❌ No detectados (Score: {details.get('total_score', 0)}%)"
            }