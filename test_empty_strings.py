#!/usr/bin/env python3
"""
🧪 Test específico para validar manejo de strings vacíos en input
"""

import requests
import json

BASE_URL = "https://ads-checker-api.onrender.com"

def test_empty_strings():
    """Prueba específica para inputs con strings vacíos"""
    
    test_cases = [
        {
            "name": "Domain vacío, Facebook válido",
            "data": {
                "domain": "",
                "facebook_url": "https://www.facebook.com/Apple"
            },
            "should_work": True
        },
        {
            "name": "Domain válido, Facebook vacío", 
            "data": {
                "domain": "apple.com",
                "facebook_url": ""
            },
            "should_work": True
        },
        {
            "name": "Ambos vacíos (debe fallar)",
            "data": {
                "domain": "",
                "facebook_url": ""
            },
            "should_work": False
        },
        {
            "name": "Con key 'facebook' vacía",
            "data": {
                "domain": "apple.com", 
                "facebook": ""
            },
            "should_work": True
        },
        {
            "name": "Solo Facebook con key 'facebook'",
            "data": {
                "domain": "",
                "facebook": "https://www.facebook.com/Apple"
            },
            "should_work": True
        }
    ]
    
    print("🧪 TESTING STRINGS VACÍOS EN INPUT")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"📨 Input: {test_case['data']}")
        print(f"🎯 Debe funcionar: {test_case['should_work']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/without-apis",
                json=test_case['data'],
                timeout=60
            )
            
            if test_case['should_work']:
                if response.status_code == 200:
                    result = response.json()
                    input_parsed = result.get('input', {})
                    print(f"✅ ÉXITO:")
                    print(f"   • Domain parseado: {input_parsed.get('domain', 'N/A')}")
                    print(f"   • Facebook parseado: {input_parsed.get('facebook_url', 'N/A')}")
                else:
                    print(f"❌ FALLÓ (esperaba éxito): {response.status_code} - {response.text}")
            else:
                if response.status_code == 400:
                    print(f"✅ CORRECTO (falló como esperado): {response.status_code}")
                else:
                    print(f"❌ INESPERADO (esperaba error 400): {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"💥 EXCEPCIÓN: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Test de strings vacíos completado!")

if __name__ == "__main__":
    test_empty_strings()