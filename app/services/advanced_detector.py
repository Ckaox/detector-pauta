import asyncio
import aiohttp
import re
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedAdsDetector:
    """Detector avanzado de anuncios sin APIs con múltiples técnicas"""
    
    def __init__(self):
        self.ua = UserAgent()
        
        # Dominios conocidos de advertising y tracking
        self.ad_domains = {
            'google_ads': [
                'googleadservices.com', 'googlesyndication.com', 'googletagmanager.com',
                'googletagservices.com', 'google-analytics.com', 'googleads.g.doubleclick.net',
                'doubleclick.net', 'adsystem.com', 'adsense.com'
            ],
            'facebook_ads': [
                'facebook.com/tr', 'connect.facebook.net', 'fbcdn.net',
                'facebook.net', 'instagram.com/embed.js'
            ],
            'other_ads': [
                'amazon-adsystem.com', 'adsystem.com', 'adnxs.com', 'adsafeprotected.com',
                'moatads.com', 'scorecardresearch.com', 'outbrain.com', 'taboola.com',
                'criteo.com', 'rlcdn.com', 'bidswitch.net', 'casalemedia.com'
            ]
        }
        
        # Herramientas de A/B testing y personalización
        self.ab_testing_tools = [
            'optimizely.com', 'google-analytics.com/gtm', 'hotjar.com',
            'fullstory.com', 'mixpanel.com', 'segment.com', 'amplitude.com',
            'heap.com', 'crazyegg.com', 'vwo.com', 'unbounce.com'
        ]
        
        # Keywords que indican actividad publicitaria
        self.ad_keywords = {
            'high_confidence': [
                'utm_campaign', 'utm_source', 'utm_medium', 'gclid', 'fbclid',
                'google_ads', 'facebook_ads', 'adwords', 'remarketing',
                'conversion_tracking', 'retargeting', 'audience_pixel'
            ],
            'medium_confidence': [
                'landing_page', 'campaign', 'promotion', 'offer', 'deal',
                'discount', 'sale', 'limited_time', 'cta', 'call_to_action'
            ]
        }

    async def analyze_domain_advanced(self, domain: str) -> Dict:
        """Análisis avanzado de un dominio"""
        try:
            results = {
                'domain': domain,
                'advanced_analysis': {},
                'confidence_factors': [],
                'risk_score': 0.0,
                'evidence_strength': 'low'
            }
            
            # Ejecutar todos los análisis en paralelo
            tasks = [
                self.analyze_sitemap(domain),
                self.analyze_robots_txt(domain),
                self.analyze_main_page_advanced(domain),
                self.analyze_common_landing_pages(domain),
                self.detect_third_party_integrations(domain),
                self.analyze_javascript_events(domain),
                self.check_structured_data(domain)
            ]
            
            analysis_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            analysis_names = [
                'sitemap_analysis', 'robots_analysis', 'main_page_analysis',
                'landing_pages_analysis', 'third_party_analysis', 
                'javascript_analysis', 'structured_data_analysis'
            ]
            
            total_score = 0
            valid_analyses = 0
            
            for i, result in enumerate(analysis_results):
                if not isinstance(result, Exception) and result:
                    results['advanced_analysis'][analysis_names[i]] = result
                    score = result.get('confidence_score', 0)
                    total_score += score
                    valid_analyses += 1
                    
                    # Agregar factores de confianza
                    if score > 50:
                        results['confidence_factors'].extend(
                            result.get('evidence', [])
                        )
            
            # Calcular score final
            if valid_analyses > 0:
                results['risk_score'] = min(100, total_score / valid_analyses * 1.2)
            
            # Determinar fuerza de evidencia
            if results['risk_score'] >= 70:
                results['evidence_strength'] = 'high'
            elif results['risk_score'] >= 40:
                results['evidence_strength'] = 'medium'
            else:
                results['evidence_strength'] = 'low'
            
            return results
            
        except Exception as e:
            logger.error(f"Error en análisis avanzado de {domain}: {e}")
            return {
                'domain': domain,
                'error': str(e),
                'risk_score': 0.0,
                'evidence_strength': 'error'
            }

    async def analyze_sitemap(self, domain: str) -> Dict:
        """Analiza sitemap.xml para detectar estructura de campañas"""
        try:
            sitemap_urls = [
                f'https://{domain}/sitemap.xml',
                f'https://{domain}/sitemap_index.xml',
                f'https://www.{domain}/sitemap.xml'
            ]
            
            evidence = []
            score = 0
            
            async with aiohttp.ClientSession() as session:
                for url in sitemap_urls:
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Buscar patrones de landing pages de campañas
                                campaign_patterns = [
                                    r'/landing[_-]?page',
                                    r'/campaign',
                                    r'/promo',
                                    r'/offer',
                                    r'/deals?',
                                    r'/sale',
                                    r'/utm_',
                                    r'/lp/',
                                    r'/landing/'
                                ]
                                
                                for pattern in campaign_patterns:
                                    matches = re.findall(pattern, content, re.IGNORECASE)
                                    if matches:
                                        evidence.append(f"Landing pages detectadas: {pattern}")
                                        score += 15
                                
                                # Contar URLs con parámetros de campaña
                                utm_count = len(re.findall(r'utm_', content))
                                if utm_count > 0:
                                    evidence.append(f"URLs con UTM parameters: {utm_count}")
                                    score += min(30, utm_count * 5)
                                
                                break
                                
                    except Exception:
                        continue
            
            return {
                'has_sitemap': len(evidence) > 0,
                'evidence': evidence,
                'confidence_score': min(100, score),
                'analysis_type': 'sitemap'
            }
            
        except Exception as e:
            return {'error': str(e), 'confidence_score': 0}

    async def analyze_robots_txt(self, domain: str) -> Dict:
        """Analiza robots.txt para detectar rutas de tracking"""
        try:
            robots_url = f'https://{domain}/robots.txt'
            evidence = []
            score = 0
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Buscar rutas relacionadas con ads y tracking
                            ad_paths = [
                                r'/ads?/',
                                r'/tracking/',
                                r'/analytics/',
                                r'/conversion/',
                                r'/pixel/',
                                r'/retargeting/',
                                r'/remarketing/',
                                r'/campaign/',
                                r'/utm_'
                            ]
                            
                            for pattern in ad_paths:
                                if re.search(pattern, content, re.IGNORECASE):
                                    evidence.append(f"Ruta de ads detectada: {pattern}")
                                    score += 20
                            
                            # Buscar sitemaps específicos de campañas
                            sitemap_patterns = [
                                r'sitemap[_-]?campaign',
                                r'sitemap[_-]?promo',
                                r'sitemap[_-]?landing'
                            ]
                            
                            for pattern in sitemap_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    evidence.append(f"Sitemap de campañas: {pattern}")
                                    score += 25
                            
                except Exception:
                    pass
            
            return {
                'has_robots': len(evidence) > 0,
                'evidence': evidence,
                'confidence_score': min(100, score),
                'analysis_type': 'robots_txt'
            }
            
        except Exception as e:
            return {'error': str(e), 'confidence_score': 0}

    async def analyze_main_page_advanced(self, domain: str) -> Dict:
        """Análisis avanzado de la página principal"""
        try:
            url = f'https://{domain}'
            evidence = []
            score = 0
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Cache-Control': 'no-cache'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 1. Análisis de headers HTTP
                    response_headers = dict(response.headers)
                    ad_headers = [
                        'x-google-ads', 'x-fb-ads', 'x-ads-enabled',
                        'x-conversion-tracking', 'x-remarketing'
                    ]
                    
                    for header in ad_headers:
                        if any(h.lower().find(header) != -1 for h in response_headers.keys()):
                            evidence.append(f"Header de ads detectado: {header}")
                            score += 20
                    
                    # 2. Detectar third-party domains en recursos
                    third_party_score = await self._analyze_third_party_resources(soup, domain)
                    score += third_party_score['score']
                    evidence.extend(third_party_score['evidence'])
                    
                    # 3. Análisis de JavaScript avanzado
                    js_score = await self._analyze_javascript_advanced(soup)
                    score += js_score['score']
                    evidence.extend(js_score['evidence'])
                    
                    # 4. Detectar structured data para e-commerce
                    structured_score = await self._analyze_structured_data(soup)
                    score += structured_score['score']
                    evidence.extend(structured_score['evidence'])
                    
                    # 5. Análisis de formularios y CTAs
                    form_score = await self._analyze_forms_and_ctas(soup)
                    score += form_score['score']
                    evidence.extend(form_score['evidence'])
            
            return {
                'analysis_completed': True,
                'evidence': evidence,
                'confidence_score': min(100, score),
                'analysis_type': 'main_page_advanced'
            }
            
        except Exception as e:
            return {'error': str(e), 'confidence_score': 0}

    async def _analyze_third_party_resources(self, soup: BeautifulSoup, domain: str) -> Dict:
        """Analiza recursos de terceros que indican advertising"""
        evidence = []
        score = 0
        
        # Buscar scripts, iframes, images de dominios de ads
        all_domains = []
        all_domains.extend(self.ad_domains['google_ads'])
        all_domains.extend(self.ad_domains['facebook_ads'])
        all_domains.extend(self.ad_domains['other_ads'])
        all_domains.extend(self.ab_testing_tools)
        
        for tag in soup.find_all(['script', 'iframe', 'img', 'link']):
            src = tag.get('src') or tag.get('href') or ''
            if src:
                parsed_url = urlparse(src)
                if parsed_url.netloc and parsed_url.netloc != domain:
                    for ad_domain in all_domains:
                        if ad_domain in parsed_url.netloc:
                            evidence.append(f"Recurso de ads: {ad_domain}")
                            score += 15
                            break
        
        return {'evidence': evidence, 'score': min(50, score)}

    async def _analyze_javascript_advanced(self, soup: BeautifulSoup) -> Dict:
        """Análisis avanzado de JavaScript para detectar tracking"""
        evidence = []
        score = 0
        
        # Patrones de JavaScript de advertising
        js_patterns = {
            'conversion_tracking': [
                r'gtag\s*\(\s*[\'"]event[\'"]',
                r'fbq\s*\(\s*[\'"]track[\'"]',
                r'conversion[_-]?tracking',
                r'track[_-]?conversion'
            ],
            'remarketing': [
                r'google_remarketing',
                r'facebook_remarketing',
                r'retargeting[_-]?pixel',
                r'audience[_-]?pixel'
            ],
            'ab_testing': [
                r'optimizely',
                r'google[_-]?optimize',
                r'vwo[_-]?api',
                r'ab[_-]?test'
            ]
        }
        
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.string or ''
            
            for category, patterns in js_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, script_content, re.IGNORECASE):
                        evidence.append(f"JS {category}: {pattern}")
                        score += 10
        
        return {'evidence': evidence, 'score': min(40, score)}

    async def _analyze_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Analiza structured data que indica actividad e-commerce"""
        evidence = []
        score = 0
        
        # Buscar JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    schema_type = data.get('@type', '').lower()
                    
                    # Tipos que indican actividad comercial
                    commercial_types = [
                        'product', 'offer', 'store', 'organization',
                        'localbusiness', 'e-commercesite'
                    ]
                    
                    if any(t in schema_type for t in commercial_types):
                        evidence.append(f"Schema comercial: {schema_type}")
                        score += 15
                        
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return {'evidence': evidence, 'score': min(30, score)}

    async def _analyze_forms_and_ctas(self, soup: BeautifulSoup) -> Dict:
        """Analiza formularios y CTAs que indican campañas"""
        evidence = []
        score = 0
        
        # Buscar formularios con parámetros de tracking
        forms = soup.find_all('form')
        for form in forms:
            # Inputs hidden con valores de tracking
            hidden_inputs = form.find_all('input', type='hidden')
            for inp in hidden_inputs:
                name = inp.get('name', '').lower()
                if any(keyword in name for keyword in ['utm_', 'campaign', 'source', 'medium']):
                    evidence.append(f"Form tracking: {name}")
                    score += 10
        
        # Buscar botones/links con clases que indican CTAs
        cta_classes = ['cta', 'call-to-action', 'btn-primary', 'buy-now', 'sign-up']
        for class_name in cta_classes:
            elements = soup.find_all(class_=re.compile(class_name, re.IGNORECASE))
            if elements:
                evidence.append(f"CTA elements: {class_name}")
                score += 5
        
        return {'evidence': evidence, 'score': min(25, score)}

    async def analyze_common_landing_pages(self, domain: str) -> Dict:
        """Analiza páginas comunes que suelen ser landing pages"""
        common_paths = [
            '/landing', '/lp', '/campaign', '/promo', '/offer',
            '/sale', '/deals', '/signup', '/register', '/demo'
        ]
        
        evidence = []
        score = 0
        
        async with aiohttp.ClientSession() as session:
            for path in common_paths:
                try:
                    url = f'https://{domain}{path}'
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            evidence.append(f"Landing page encontrada: {path}")
                            score += 10
                            
                except Exception:
                    continue
        
        return {
            'landing_pages_found': len(evidence),
            'evidence': evidence,
            'confidence_score': min(60, score),
            'analysis_type': 'landing_pages'
        }

    async def detect_third_party_integrations(self, domain: str) -> Dict:
        """Detecta integraciones con plataformas de ads"""
        # Esta función se implementaría para detectar integraciones
        # basándose en subdominios, DNS records, etc.
        return {
            'integrations_detected': [],
            'confidence_score': 0,
            'analysis_type': 'third_party_integrations'
        }

    async def analyze_javascript_events(self, domain: str) -> Dict:
        """Analiza eventos de JavaScript relacionados con conversión"""
        return {
            'events_detected': [],
            'confidence_score': 0,
            'analysis_type': 'javascript_events'
        }

    async def check_structured_data(self, domain: str) -> Dict:
        """Verifica structured data adicional"""
        return {
            'structured_data_found': [],
            'confidence_score': 0,
            'analysis_type': 'structured_data'
        }