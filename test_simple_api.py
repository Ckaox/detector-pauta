import asyncio
import aiohttp
import json

async def test_ultra_simple_api():
    """Prueba la nueva API ultra-simplificada con solo 2 endpoints"""
    print("🚀 PROBANDO API ULTRA-SIMPLIFICADA V4.0")
    print("=" * 70)
    print("📊 Solo 2 endpoints: /without-apis y /with-apis")
    print("🔗 Input flexible: dominio, URL Facebook o JSON")
    print("📘 Transparencia Facebook SIEMPRE incluida")
    print("=" * 70)
    
    # Test cases con diferentes tipos de input
    test_cases = [
        {
            "name": "Dominio simple",
            "input": "nike.com",
            "description": "Input como string de dominio"
        },
        {
            "name": "URL de Facebook",
            "input": "https://facebook.com/nike",
            "description": "Input como URL directa de Facebook"
        },
        {
            "name": "JSON completo",
            "input": {
                "domain": "apple.com",
                "facebook_url": "https://facebook.com/Apple"
            },
            "description": "Input como JSON con dominio y Facebook"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        print("\n📊 1. TESTING ENDPOINT SIN APIs")
        print("=" * 50)
        
        for test_case in test_cases:
            print(f"\n🔍 {test_case['name']}: {test_case['description']}")
            print(f"Input: {test_case['input']}")
            
            try:
                async with session.post(
                    "https://ads-checker-api.onrender.com/api/v1/without-apis",
                    json=test_case['input'],
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Mostrar resultado estructurado
                        input_info = result.get('input', {})
                        detection = result.get('detection_summary', {})
                        fb_transparency = result.get('facebook_transparency', {})
                        
                        print(f"✅ RESULTADO:")
                        print(f"   📝 Dominio procesado: {input_info.get('domain', 'N/A')}")
                        print(f"   🔗 Facebook URL: {input_info.get('facebook_url', 'Ninguna')}")
                        print(f"   📊 Score general: {detection.get('overall_score', 0):.1f}%")
                        print(f"   🎯 Ads detectados: {'✅' if detection.get('has_ads_detected', False) else '❌'}")
                        print(f"   🔥 Prioridad: {detection.get('priority', 'UNKNOWN')}")
                        print(f"   📘 FB Transparencia:")
                        print(f"      • Página encontrada: {'✅' if fb_transparency.get('page_found', False) else '❌'}")
                        print(f"      • Anuncios en circulación: {'✅' if fb_transparency.get('ads_in_circulation', False) else '❌'}")
                        print(f"      • Confianza: {fb_transparency.get('confidence', 0)}%")
                        print(f"   🔍 Fuentes detectadas: {len(detection.get('sources_detected', []))} métodos")
                        
                        if detection.get('sources_detected'):
                            print(f"      Métodos: {', '.join(detection['sources_detected'])}")
                        
                    else:
                        error_text = await response.text()
                        print(f"❌ Error HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print("-" * 40)
        
        # Test de transparencia específica con URL directa de Facebook
        print(f"\n📘 2. TESTING CON URL DIRECTA DE FACEBOOK")
        print("=" * 50)
        
        facebook_test = {
            "domain": "apple.com",
            "facebook_url": "https://www.facebook.com/Apple"
        }
        
        print(f"🔍 Probando con URL específica de Apple en Facebook...")
        print(f"Input: {facebook_test}")
        
        try:
            async with session.post(
                "https://ads-checker-api.onrender.com/api/v1/without-apis",
                json=facebook_test,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    fb_transparency = result.get('facebook_transparency', {})
                    detection = result.get('detection_summary', {})
                    
                    print(f"✅ RESULTADO CON URL ESPECÍFICA:")
                    print(f"   📘 Facebook Transparencia:")
                    print(f"      • Página encontrada: {'✅' if fb_transparency.get('page_found', False) else '❌'}")
                    print(f"      • Anuncios en circulación: {'✅' if fb_transparency.get('ads_in_circulation', False) else '❌'}")
                    print(f"      • Evidencia encontrada: {len(fb_transparency.get('evidence', []))} items")
                    print(f"   📊 Score boosted: {detection.get('overall_score', 0):.1f}%")
                    
                    if fb_transparency.get('evidence'):
                        print(f"   🔍 Evidencia:")
                        for evidence in fb_transparency.get('evidence', [])[:3]:
                            print(f"      • {evidence}")
                
                else:
                    error_text = await response.text()
                    print(f"❌ Error HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test del endpoint con APIs (simulado - sin ejecutar para no gastar créditos)
        print(f"\n💰 3. ESTRUCTURA DEL ENDPOINT CON APIs")
        print("=" * 50)
        print("📝 Input sería idéntico al endpoint sin APIs:")
        print("   • Dominio: 'nike.com'")
        print("   • URL FB: 'https://facebook.com/nike'") 
        print("   • JSON: {'domain': 'nike.com', 'facebook_url': '...'}")
        print("")
        print("📊 Response incluiría:")
        print("   ✅ Google Ads API data (oficial)")
        print("   ✅ Meta Marketing API data (oficial)")
        print("   ✅ Facebook Transparency (bonus gratuito)")
        print("   ✅ JSON unificado y estructurado")
        print("   💰 Costo: Consume créditos de APIs")

    print(f"\n🎯 BENEFICIOS DE LA API ULTRA-SIMPLIFICADA:")
    print("=" * 70)
    print("✅ Solo 2 endpoints: máxima simplicidad")
    print("✅ Input flexible: dominio, URL Facebook o JSON")
    print("✅ Facebook Transparency siempre incluida automáticamente")
    print("✅ JSON response consistente y estructurado")
    print("✅ Transparencia específica con URL directa de Facebook")
    print("✅ Boost automático de score si FB detecta anuncios")
    print("✅ Perfecto para integración en cualquier sistema")

if __name__ == "__main__":
    asyncio.run(test_ultra_simple_api())