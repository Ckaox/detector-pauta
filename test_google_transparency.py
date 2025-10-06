#!/usr/bin/env python3
"""
🔍 Test específico para Google Ads Transparency Center
Verificando si la URL y el scraper funcionan correctamente
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote
from fake_useragent import UserAgent
import re

class GoogleTransparencyTester:
    def __init__(self):
        self.base_url = "https://adstransparency.google.com"
        self.timeout = 15
        ua = UserAgent()
        self.user_agent = ua.random

    async def test_different_urls(self, domain: str):
        """Prueba diferentes formatos de URL para Google Transparency"""
        
        test_urls = [
            # URL actual en el código
            f"{self.base_url}/advertiser?advertiser={quote(domain)}",
            
            # Variaciones posibles
            f"{self.base_url}/search?q={quote(domain)}",
            f"{self.base_url}/advertiser/{quote(domain)}",
            f"{self.base_url}/search?advertiser={quote(domain)}",
            f"{self.base_url}/?q={quote(domain)}",
            f"{self.base_url}/transparency/advertiser?name={quote(domain)}",
            
            # Intentar con nombre de marca sin .com
            f"{self.base_url}/advertiser?advertiser={quote(domain.replace('.com', ''))}",
            f"{self.base_url}/search?q={quote(domain.replace('.com', ''))}",
        ]
        
        print(f"🔍 TESTING URLs para: {domain}")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(test_urls, 1):
                print(f"\n📋 Test {i}: {url}")
                
                try:
                    headers = {
                        'User-Agent': self.user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    }
                    
                    async with session.get(url, headers=headers, timeout=self.timeout) as response:
                        print(f"   🌐 Status: {response.status}")
                        
                        if response.status == 200:
                            content = await response.text()
                            analysis = self.analyze_content(content, domain)
                            
                            print(f"   📄 Content Length: {len(content)}")
                            print(f"   🎯 Domain Found: {analysis['domain_found']}")
                            print(f"   📊 Advertiser Found: {analysis['advertiser_found']}")
                            print(f"   🔍 Indicators: {analysis['indicators']}")
                            print(f"   ✅ Has Ads: {analysis['has_ads']}")
                            
                            if analysis['has_ads']:
                                print(f"   🎉 ÉXITO! Esta URL funciona")
                                return url, analysis
                            
                            # Mostrar snippet del contenido para debug
                            snippet = content[:200].replace('\n', ' ')
                            print(f"   📝 Content Preview: {snippet}...")
                            
                        elif response.status == 404:
                            print(f"   ❌ Not Found")
                        elif response.status == 403:
                            print(f"   🚫 Forbidden (posible anti-bot)")
                        else:
                            print(f"   ⚠️  Status inesperado: {response.status}")
                            
                except asyncio.TimeoutError:
                    print(f"   ⏰ Timeout")
                except Exception as e:
                    print(f"   💥 Error: {str(e)}")
        
        return None, None

    def analyze_content(self, html: str, domain: str) -> dict:
        """Analiza el contenido buscando indicadores de Google Ads"""
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text().lower()
        
        analysis = {
            'domain_found': False,
            'advertiser_found': False,
            'indicators': [],
            'has_ads': False
        }
        
        # Buscar el dominio
        domain_variations = [
            domain.lower(),
            domain.replace('.com', '').lower(),
            domain.split('.')[0].lower()
        ]
        
        for variation in domain_variations:
            if variation in text_content:
                analysis['domain_found'] = True
                analysis['indicators'].append(f'domain:{variation}')
                break
        
        # Buscar indicadores de Google Ads
        ad_indicators = [
            'advertiser',
            'advertisement',
            'google ads',
            'campaign',
            'verified advertiser',
            'ads by',
            'sponsored',
            'promotion',
            'advertising',
            'ad campaigns'
        ]
        
        for indicator in ad_indicators:
            if indicator in text_content:
                analysis['indicators'].append(indicator)
                if indicator in ['advertiser', 'verified advertiser']:
                    analysis['advertiser_found'] = True
        
        # Determinar si hay anuncios
        analysis['has_ads'] = (
            analysis['domain_found'] and len(analysis['indicators']) >= 1
        ) or analysis['advertiser_found']
        
        return analysis

async def test_known_advertisers():
    """Prueba con dominios que SABEMOS que tienen Google Ads"""
    
    tester = GoogleTransparencyTester()
    
    # Dominios que casi seguro tienen Google Ads
    test_domains = [
        "nike.com",        # Marca global masiva
        "amazon.com",      # E-commerce gigante  
        "booking.com",     # Travel con mucho ad spend
        "adidas.com",      # Deportes/competidor Nike
        "walmart.com",     # Retail gigante
        "target.com",      # Retail competidor
        "bestbuy.com",     # Electronics retail
        "homedepot.com",   # Home improvement
        "repsol.es",       # El único que dio positivo según usuario
    ]
    
    print("🎯 TESTING GOOGLE ADS TRANSPARENCY CENTER")
    print("Probando dominios que DEBERÍAN tener Google Ads")
    print("=" * 70)
    
    successful_urls = []
    successful_domains = []
    
    for domain in test_domains:
        print(f"\n🔍 DOMAIN: {domain}")
        print("-" * 40)
        
        working_url, analysis = await tester.test_different_urls(domain)
        
        if working_url:
            successful_urls.append(working_url)
            successful_domains.append(domain)
            print(f"✅ WORKING URL FOUND: {working_url}")
        else:
            print(f"❌ NO WORKING URL FOUND")
        
        # Pausa entre tests
        await asyncio.sleep(2)
    
    print(f"\n" + "=" * 70)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 70)
    
    if successful_urls:
        print(f"✅ URLs que funcionan ({len(successful_urls)}):")
        for url in set(successful_urls):  # Remove duplicates
            print(f"   • {url}")
        
        print(f"\n✅ Dominios detectados ({len(successful_domains)}):")
        for domain in successful_domains:
            print(f"   • {domain}")
            
        # Recomendar la mejor URL
        most_common_url = max(set(successful_urls), key=successful_urls.count)
        print(f"\n🎯 URL RECOMENDADA PARA EL CÓDIGO:")
        print(f"   {most_common_url}")
    else:
        print("❌ NINGUNA URL FUNCIONÓ")
        print("Posibles problemas:")
        print("1. Google cambió la estructura de URLs")
        print("2. Requiere autenticación o API key")
        print("3. Anti-bot protections muy fuertes")
        print("4. El servicio no está disponible públicamente")

if __name__ == "__main__":
    asyncio.run(test_known_advertisers())