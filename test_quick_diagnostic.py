#!/usr/bin/env python3
"""
🔍 Test rápido para diagnosticar problemas específicos
"""

import requests
import json

BASE_URL = "https://ads-checker-api.onrender.com"

def quick_diagnostic():
    """Test rápido de diagnóstico"""
    
    test_cases = [
        "nike.com",      # Debería tener ads
        "repsol.es"      # El único que dio positivo según el usuario
    ]
    
    print("🔍 DIAGNÓSTICO RÁPIDO")
    print("=" * 50)
    
    for domain in test_cases:
        print(f"\n🎯 Analizando: {domain}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/without-apis",
                json=domain,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Datos principales
                detection = result.get('detection_summary', {})
                public_libs = result.get('public_libraries', {})
                website_analysis = result.get('website_analysis', {})
                fb_transparency = result.get('facebook_transparency', {})
                
                print(f"   📊 Has Ads: {detection.get('has_ads_detected', False)}")
                print(f"   📘 Facebook Ad Library: {public_libs.get('facebook_ad_library', False)}")
                print(f"   🔍 Google Transparency: {public_libs.get('google_transparency', False)}")
                print(f"   🌐 Facebook Transparency: {fb_transparency.get('ads_in_circulation', False)}")
                print(f"   📄 Landing Pages: {website_analysis.get('landing_pages_found', False)}")
                print(f"   🟡 JavaScript Events: {website_analysis.get('javascript_events', False)}")
                print(f"   🎯 Third Party Ads: {website_analysis.get('third_party_ads', False)}")
                print(f"   🔄 Tracking Detected: {website_analysis.get('tracking_detected', False)}")
                
                # Score y fuentes
                print(f"   📈 Overall Score: {detection.get('overall_score', 0)}")
                print(f"   🏷️  Sources: {detection.get('sources_detected', [])}")
                
                # Verificar si tenemos detalles más profundos
                if 'detailed_analysis' in result:
                    print(f"   📋 Detailed Analysis disponible: SÍ")
                else:
                    print(f"   📋 Detailed Analysis disponible: NO")
                    
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    print(f"\n🔍 PROBLEMAS IDENTIFICADOS:")
    print("1. Website analysis componentes siempre false")
    print("2. Solo algunas páginas detectan Facebook Ad Library")  
    print("3. Google Transparency siempre false")
    print("4. Mismatch entre Facebook Ad Library y Transparency")

if __name__ == "__main__":
    quick_diagnostic()