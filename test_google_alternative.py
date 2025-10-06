#!/usr/bin/env python3
"""
🔧 SOLUCIÓN ALTERNATIVA para Google Ads Detection
Ya que Google Ads Transparency Center requiere JS/autenticación,
vamos a usar métodos alternativos más efectivos
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import quote
from fake_useragent import UserAgent

class AlternativeGoogleAdsDetector:
    def __init__(self):
        ua = UserAgent()
        self.user_agent = ua.random
        self.timeout = 15

    async def detect_google_ads_alternative(self, domain: str) -> dict:
        """Detecta Google Ads usando métodos alternativos más efectivos"""
        
        print(f"🔍 ALTERNATIVE GOOGLE ADS DETECTION: {domain}")
        print("=" * 50)
        
        detection_methods = [
            self.check_ads_txt(domain),
            self.check_google_ads_scripts(domain), 
            self.check_google_search_ads(domain),
            self.check_doubleclick_domains(domain),
            self.check_google_tag_manager(domain)
        ]
        
        results = await asyncio.gather(*detection_methods, return_exceptions=True)
        
        # Analizar resultados combinados
        total_score = 0
        evidence = []
        
        method_names = [
            "ads.txt Analysis",
            "Google Ads Scripts", 
            "Google Search Ads",
            "DoubleClick Domains",
            "Google Tag Manager"
        ]
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                score = result.get('score', 0)
                total_score += score
                
                print(f"✅ {method_names[i]}: {score}% - {result.get('message', '')}")
                if result.get('evidence'):
                    evidence.extend(result['evidence'])
            else:
                print(f"❌ {method_names[i]}: Failed")
        
        # Determinar si tiene Google Ads
        has_google_ads = total_score >= 30  # Threshold más bajo pero más preciso
        confidence = min(100, total_score)
        
        print(f"\n📊 TOTAL SCORE: {total_score}%")
        print(f"🎯 HAS GOOGLE ADS: {has_google_ads}")
        print(f"📈 CONFIDENCE: {confidence}%")
        
        return {
            'domain': domain,
            'has_ads': has_google_ads,
            'confidence': confidence,
            'total_score': total_score,
            'evidence': evidence,
            'message': f"{'✅ Google Ads detectados' if has_google_ads else '❌ No se detectaron Google Ads'} (Score: {total_score}%)"
        }

    async def check_ads_txt(self, domain: str) -> dict:
        """Verifica archivo ads.txt para Google Ads"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://{domain}/ads.txt"
                
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Buscar entradas de Google
                        google_patterns = [
                            r'google\.com',
                            r'googlesyndication\.com', 
                            r'doubleclick\.net',
                            r'googleadservices\.com'
                        ]
                        
                        google_entries = []
                        for pattern in google_patterns:
                            matches = re.findall(f".*{pattern}.*", content, re.IGNORECASE)
                            google_entries.extend(matches)
                        
                        if google_entries:
                            return {
                                'score': 40,  # High score for ads.txt
                                'evidence': [f"ads.txt: {entry[:80]}..." for entry in google_entries[:3]],
                                'message': f"{len(google_entries)} Google entries in ads.txt"
                            }
            
            return {'score': 0, 'message': 'No ads.txt or no Google entries'}
            
        except Exception as e:
            return {'score': 0, 'message': f'ads.txt check failed: {str(e)}'}

    async def check_google_ads_scripts(self, domain: str) -> dict:
        """Busca scripts de Google Ads en la página principal"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': self.user_agent}
                url = f"https://{domain}"
                
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Patrones específicos de Google Ads
                        google_ads_patterns = [
                            r'googleadservices\.com',
                            r'googlesyndication\.com',
                            r'doubleclick\.net',
                            r'google_ad_client',
                            r'gtag\s*\(\s*[\'"]config[\'"].*[\'"]AW-',
                            r'_gac_',
                            r'_gcl_',
                            r'googleads\.g\.doubleclick\.net'
                        ]
                        
                        found_patterns = []
                        for pattern in google_ads_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                found_patterns.append(pattern)
                        
                        if found_patterns:
                            score = min(30, len(found_patterns) * 8)  # Max 30 points
                            return {
                                'score': score,
                                'evidence': [f"Script pattern: {p}" for p in found_patterns],
                                'message': f"{len(found_patterns)} Google Ads patterns found"
                            }
            
            return {'score': 0, 'message': 'No Google Ads scripts found'}
            
        except Exception as e:
            return {'score': 0, 'message': f'Scripts check failed: {str(e)}'}

    async def check_google_search_ads(self, domain: str) -> dict:
        """Busca el dominio en Google para ver si aparecen anuncios"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': self.user_agent}
                # Búsqueda específica para el dominio
                search_query = f"site:{domain}"
                url = f"https://www.google.com/search?q={quote(search_query)}"
                
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Buscar indicadores de que el sitio hace ads
                        ad_indicators = [
                            r'Anuncio',  # Spanish
                            r'Publicidad',
                            r'Ad\s*·',   # English  
                            r'Sponsored',
                            domain.replace('.com', '')  # Brand name
                        ]
                        
                        found_indicators = []
                        for pattern in ad_indicators:
                            if re.search(pattern, content, re.IGNORECASE):
                                found_indicators.append(pattern)
                        
                        if found_indicators:
                            return {
                                'score': 15,
                                'evidence': [f"Search indicator: {i}" for i in found_indicators],
                                'message': f"Domain appears in Google search results with ad indicators"
                            }
            
            return {'score': 0, 'message': 'No search ads indicators'}
            
        except Exception as e:
            return {'score': 0, 'message': f'Search ads check failed: {str(e)}'}

    async def check_doubleclick_domains(self, domain: str) -> dict:
        """Verifica conexiones a dominios de DoubleClick"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': self.user_agent}
                url = f"https://{domain}"
                
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Dominios específicos de Google/DoubleClick
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
                                'evidence': [f"Connected to: {d}" for d in found_domains],
                                'message': f"{len(found_domains)} Google/DoubleClick domains found"
                            }
            
            return {'score': 0, 'message': 'No DoubleClick domains found'}
            
        except Exception as e:
            return {'score': 0, 'message': f'DoubleClick check failed: {str(e)}'}

    async def check_google_tag_manager(self, domain: str) -> dict:
        """Verifica Google Tag Manager (GTM) que a menudo maneja Google Ads"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': self.user_agent}
                url = f"https://{domain}"
                
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Patrones de GTM
                        gtm_patterns = [
                            r'GTM-[A-Z0-9]+',
                            r'googletagmanager\.com/gtm\.js',
                            r'dataLayer\s*=',
                            r'gtag\s*\(',
                        ]
                        
                        gtm_found = []
                        for pattern in gtm_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                gtm_found.extend(matches[:2])  # Limit to 2 per pattern
                        
                        if gtm_found:
                            return {
                                'score': 20,
                                'evidence': [f"GTM: {match}" for match in gtm_found],
                                'message': f"Google Tag Manager detected"
                            }
            
            return {'score': 0, 'message': 'No GTM found'}
            
        except Exception as e:
            return {'score': 0, 'message': f'GTM check failed: {str(e)}'}

