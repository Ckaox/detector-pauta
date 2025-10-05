#!/usr/bin/env python3
"""
🧪 Test para validar el input flexible mejorado
Casos de prueba:
1. Solo dominio → busca Facebook automáticamente  
2. Solo Facebook → extrae dominio automáticamente
3. Ambos juntos → usa directamente sin búsquedas adicionales
4. Diferentes formatos de keys (facebook vs facebook_url)
"""

import requests
import json
import time

# Configuración
BASE_URL = "https://ads-checker-api.onrender.com"
# BASE_URL = "http://localhost:8000"  # Para pruebas locales

def test_flexible_input():
    """Prueba todas las variaciones de input flexible"""
    
    test_cases = [
        # Caso 1: Solo dominio (debe buscar Facebook automáticamente)
        {
            "name": "Solo dominio",
            "data": "apple.com",
            "description": "API debe buscar Facebook de Apple automáticamente"
        },
        
        # Caso 2: Solo Facebook URL (debe extraer dominio automáticamente) 
        {
            "name": "Solo Facebook",
            "data": "https://www.facebook.com/Apple",
            "description": "API debe extraer apple.com automáticamente"
        },
        
        # Caso 3: Ambos con 'facebook_url' (uso directo, sin búsquedas)
        {
            "name": "Ambos con facebook_url",
            "data": {
                "domain": "apple.com",
                "facebook_url": "https://www.facebook.com/Apple"
            },
            "description": "API debe usar ambos directamente sin búsquedas adicionales"
        },
        
        # Caso 4: Ambos con 'facebook' (key alternativa)
        {
            "name": "Ambos con facebook", 
            "data": {
                "domain": "apple.com",
                "facebook": "https://www.facebook.com/Apple"
            },
            "description": "API debe aceptar 'facebook' como key alternativa"
        },
        
        # Caso 5: Solo dominio con Facebook conocido
        {
            "name": "Solo dominio Nike",
            "data": "nike.com", 
            "description": "API debe encontrar Facebook de Nike automáticamente"
        }
    ]
    
    print("🧪 TESTING INPUT FLEXIBLE MEJORADO")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"📄 Descripción: {test_case['description']}")
        print(f"📨 Input: {test_case['data']}")
        
        try:
            # Llamar endpoint sin APIs
            response = requests.post(
                f"{BASE_URL}/without-apis",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                input_parsed = result.get('input', {})
                detection = result.get('detection_summary', {})
                
                print(f"✅ ÉXITO:")
                print(f"   • Dominio parseado: {input_parsed.get('domain', 'N/A')}")
                print(f"   • Facebook parseado: {input_parsed.get('facebook_url', 'N/A')}")
                print(f"   • Ads detectados: {detection.get('has_ads_detected', False)}")
                print(f"   • Fuentes: {len(detection.get('sources_detected', []))}")
                
                # Verificar transparencia de Facebook
                fb_transparency = result.get('facebook_transparency', {})
                if fb_transparency:
                    print(f"   • Transparencia FB: {fb_transparency.get('has_active_ads', 'No detectado')}")
                
            else:
                print(f"❌ ERROR {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"💥 EXCEPCIÓN: {str(e)}")
        
        # Pausa entre tests
        if i < len(test_cases):
            print("⏳ Esperando 3 segundos...")
            time.sleep(3)
    
    print("\n" + "=" * 60)
    print("🎯 Tests completados!")

def test_efficiency_comparison():
    """Compara eficiencia: con búsqueda automática vs input completo"""
    
    print("\n⚡ COMPARACIÓN DE EFICIENCIA")
    print("=" * 60)
    
    # Test 1: Solo dominio (requiere búsqueda de Facebook)
    print("\n🔍 Test 1: Solo dominio (con búsqueda automática)")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/without-apis",
            json="nike.com",
            timeout=90
        )
        elapsed = time.time() - start_time
        print(f"⏱️  Tiempo: {elapsed:.2f} segundos")
        if response.status_code == 200:
            print("✅ Completado con búsqueda automática")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"💥 Error: {str(e)}")
    
    time.sleep(5)
    
    # Test 2: Input completo (sin búsquedas)
    print("\n🚀 Test 2: Input completo (sin búsquedas)")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/without-apis",
            json={
                "domain": "nike.com",
                "facebook": "https://www.facebook.com/nike"
            },
            timeout=90
        )
        elapsed = time.time() - start_time
        print(f"⏱️  Tiempo: {elapsed:.2f} segundos")
        if response.status_code == 200:
            print("✅ Completado sin búsquedas adicionales")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    test_flexible_input()
    test_efficiency_comparison()