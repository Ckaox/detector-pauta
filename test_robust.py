import asyncio
import aiohttp
import json

DOMAINS = [
    "rockler.com", "nike.com", "moodfabrics.com", "primor.eu", "druni.es",
    "scufgaming.com", "adidas.com", "saq.com", "macron.com", "paperpapers.com"
]

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

async def test_domain(domain):
    print(f"\n🔍 Analizando {domain}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://ads-checker-api.onrender.com/api/v1/no-api/analyze/{domain}",
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    score = result.get('probability_score', 0)
                    recommendation = result.get('recommendation', 'UNKNOWN')
                    
                    print(f"✅ {domain}:")
                    print(f"   📊 Score: {score:.1f}%")
                    print(f"   💬 Recomendación: {recommendation}")
                    
                    # Comparar con datos esperados
                    expected = EXPECTED_DATA.get(domain, {})
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
                        return True
                    else:
                        print(f"   🎯 Detección: ❌ INCORRECTA")
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Error HTTP {response.status}: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

async def main():
    print("🚀 TESTING API EN PRODUCCIÓN - DOMINIO POR DOMINIO")
    print("=" * 60)
    
    correct = 0
    total = 0
    
    for domain in DOMAINS:
        result = await test_domain(domain)
        if result is not None:
            total += 1
            if result:
                correct += 1
        
        print("-" * 60)
        await asyncio.sleep(2)  # Pausa entre requests
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"🎯 Precisión: {correct}/{total} = {(correct/total*100):.1f}%" if total > 0 else "No hay resultados")

if __name__ == "__main__":
    asyncio.run(main())