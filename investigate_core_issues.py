#!/usr/bin/env python3
"""
🔍 Investigación específica de los problemas reportados:
1. ¿Por qué solo Repsol y SAQ detectaron Facebook Ad Library?
2. ¿Por qué ninguna detectó Google Ad Library?
3. ¿Por qué discrepancia entre Facebook Ad Library y Transparency?
"""

import requests
import json
import time

BASE_URL = "https://ads-checker-api.onrender.com"

def investigate_specific_issues():
    """Investiga los problemas específicos reportados"""
    
    # Los dominios que reportaste
    test_domains = [
        "rockler.com",
        "nike.com", 
        "moodfabrics.com",
        "primor.eu",
        "druni.es",
        "scufgaming.com",
        "adidas.com",
        "saq.com",         # ✅ Facebook Ad Library (pero 0 Transparency)
        "macron.com",
        "paperpapers.com",
        "repsol.es"        # ✅ Facebook Ad Library + Has Ads = True (pero 0 Transparency)
    ]
    
    print("🔍 INVESTIGACIÓN ESPECÍFICA DE PROBLEMAS")
    print("=" * 70)
    print("Enfoque en:")
    print("1. Facebook Ad Library: Solo 2/11 positivos (raro)")
    print("2. Google Ad Library: 0/11 positivos (muy raro)")
    print("3. Facebook Library vs Transparency mismatch")
    print("=" * 70)
    
    facebook_library_results = {}
    google_library_results = {}
    transparency_results = {}
    
    for i, domain in enumerate(test_domains, 1):
        print(f"\n🎯 [{i}/11] INVESTIGANDO: {domain}")
        
        try:
            # Hacer request con include_details=True para ver datos internos
            response = requests.post(
                f"{BASE_URL}/api/v1/without-apis",
                json=domain,
                params={"include_details": True},
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extraer datos específicos
                public_libs = result.get('public_libraries', {})
                fb_transparency = result.get('facebook_transparency', {})
                detection = result.get('detection_summary', {})
                
                fb_lib = public_libs.get('facebook_ad_library', False)
                google_lib = public_libs.get('google_transparency', False)
                fb_trans = fb_transparency.get('ads_in_circulation', False)
                has_ads = detection.get('has_ads_detected', False)
                overall_score = detection.get('overall_score', 0)
                
                # Guardar resultados
                facebook_library_results[domain] = fb_lib
                google_library_results[domain] = google_lib
                transparency_results[domain] = fb_trans
                
                print(f"   📊 Overall Score: {overall_score}")
                print(f"   🎯 Has Ads: {has_ads}")
                print(f"   📘 Facebook Ad Library: {fb_lib}")
                print(f"   🔍 Google Ad Library: {google_lib}")
                print(f"   🌐 Facebook Transparency: {fb_trans}")
                
                # Si tenemos detailed_analysis, mostrar datos internos
                if 'detailed_analysis' in result:
                    detailed = result['detailed_analysis']
                    ultra_analysis = detailed.get('ultra_analysis', {})
                    basic_detection = ultra_analysis.get('basic_detection', {})
                    
                    if basic_detection and 'detailed_analysis' in basic_detection:
                        internal_data = basic_detection['detailed_analysis']
                        
                        # Facebook Ad Library interno
                        fb_internal = internal_data.get('facebook_ad_library', {})
                        if fb_internal:
                            print(f"   📋 FB Library Internal:")
                            print(f"      - Has Ads: {fb_internal.get('has_ads', 'N/A')}")
                            print(f"      - Confidence: {fb_internal.get('confidence', 'N/A')}")
                            print(f"      - Message: {fb_internal.get('message', 'N/A')[:60]}...")
                        
                        # Google Transparency interno
                        google_internal = internal_data.get('google_transparency', {})
                        if google_internal:
                            print(f"   📋 Google Internal:")
                            print(f"      - Has Ads: {google_internal.get('has_ads', 'N/A')}")
                            print(f"      - Confidence: {google_internal.get('confidence', 'N/A')}")
                            print(f"      - Message: {google_internal.get('message', 'N/A')[:60]}...")
                
                # Facebook Transparency detalles
                if fb_transparency:
                    print(f"   📋 FB Transparency Internal:")
                    print(f"      - Page Found: {fb_transparency.get('page_found', 'N/A')}")
                    print(f"      - Confidence: {fb_transparency.get('confidence', 'N/A')}")
                    print(f"      - Evidence Count: {len(fb_transparency.get('evidence', []))}")
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        # Pausa para no sobrecargar
        if i < len(test_domains):
            time.sleep(2)
    
    # Análisis de patrones
    print(f"\n" + "=" * 70)
    print("📊 ANÁLISIS DE PATRONES ENCONTRADOS")
    print("=" * 70)
    
    # Facebook Ad Library
    fb_positives = [domain for domain, result in facebook_library_results.items() if result]
    print(f"\n📘 Facebook Ad Library POSITIVOS ({len(fb_positives)}/11):")
    for domain in fb_positives:
        transparency_status = "✅ Sí" if transparency_results.get(domain, False) else "❌ No"
        print(f"   • {domain} (Transparency: {transparency_status})")
    
    # Google Ad Library  
    google_positives = [domain for domain, result in google_library_results.items() if result]
    print(f"\n🔍 Google Ad Library POSITIVOS ({len(google_positives)}/11):")
    if google_positives:
        for domain in google_positives:
            print(f"   • {domain}")
    else:
        print("   ❌ NINGUNO - Esto es muy extraño para marcas grandes")
    
    # Discrepancias
    discrepancies = []
    for domain in facebook_library_results:
        fb_lib = facebook_library_results[domain]
        fb_trans = transparency_results.get(domain, False)
        if fb_lib and not fb_trans:
            discrepancies.append(domain)
    
    print(f"\n🟡 DISCREPANCIAS FB Library vs Transparency ({len(discrepancies)}):")
    for domain in discrepancies:
        print(f"   • {domain} (Library: SÍ, Transparency: NO)")
    
    return {
        'facebook_library': facebook_library_results,
        'google_library': google_library_results, 
        'transparency': transparency_results,
        'discrepancies': discrepancies
    }

def analyze_why_google_fails():
    """Analiza específicamente por qué Google Ad Library no detecta nada"""
    
    print(f"\n" + "=" * 70)
    print("🔍 ANÁLISIS ESPECÍFICO: ¿Por qué Google Ad Library falla?")
    print("=" * 70)
    
    # Dominios que DEBERÍAN tener Google Ads
    should_have_google_ads = [
        "nike.com",     # Marca global masiva
        "adidas.com",   # Competidor directo de Nike
        "booking.com",  # Travel con mucho ad spend
        "amazon.com"    # E-commerce gigante
    ]
    
    for domain in should_have_google_ads:
        print(f"\n🎯 Investigando Google Ads en: {domain}")
        print(f"   💭 Expectativa: DEBERÍA tener Google Ads (marca global)")
        
        # Hacer test específico
        # (En este punto necesitaríamos acceso directo al Google Transparency Center)
        print(f"   🔍 Resultado API: Pendiente de análisis detallado...")

if __name__ == "__main__":
    results = investigate_specific_issues()
    analyze_why_google_fails()
    
    print(f"\n🎯 CONCLUSIONES PRELIMINARES:")
    print("1. Facebook Ad Library: Muy pocos positivos para marcas grandes")
    print("2. Google Ad Library: Cero detecciones (sospechoso)")
    print("3. Facebook Transparency vs Library: Sistemas diferentes")
    print("4. Posibles problemas con scrapers o thresholds muy altos")