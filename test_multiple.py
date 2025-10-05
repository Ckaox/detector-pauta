import asyncio
import aiohttp
import json

# Dominios diversos para probar
TEST_DOMAINS = [
    # E-commerce grandes
    "amazon.com",
    "ebay.com", 
    "shopify.com",
    "etsy.com",
    
    # Marcas de ropa/moda
    "zara.com",
    "hm.com",
    "uniqlo.com",
    "gap.com",
    
    # Tecnología
    "apple.com",
    "microsoft.com",
    "google.com",
    "samsung.com",
    
    # Viajes
    "booking.com",
    "airbnb.com",
    "expedia.com",
    "trivago.com",
    
    # Comida/delivery
    "mcdonalds.com",
    "starbucks.com",
    "dominos.com",
    "ubereats.com",
    
    # Entretenimiento
    "netflix.com",
    "spotify.com",
    "youtube.com",
    "twitch.tv"
]

async def test_domain_quick(session, domain):
    """Testa un dominio y devuelve resultado básico"""
    try:
        async with session.get(
            f"https://ads-checker-api.onrender.com/api/v1/no-api/analyze/{domain}",
            timeout=aiohttp.ClientTimeout(total=90)
        ) as response:
            if response.status == 200:
                result = await response.json()
                score = result.get('probability_score', 0)
                recommendation = result.get('recommendation', 'UNKNOWN')
                likely_has_ads = result.get('likely_has_ads', False)
                
                return {
                    'domain': domain,
                    'score': score,
                    'likely_has_ads': likely_has_ads,
                    'recommendation': recommendation,
                    'status': 'success'
                }
            else:
                return {
                    'domain': domain,
                    'status': 'error',
                    'error': f"HTTP {response.status}"
                }
    except Exception as e:
        return {
            'domain': domain,
            'status': 'error',
            'error': str(e)
        }

async def test_multiple_domains():
    """Testa múltiples dominios y muestra resultados"""
    print("🚀 PROBANDO MÚLTIPLES DOMINIOS CON LA API EN PRODUCCIÓN")
    print("=" * 80)
    print(f"🌐 URL: https://ads-checker-api.onrender.com")
    print(f"📋 Probando {len(TEST_DOMAINS)} dominios...")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for i, domain in enumerate(TEST_DOMAINS, 1):
            print(f"\n🔍 [{i}/{len(TEST_DOMAINS)}] Analizando {domain}...")
            
            result = await test_domain_quick(session, domain)
            results.append(result)
            
            if result['status'] == 'success':
                score = result['score']
                likely_has_ads = result['likely_has_ads']
                
                # Emoticon basado en score
                if score >= 70:
                    priority_emoji = "🔴"
                    priority_text = "ALTA PRIORIDAD"
                elif score >= 30:
                    priority_emoji = "🟡"
                    priority_text = "PRIORIDAD MEDIA"
                else:
                    priority_emoji = "🟢"
                    priority_text = "BAJA PRIORIDAD"
                
                print(f"   📊 Score: {score:.1f}%")
                print(f"   🎯 Ads detectados: {'✅ SÍ' if likely_has_ads else '❌ NO'}")
                print(f"   {priority_emoji} {priority_text}")
                
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown')}")
            
            # Pausa corta entre requests
            await asyncio.sleep(1)
            print("-" * 50)
    
    # Resumen final
    print("\n📊 RESUMEN POR CATEGORÍAS:")
    print("=" * 80)
    
    categories = {
        "E-commerce": ["amazon.com", "ebay.com", "shopify.com", "etsy.com"],
        "Moda/Ropa": ["zara.com", "hm.com", "uniqlo.com", "gap.com"],
        "Tecnología": ["apple.com", "microsoft.com", "google.com", "samsung.com"],
        "Viajes": ["booking.com", "airbnb.com", "expedia.com", "trivago.com"],
        "Comida": ["mcdonalds.com", "starbucks.com", "dominos.com", "ubereats.com"],
        "Entretenimiento": ["netflix.com", "spotify.com", "youtube.com", "twitch.tv"]
    }
    
    successful_results = [r for r in results if r['status'] == 'success']
    
    for category, domains in categories.items():
        print(f"\n📂 {category.upper()}:")
        category_results = [r for r in successful_results if r['domain'] in domains]
        
        if category_results:
            avg_score = sum(r['score'] for r in category_results) / len(category_results)
            high_score_count = len([r for r in category_results if r['score'] >= 50])
            
            print(f"   📈 Score promedio: {avg_score:.1f}%")
            print(f"   🎯 Dominios con alta probabilidad de ads: {high_score_count}/{len(category_results)}")
            
            # Top 3 en la categoría
            sorted_results = sorted(category_results, key=lambda x: x['score'], reverse=True)[:3]
            print(f"   🏆 Top 3:")
            for r in sorted_results:
                emoji = "🔴" if r['score'] >= 70 else "🟡" if r['score'] >= 30 else "🟢"
                print(f"      {emoji} {r['domain']}: {r['score']:.1f}%")
    
    # Estadísticas generales
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print("=" * 80)
    
    if successful_results:
        total_avg = sum(r['score'] for r in successful_results) / len(successful_results)
        high_priority = len([r for r in successful_results if r['score'] >= 70])
        medium_priority = len([r for r in successful_results if r['score'] >= 30 and r['score'] < 70])
        low_priority = len([r for r in successful_results if r['score'] < 30])
        
        print(f"📈 Score promedio general: {total_avg:.1f}%")
        print(f"🔴 Alta prioridad (≥70%): {high_priority} dominios")
        print(f"🟡 Prioridad media (30-69%): {medium_priority} dominios")
        print(f"🟢 Baja prioridad (<30%): {low_priority} dominios")
        
        print(f"\n💡 RECOMENDACIÓN:")
        if high_priority > 0:
            print(f"   🎯 Enfócate primero en los {high_priority} dominios de alta prioridad")
            print(f"   💰 Esto representa el {(high_priority/len(successful_results)*100):.1f}% de los dominios testados")
        else:
            print(f"   🎯 No hay dominios de alta prioridad inmediata")
            print(f"   📋 Revisa los {medium_priority} de prioridad media si tienes presupuesto")

if __name__ == "__main__":
    asyncio.run(test_multiple_domains())