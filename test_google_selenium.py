#!/usr/bin/env python3
"""
🔧 Solución para Google Ads Transparency Center
Usando Selenium para renderizar JavaScript y obtener contenido real
"""

import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

class GoogleTransparencySelenium:
    def __init__(self):
        self.base_url = "https://adstransparency.google.com"
        self.setup_driver()

    def setup_driver(self):
        """Configura el driver de Chrome para scraping"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecutar sin GUI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            print(f"❌ Error configurando Chrome driver: {e}")
            print("💡 Asegúrate de tener ChromeDriver instalado")
            self.driver = None

    def test_google_transparency(self, domain: str) -> dict:
        """Prueba Google Transparency con JavaScript rendering"""
        
        if not self.driver:
            return {"error": "ChromeDriver no disponible"}
        
        test_urls = [
            f"{self.base_url}/search?q={domain}",
            f"{self.base_url}/advertiser/{domain}",
            f"{self.base_url}/search?q={domain.replace('.com', '')}",
        ]
        
        results = {}
        
        for url in test_urls:
            print(f"\n🔍 Testing: {url}")
            
            try:
                # Cargar la página
                self.driver.get(url)
                
                # Esperar a que cargue el contenido JavaScript
                wait = WebDriverWait(self.driver, 10)
                
                # Esperar elementos que indiquen que la página cargó
                time.sleep(3)  # Dar tiempo para que JavaScript se ejecute
                
                # Obtener el contenido final
                page_content = self.driver.page_source
                text_content = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # Analizar contenido
                analysis = self.analyze_content_with_js(text_content, domain)
                
                print(f"   📄 Content Length: {len(page_content)}")
                print(f"   📝 Text Length: {len(text_content)}")
                print(f"   🎯 Domain Found: {analysis['domain_found']}")
                print(f"   📊 Advertiser Found: {analysis['advertiser_found']}")
                print(f"   🔍 Indicators: {analysis['indicators']}")
                print(f"   ✅ Has Ads: {analysis['has_ads']}")
                
                # Mostrar snippet del texto extraído
                snippet = text_content[:300].replace('\n', ' ')
                print(f"   📖 Text Preview: {snippet}...")
                
                if analysis['has_ads']:
                    print(f"   🎉 ÉXITO! Encontrado con JavaScript")
                    results[url] = analysis
                
                # Buscar elementos específicos de Google Ads Transparency
                try:
                    # Buscar elementos que podrían indicar resultados de anuncios
                    ad_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'advertiser') or contains(text(), 'campaign') or contains(text(), 'ad')]")
                    if ad_elements:
                        print(f"   🎯 Elementos de ads encontrados: {len(ad_elements)}")
                        for element in ad_elements[:3]:  # Mostrar primeros 3
                            print(f"      • {element.text[:50]}...")
                
                except Exception as e:
                    print(f"   ⚠️ Error buscando elementos: {e}")
                
            except TimeoutException:
                print(f"   ⏰ Timeout cargando página")
            except Exception as e:
                print(f"   💥 Error: {e}")
        
        return results

    def analyze_content_with_js(self, text_content: str, domain: str) -> dict:
        """Analiza contenido extraído con JavaScript"""
        
        analysis = {
            'domain_found': False,
            'advertiser_found': False,
            'indicators': [],
            'has_ads': False
        }
        
        # Buscar variaciones del dominio
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
        
        # Buscar indicadores más específicos después de renderizar JS
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
            'ad campaigns',
            'active ads',
            'ad preview',
            'advertiser name',
            'ad content'
        ]
        
        for indicator in ad_indicators:
            if indicator in text_content:
                analysis['indicators'].append(indicator)
                if indicator in ['advertiser', 'verified advertiser', 'advertiser name']:
                    analysis['advertiser_found'] = True
        
        # Determinar si hay anuncios
        analysis['has_ads'] = (
            analysis['domain_found'] and len(analysis['indicators']) >= 2
        ) or analysis['advertiser_found']
        
        return analysis

    def close(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()

def test_with_selenium():
    """Test principal usando Selenium"""
    
    print("🚀 TESTING GOOGLE TRANSPARENCY CON SELENIUM")
    print("=" * 60)
    
    tester = GoogleTransparencySelenium()
    
    if not tester.driver:
        print("❌ No se pudo inicializar Selenium")
        print("💡 Instala ChromeDriver:")
        print("   1. Descargar de: https://chromedriver.chromium.org/")
        print("   2. Agregar a PATH o colocar en carpeta del proyecto")
        return
    
    # Dominios de prueba
    test_domains = [
        "nike.com",
        "amazon.com", 
        "booking.com",
        "repsol.es"
    ]
    
    successful_results = {}
    
    try:
        for domain in test_domains:
            print(f"\n{'='*60}")
            print(f"🎯 DOMAIN: {domain}")
            print(f"{'='*60}")
            
            results = tester.test_google_transparency(domain)
            if results:
                successful_results[domain] = results
            
            time.sleep(2)  # Pausa entre dominios
    
    finally:
        tester.close()
    
    # Resumen
    print(f"\n{'='*60}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*60}")
    
    if successful_results:
        print(f"✅ Dominios con detección exitosa: {len(successful_results)}")
        for domain, results in successful_results.items():
            print(f"   • {domain}: {len(results)} URLs funcionando")
    else:
        print("❌ CONCLUSIÓN: Google Ads Transparency Center")
        print("   Requiere autenticación o tiene anti-bot muy fuerte")
        print("   Recomendación: Usar Google Ads API oficial")

if __name__ == "__main__":
    test_with_selenium()