async def test_alternative_detection():
    """Test la detección alternativa con dominios conocidos"""
    
    detector = AlternativeGoogleAdsDetector()
    
    test_domains = [
        "nike.com",
        "amazon.com", 
        "booking.com",
        "adidas.com",
        "repsol.es",
        "walmart.com"
    ]
    
    print("🚀 ALTERNATIVE GOOGLE ADS DETECTION")
    print("Usando métodos más efectivos que Google Transparency Center")
    print("=" * 70)
    
    successful_detections = []
    
    for domain in test_domains:
        print(f"\n🎯 TESTING: {domain}")
        print("-" * 50)
        
        result = await detector.detect_google_ads_alternative(domain)
        
        if result['has_ads']:
            successful_detections.append(domain)
        
        await asyncio.sleep(1)  # Rate limiting
    
    print(f"\n{'='*70}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*70}")
    print(f"✅ Dominios con Google Ads detectados: {len(successful_detections)}/{len(test_domains)}")
    
    for domain in successful_detections:
        print(f"   • {domain}")
    
    if len(successful_detections) > 0:
        print(f"\n🎉 ÉXITO! La detección alternativa funciona")
        print(f"📈 Tasa de éxito: {len(successful_detections)/len(test_domains)*100:.1f}%")
    else:
        print(f"\n❌ Ninguna detección exitosa")

if __name__ == "__main__":
    asyncio.run(test_alternative_detection())