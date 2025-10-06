#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO URGENTE: ¿Por qué solo detectamos 1/11 cuando deberían ser 8/11?
Comparando con datos reales de APIs oficiales
"""

import requests
import json

BASE_URL = "https://ads-checker-api.onrender.com"

def compare_with_official_apis():
    """Compara nuestros resultados con los datos oficiales de APIs"""
    
    # Datos de las APIs oficiales (de la imagen del usuario)
    official_data = {
        "rockler.com": {"google": True, "meta": False},
        "nike.com": {"google": False, "meta": True},
        "moodfabrics.com": {"google": True, "meta": False},
        "primor.eu": {"google": True, "meta": False},
        "druni.es": {"google": True, "meta": True},
        "scufgaming.com": {"google": True, "meta": False},
        "adidas.com": {"google": True, "meta": True},
        "saq.com": {"google": True, "meta": False},
        "macron.com": {"google": True, "meta": True},
        "paperpapers.com": {"google": False, "meta": False},
        "repsol.es": {"google": True, "meta": True}
    }
    
    print("🔍 DIAGNÓSTICO: APIs Oficiales vs Nuestra Detección")
    print("=" * 80)
    print("Datos oficiales:")
    print("Google Ads: 8/11 páginas ✅")
    print("Meta Ads: 5/11 páginas ✅") 
    print("Nuestra API: Solo 1/11 ❌ (PROBLEMA GRAVE)")
    print("=" * 80)
    
    our_results = {}
    false_negatives = []
    
    for domain, official in official_data.items():
        print(f"\n🎯 TESTING: {domain}")
        
        # Datos oficiales
        should_have_google = official['google']
        should_have_meta = official['meta']
        should_have_ads = should_have_google or should_have_meta
        
        print(f"   📊 Official: Google={should_have_google}, Meta={should_have_meta}")
        
        try:
            # Test nuestra API con detalles
            response = requests.post(
                f"{BASE_URL}/api/v1/without-apis",
                json=domain,
                params={"include_details": True},
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extraer nuestros resultados
                detection = result.get('detection_summary', {})
                public_libs = result.get('public_libraries', {})
                website_analysis = result.get('website_analysis', {})
                
                our_has_ads = detection.get('has_ads_detected', False)
                our_google = public_libs.get('google_transparency', False)
                our_facebook = public_libs.get('facebook_ad_library', False)
                our_tracking = website_analysis.get('tracking_detected', False)
                overall_score = detection.get('overall_score', 0)
                sources = detection.get('sources_detected', [])
                
                our_results[domain] = {
                    'has_ads': our_has_ads,
                    'google': our_google,
                    'facebook': our_facebook,
                    'tracking': our_tracking,
                    'score': overall_score,
                    'sources': sources
                }
                
                print(f"   🤖 Our API: Has Ads={our_has_ads}, Google={our_google}, FB={our_facebook}")
                print(f"   📈 Score: {overall_score}%, Sources: {sources}")
                
                # Detectar falsos negativos
                if should_have_ads and not our_has_ads:
                    false_negatives.append(domain)
                    print(f"   ❌ FALSE NEGATIVE! Debería tener ads pero no detectamos")
                elif our_has_ads and should_have_ads:
                    print(f"   ✅ CORRECT DETECTION")
                elif not our_has_ads and not should_have_ads:
                    print(f"   ✅ CORRECT NEGATIVE")
                else:
                    print(f"   ⚠️  FALSE POSITIVE (raro)")
                
                # Análisis de scores bajos
                if should_have_ads and overall_score < 30:
                    print(f"   🔍 SCORE TOO LOW: {overall_score}% (threshold problem?)")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
    
    # Análisis final
    print(f"\n" + "=" * 80)
    print("📊 ANÁLISIS FINAL")
    print("=" * 80)
    
    total_should_have = sum(1 for official in official_data.values() if official['google'] or official['meta'])
    our_detections = sum(1 for result in our_results.values() if result.get('has_ads', False))
    
    print(f"Deberían tener ads: {total_should_have}/11")
    print(f"Nuestras detecciones: {our_detections}/11")
    print(f"Falsos negativos: {len(false_negatives)}/11")
    
    print(f"\n❌ FALSOS NEGATIVOS:")
    for domain in false_negatives:
        official = official_data[domain]
        our = our_results.get(domain, {})
        print(f"   • {domain}: Official(G:{official['google']}, M:{official['meta']}) vs Our(Score: {our.get('score', 0)}%)")
    
    # Recomendaciones específicas
    print(f"\n🔧 PROBLEMAS IDENTIFICADOS:")
    low_scores = [d for d, r in our_results.items() if r.get('score', 0) < 30 and (official_data[d]['google'] or official_data[d]['meta'])]
    if low_scores:
        print(f"1. Scores demasiado bajos en {len(low_scores)} páginas")
    
    no_google_detected = [d for d, r in our_results.items() if not r.get('google', False) and official_data[d]['google']]
    if no_google_detected:
        print(f"2. Google Ads no detectado en {len(no_google_detected)} páginas que SÍ tienen")
    
    no_facebook_detected = [d for d, r in our_results.items() if not r.get('facebook', False) and official_data[d]['meta']]
    if no_facebook_detected:
        print(f"3. Facebook Ads no detectado en {len(no_facebook_detected)} páginas que SÍ tienen")

if __name__ == "__main__":
    compare_with_official_apis()