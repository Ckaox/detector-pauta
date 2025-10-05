import asyncio
import aiohttp
import json
from datetime import datetime

# Los 10 dominios originales de tu tabla
DOMAINS = [
    "rockler.com",      # Google ✅ (2000), Meta ❌ (0)
    "nike.com",         # Google ❌ (0), Meta ✅ (78)
    "moodfabrics.com",  # Google ✅ (13), Meta ✅ (1)
    "primor.eu",        # Google ✅ (49), Meta ❌ (0)
    "druni.es",         # Google ✅ (40), Meta ❌ (0)
    "scufgaming.com",   # Google ✅ (8), Meta ❌ (0)
    "adidas.com",       # Google ✅ (79), Meta ✅ (22)
    "saq.com",          # Google ✅ (5), Meta ❌ (0)
    "macron.com",       # Google ✅ (100), Meta ✅ (3)
    "paperpapers.com"   # Google ✅ (9), Meta ❌ (0)
]

# Datos esperados según tu tabla original
EXPECTED_DATA = {
    "rockler.com": {"google": True, "meta": False, "google_ads": 2000, "meta_ads": 0},
    "nike.com": {"google": False, "meta": True, "google_ads": 0, "meta_ads": 78},
    "moodfabrics.com": {"google": True, "meta": True, "google_ads": 13, "meta_ads": 1},
    "primor.eu": {"google": True, "meta": False, "google_ads": 49, "meta_ads": 0},
    "druni.es": {"google": True, "meta": False, "google_ads": 40, "meta_ads": 0},
    "scufgaming.com": {"google": True, "meta": False, "google_ads": 8, "meta_ads": 0},
    "adidas.com": {"google": True, "meta": True, "google_ads": 79, "meta_ads": 22},
    "saq.com": {"google": True, "meta": False, "google_ads": 5, "meta_ads": 0},
    "macron.com": {"google": True, "meta": True, "google_ads": 100, "meta_ads": 3},
    "paperpapers.com": {"google": True, "meta": False, "google_ads": 9, "meta_ads": 0}
}

API_URL = "https://ads-checker-api.onrender.com"

async def test_single_domain(session, domain):
    """Testa un dominio individual"""
    try:
        async with session.get(
            f"{API_URL}/api/v1/no-api/analyze/{domain}",
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            
            if response.status == 200:
                result = await response.json()
                return domain, result
            else:
                error_text = await response.text()
                return domain, {"error": f"HTTP {response.status}: {error_text}"}
                
    except Exception as e:
        return domain, {"error": str(e)}

async def test_production_api():
    """Testa la API en producción con los 10 dominios reales"""
    print("🚀 TESTING API EN PRODUCCIÓN")
    print("=" * 80)
    print(f"🌐 URL: {API_URL}")
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for i, domain in enumerate(DOMAINS, 1):
            print(f"\n🔍 [{i}/10] Analizando {domain}...")
            
            domain_name, result = await test_single_domain(session, domain)
            results.append((domain_name, result))
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                score = result.get('probability_score', 0)
                recommendation = result.get('recommendation', 'UNKNOWN')
                priority = "HIGH" if score > 70 else "MEDIUM" if score > 30 else "LOW"
                
                print(f"✅ {domain_name}:")
                print(f"   📊 Score: {score:.1f}%")
                print(f"   🎯 Prioridad: {priority}")
                print(f"   💬 Recomendación: {recommendation}")
                
                # Comparar con datos esperados
                expected = EXPECTED_DATA.get(domain_name, {})
                expected_google = "✅" if expected.get('google', False) else "❌"
                expected_meta = "✅" if expected.get('meta', False) else "❌"
                
                print(f"   📈 ESPERADO:")
                print(f"      Google: {expected_google} ({expected.get('google_ads', 0)} ads)")
                print(f"      Meta: {expected_meta} ({expected.get('meta_ads', 0)} ads)")
                
                # Determinar si la detección fue correcta
                has_ads = expected.get('google', False) or expected.get('meta', False)
                detected_ads = score > 30  # Threshold de 30%
                
                if has_ads == detected_ads:
                    print(f"   🎯 Detección: ✅ CORRECTA")
                else:
                    print(f"   🎯 Detección: ❌ INCORRECTA")
            
            print("-" * 80)
    
    print("\n📊 RESUMEN FINAL:")
    print("=" * 80)
    
    correct_detections = 0
    total_detections = 0
    
    for domain_name, result in results:
        if "error" not in result:
            total_detections += 1
            score = result.get('probability_score', 0)
            expected = EXPECTED_DATA.get(domain_name, {})
            has_ads = expected.get('google', False) or expected.get('meta', False)
            detected_ads = score > 30
            
            if has_ads == detected_ads:
                correct_detections += 1
            
            print(f"📍 {domain_name}: {score:.1f}% - {'✅' if has_ads == detected_ads else '❌'}")
    
    if total_detections > 0:
        accuracy = (correct_detections / total_detections) * 100
        print(f"\n🎯 PRECISIÓN TOTAL: {accuracy:.1f}% ({correct_detections}/{total_detections})")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_production_api())