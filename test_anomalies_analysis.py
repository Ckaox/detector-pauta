#!/usr/bin/env python3
"""
🔍 Análisis detallado de resultados anómalos detectados por el usuario
Investigando por qué ciertos componentes no se detectan correctamente
"""

import requests
import json
import time

BASE_URL = "https://ads-checker-api.onrender.com"

def analyze_anomalies():
    """Analiza las páginas con resultados anómalos reportados por el usuario"""
    
    test_domains = [
        "rockler.com",
        "nike.com", 
        "moodfabrics.com",
        "primor.eu",
        "druni.es",
        "scufgaming.com",
        "adidas.com",
        "saq.com",         # ✅ Facebook Ad Library detectado
        "macron.com",
        "paperpapers.com",
        "repsol.es"        # ✅ Facebook Ad Library detectado + Has Ads = True
    ]
    
    print("🔍 ANÁLISIS DE RESULTADOS ANÓMALOS")
    print("=" * 80)
    print("Investigando patrones extraños:")
    print("• Solo 2/11 páginas con Facebook Ad Library")
    print("• 0/11 páginas con Google Ad Library") 
    print("• Landing Pages, JavaScript Events, Third Party Ads = FALSE en todas")
    print("• Facebook Ad Library positivo pero Facebook Transparency = 0 evidencia")
    print("=" * 80)
    
    results = {}
    anomalies = {
        "facebook_ad_library_positive": [],
        "google_ad_library_zero": [],
        "all_components_false": [],
        "facebook_library_vs_transparency_mismatch": []
    }
    
    for i, domain in enumerate(test_domains, 1):
        print(f"\n🔍 [{i}/11] Analizando: {domain}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/without-apis",
                json=domain,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                results[domain] = result
                
                # Extraer datos clave
                detection = result.get('detection_summary', {})
                public_libs = result.get('public_libraries', {})
                website_analysis = result.get('website_analysis', {})
                fb_transparency = result.get('facebook_transparency', {})
                
                # Detectar anomalías
                fb_ad_lib = public_libs.get('facebook_ad_library', False)
                google_ad_lib = public_libs.get('google_transparency', False)
                has_ads = detection.get('has_ads_detected', False)
                fb_transparency_ads = fb_transparency.get('ads_in_circulation', False)
                
                print(f"   📊 Has Ads: {has_ads}")
                print(f"   📘 Facebook Ad Library: {fb_ad_lib}")
                print(f"   🔍 Google Ad Library: {google_ad_lib}")
                print(f"   🌐 Facebook Transparency: {fb_transparency_ads}")
                print(f"   📄 Landing Pages: {website_analysis.get('landing_pages_found', False)}")
                print(f"   🟡 JavaScript Events: {website_analysis.get('javascript_events', False)}")
                print(f"   🎯 Third Party Ads: {website_analysis.get('third_party_ads', False)}")
                
                # Registrar anomalías
                if fb_ad_lib:
                    anomalies["facebook_ad_library_positive"].append(domain)
                
                if not google_ad_lib:
                    anomalies["google_ad_library_zero"].append(domain)
                
                # Verificar si TODOS los componentes web son false
                if not any([
                    website_analysis.get('landing_pages_found', False),
                    website_analysis.get('javascript_events', False),
                    website_analysis.get('third_party_ads', False),
                    website_analysis.get('tracking_detected', False)
                ]):
                    anomalies["all_components_false"].append(domain)
                
                # Facebook Library vs Transparency mismatch
                if fb_ad_lib and not fb_transparency_ads:
                    anomalies["facebook_library_vs_transparency_mismatch"].append(domain)
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   💥 Excepción: {str(e)}")
        
        # Pausa entre requests
        if i < len(test_domains):
            time.sleep(3)
    
    # Resumen de anomalías
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE ANOMALÍAS DETECTADAS")
    print("=" * 80)
    
    print(f"\n🟢 Facebook Ad Library POSITIVO ({len(anomalies['facebook_ad_library_positive'])}/11):")
    for domain in anomalies['facebook_ad_library_positive']:
        print(f"   • {domain}")
    
    print(f"\n🔴 Google Ad Library CERO ({len(anomalies['google_ad_library_zero'])}/11):")
    print(f"   • Todas las {len(anomalies['google_ad_library_zero'])} páginas dieron negativo")
    
    print(f"\n🔴 Componentes Web TODOS FALSE ({len(anomalies['all_components_false'])}/11):")
    for domain in anomalies['all_components_false']:
        print(f"   • {domain}")
    
    print(f"\n🟡 Facebook Library vs Transparency MISMATCH ({len(anomalies['facebook_library_vs_transparency_mismatch'])}/11):")
    for domain in anomalies['facebook_library_vs_transparency_mismatch']:
        print(f"   • {domain} (Library=SÍ, Transparency=NO)")
    
    return results, anomalies

def deep_analysis_specific_domains():
    """Análisis profundo de dominios específicos para entender las anomalías"""
    
    print("\n" + "=" * 80)
    print("🔬 ANÁLISIS PROFUNDO DE CASOS ESPECÍFICOS")
    print("=" * 80)
    
    # Casos de interés
    test_cases = [
        {
            "domain": "nike.com",
            "expected": "Debería tener ads (marca global con presupuesto masivo)",
            "focus": "¿Por qué no detecta componentes web?"
        },
        {
            "domain": "adidas.com", 
            "expected": "Debería tener ads (competidor directo de Nike)",
            "focus": "¿Por qué no detecta Google Ads?"
        },
        {
            "domain": "saq.com",
            "expected": "Facebook Ad Library positivo",
            "focus": "¿Por qué Facebook Transparency no coincide?"
        },
        {
            "domain": "repsol.es",
            "expected": "Único con Has Ads = True",
            "focus": "¿Qué detectó que otros no?"
        }
    ]
    
    for case in test_cases:
        print(f"\n🎯 CASO: {case['domain']}")
        print(f"   📝 Expectativa: {case['expected']}")
        print(f"   🔍 Foco: {case['focus']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/without-apis",
                json={"domain": case['domain']},
                params={"include_details": True},  # Solicitar detalles completos
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Mostrar detalles completos
                if 'detailed_analysis' in result:
                    detailed = result['detailed_analysis']
                    print(f"   📊 Tracking Scripts: {len(detailed.get('tracking_scripts', []))}")
                    print(f"   🔗 Third Party Domains: {len(detailed.get('third_party_domains', []))}")
                    print(f"   📄 Meta Tags Found: {len(detailed.get('meta_tags', []))}")
                    
                    # Mostrar algunos ejemplos
                    if detailed.get('tracking_scripts'):
                        print(f"   📜 Ejemplo tracking: {detailed['tracking_scripts'][0][:50]}...")
                    
                    if detailed.get('third_party_domains'):
                        print(f"   🌐 Ejemplo 3rd party: {detailed['third_party_domains'][0]}")
                
                # Mostrar sources detected
                sources = result.get('detection_summary', {}).get('sources_detected', [])
                if sources:
                    print(f"   ✅ Sources detectados: {', '.join(sources)}")
                else:
                    print(f"   ❌ No sources detectados")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    return True

if __name__ == "__main__":
    results, anomalies = analyze_anomalies()
    deep_analysis_specific_domains()
    
    print(f"\n🎯 ANÁLISIS COMPLETADO")
    print(f"Datos guardados para investigación de mejoras algorítmicas")