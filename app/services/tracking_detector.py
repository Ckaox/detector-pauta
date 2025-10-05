import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import asyncio
from fake_useragent import UserAgent


class TrackingDetector:
    """Detector de pixels de tracking y scripts de anuncios sin usar APIs"""
    
    def __init__(self):
        self.timeout = 10
        ua = UserAgent()
        self.user_agent = ua.random
        
        # Patrones para detectar tracking de Facebook/Meta
        self.facebook_patterns = [
            r'facebook\.com/tr',
            r'fbq\s*\(',
            r'_fbp',
            r'_fbc',
            r'facebook\.net',
            r'connect\.facebook\.net',
            r'Meta\s+Pixel',
            r'FB\.init'
        ]
        
        # Patrones para detectar tracking de Google Ads
        self.google_ads_patterns = [
            r'googleadservices\.com',
            r'googlesyndication\.com',
            r'doubleclick\.net',
            r'gtag\s*\(',
            r'ga\s*\(',
            r'google_ad_client',
            r'_gac_',
            r'_gcl_',
            r'conversion_id',
            r'google_conversion_id',
            r'gtm\.js',
            r'adnxs\.com'
        ]
        
        # Patrones UTM y parámetros de campaigns
        self.campaign_patterns = [
            r'utm_source',
            r'utm_medium',
            r'utm_campaign',
            r'gclid=',
            r'fbclid=',
            r'msclkid='
        ]
    
    async def analyze_website(self, domain: str) -> Dict:
        """Analiza un sitio web para detectar indicadores de anuncios"""
        normalized_domain = self.normalize_domain(domain)
        
        try:
            # Obtener contenido del sitio
            html_content = await self.fetch_website_content(f"https://{normalized_domain}")
            if not html_content:
                html_content = await self.fetch_website_content(f"http://{normalized_domain}")
            
            if not html_content:
                return self.create_analysis_result(normalized_domain, False, 0, "No se pudo acceder al sitio")
            
            # Analizar contenido
            analysis = self.analyze_html_content(html_content)
            
            # Calcular score de probabilidad
            probability_score = self.calculate_probability_score(analysis)
            
            return self.create_analysis_result(
                normalized_domain, 
                probability_score > 30,  # Umbral del 30%
                probability_score,
                analysis
            )
            
        except Exception as e:
            return self.create_analysis_result(normalized_domain, False, 0, f"Error: {str(e)}")
    
    def normalize_domain(self, domain: str) -> str:
        """Normaliza el dominio"""
        domain = domain.lower()
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")
        if domain.endswith("/"):
            domain = domain[:-1]
        return domain
    
    async def fetch_website_content(self, url: str) -> Optional[str]:
        """Obtiene el contenido HTML de un sitio web"""
        headers_list = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        ]
        
        for headers in headers_list:
            try:
                async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                    response = await client.get(url, headers=headers)
                    
                    # Aceptar códigos de respuesta que aún pueden tener contenido útil
                    if response.status_code in [200, 403, 301, 302] and len(response.text) > 100:
                        return response.text
                        
            except Exception:
                continue
                
        # Si todas las opciones fallan, intentar con requests básico
        try:
            import requests
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code in [200, 403] and len(response.text) > 100:
                return response.text
        except Exception:
            pass
            
        return None
    
    def analyze_html_content(self, html: str) -> Dict:
        """Analiza el contenido HTML buscando indicadores de tracking"""
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            'facebook_indicators': [],
            'google_ads_indicators': [],
            'campaign_indicators': [],
            'scripts_found': [],
            'meta_tags': [],
            'external_domains': set()
        }
        
        # Buscar en todo el HTML
        full_text = str(soup).lower()
        
        # Detectar Facebook/Meta tracking
        for pattern in self.facebook_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                analysis['facebook_indicators'].extend(matches)
        
        # Detectar Google Ads tracking  
        for pattern in self.google_ads_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                analysis['google_ads_indicators'].extend(matches)
        
        # Detectar parámetros de campaign
        for pattern in self.campaign_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                analysis['campaign_indicators'].extend(matches)
        
        # Analizar scripts externos
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '')
            if src:
                analysis['scripts_found'].append(src)
                domain = self.extract_domain(src)
                if domain:
                    analysis['external_domains'].add(domain)
        
        # Analizar meta tags relevantes
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if any(keyword in name + property_attr for keyword in ['facebook', 'fb:', 'og:', 'google', 'pixel']):
                analysis['meta_tags'].append({
                    'name': name,
                    'property': property_attr,
                    'content': content
                })
        
        # Convertir set a list para JSON serialization
        analysis['external_domains'] = list(analysis['external_domains'])
        
        return analysis
    
    def extract_domain(self, url: str) -> Optional[str]:
        """Extrae el dominio de una URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return None
    
    def calculate_probability_score(self, analysis: Dict) -> int:
        """Calcula un score de probabilidad de que el sitio tenga anuncios activos"""
        score = 0
        
        # Facebook/Meta indicators (peso alto)
        if analysis['facebook_indicators']:
            score += 40
        
        # Google Ads indicators (peso alto)
        if analysis['google_ads_indicators']:
            score += 40
        
        # Campaign parameters (peso medio)
        if analysis['campaign_indicators']:
            score += 20
        
        # Dominios externos de tracking conocidos
        tracking_domains = [
            'facebook.com', 'facebook.net', 'connect.facebook.net',
            'googleadservices.com', 'googlesyndication.com', 'doubleclick.net',
            'google-analytics.com', 'googletagmanager.com'
        ]
        
        for domain in analysis['external_domains']:
            if any(tracking in domain for tracking in tracking_domains):
                score += 15
        
        # Meta tags relevantes
        for meta in analysis['meta_tags']:
            if any(keyword in meta['property'] + meta['name'] for keyword in ['fb:', 'og:', 'pixel']):
                score += 10
        
        # Scripts específicos
        tracking_scripts = ['fbq', 'gtag', 'ga(', 'fbevents.js', 'gtm.js']
        for script in analysis['scripts_found']:
            if any(tracking in script.lower() for tracking in tracking_scripts):
                score += 15
        
        return min(score, 100)  # Máximo 100%
    
    def create_analysis_result(self, domain: str, likely_has_ads: bool, score: int, details) -> Dict:
        """Crea el resultado del análisis"""
        return {
            'domain': domain,
            'likely_has_ads': likely_has_ads,
            'probability_score': score,
            'facebook_tracking_detected': bool(details.get('facebook_indicators', [])) if isinstance(details, dict) else False,
            'google_ads_tracking_detected': bool(details.get('google_ads_indicators', [])) if isinstance(details, dict) else False,
            'campaign_parameters_detected': bool(details.get('campaign_indicators', [])) if isinstance(details, dict) else False,
            'analysis_details': details if isinstance(details, dict) else {'message': str(details)},
            'recommendation': self.get_recommendation(score)
        }
    
    def get_recommendation(self, score: int) -> str:
        """Devuelve una recomendación basada en el score"""
        if score >= 70:
            return "🟢 Muy probable que tenga anuncios activos - Priorizar para API calls"
        elif score >= 40:
            return "🟡 Probable que tenga anuncios - Considerar para verificación con API"
        elif score >= 20:
            return "🟠 Posible actividad publicitaria - Verificar manualmente"
        else:
            return "🔴 Poco probable que tenga anuncios activos - Baja prioridad"