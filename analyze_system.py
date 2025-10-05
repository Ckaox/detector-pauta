import asyncio
import aiohttp
import json

# Dominios para análisis detallado
ANALYSIS_DOMAINS = [
    "ebay.com",      # Sabemos que tuvo 45% 
    "amazon.com",    # Sabemos que tuvo 15.6%
    "nike.com",      # De tu tabla original
    "google.com",    # Interesante caso
    "facebook.com"   # Meta propio sitio
]

async def get_detailed_analysis(domain):
    """Obtiene análisis detallado de un dominio"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://ads-checker-api.onrender.com/api/v1/no-api/analyze/{domain}",
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
    except Exception as e:
        return {"error": str(e)}

async def analyze_scoring_system():
    """Analiza cómo funciona el sistema de scoring"""
    print("🔍 ANÁLISIS DETALLADO DEL SISTEMA DE SCORING")
    print("=" * 80)
    
    results = {}
    
    for domain in ANALYSIS_DOMAINS:
        print(f"\n📊 ANALIZANDO: {domain}")
        print("-" * 50)
        
        result = await get_detailed_analysis(domain)
        results[domain] = result
        
        if "error" not in result:
            # Datos principales
            score = result.get('probability_score', 0)
            likely_has_ads = result.get('likely_has_ads', False)
            confidence = result.get('confidence_level', 'Unknown')
            
            print(f"✅ RESULTADO GENERAL:")
            print(f"   📊 Score Final: {score:.1f}%")
            print(f"   🎯 Probable ads: {'✅ SÍ' if likely_has_ads else '❌ NO'}")
            print(f"   📋 Confianza: {confidence}")
            
            # Análisis detallado
            detailed = result.get('detailed_analysis', {})
            summary = result.get('summary', {})
            
            if detailed:
                print(f"\n🔬 DESGLOSE DEL SCORING:")
                
                # Tracking del sitio web
                tracking = detailed.get('website_tracking', {})
                tracking_score = tracking.get('probability_score', 0)
                print(f"   🌐 Website Tracking: {tracking_score:.1f}%")
                if tracking_score > 0:
                    fb_detected = tracking.get('facebook_tracking_detected', False)
                    google_detected = tracking.get('google_ads_tracking_detected', False)
                    campaigns_detected = tracking.get('campaign_parameters_detected', False)
                    print(f"      📘 Facebook tracking: {'✅' if fb_detected else '❌'}")
                    print(f"      🔍 Google Ads tracking: {'✅' if google_detected else '❌'}")
                    print(f"      📈 Campaign parameters: {'✅' if campaigns_detected else '❌'}")
                
                # Facebook Ad Library
                facebook = detailed.get('facebook_ad_library', {})
                fb_score = summary.get('facebook_score', 0)
                print(f"   📘 Facebook Ad Library: {fb_score:.1f}%")
                if facebook.get('has_ads', False):
                    estimated_ads = facebook.get('estimated_ads', 0)
                    page_names = facebook.get('page_names', [])
                    print(f"      📊 Anuncios estimados: {estimated_ads}")
                    print(f"      📄 Páginas encontradas: {len(page_names)}")
                
                # Google Transparency
                google = detailed.get('google_transparency', {})
                google_score = summary.get('google_score', 0)
                print(f"   🔍 Google Transparency: {google_score:.1f}%")
                
                # Cálculo final
                if summary:
                    final_score = summary.get('final_score', 0)
                    methods_detected = summary.get('methods_detected', 0)
                    strongest = summary.get('strongest_indicator', 'none')
                    print(f"\n📈 CÁLCULO FINAL:")
                    print(f"   🎯 Score combinado: {final_score:.1f}%")
                    print(f"   🔢 Métodos que detectaron ads: {methods_detected}/3")
                    print(f"   💪 Indicador más fuerte: {strongest}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
        
        print("=" * 50)
        await asyncio.sleep(2)
    
    # Resumen del sistema de scoring
    print(f"\n🧮 CÓMO FUNCIONA EL SISTEMA DE SCORING:")
    print("=" * 80)
    print("📊 El score final se calcula con 3 métodos:")
    print("   1️⃣ Website Tracking Analysis (50% peso)")
    print("      - Busca pixels de Facebook, Google Ads")
    print("      - Detecta parámetros de campañas (utm_, fbclid, gclid)")
    print("      - Analiza scripts de tracking y analytics")
    print("")
    print("   2️⃣ Facebook Ad Library Search (30% peso)")
    print("      - Busca el dominio en la biblioteca pública de Facebook")
    print("      - Cuenta anuncios activos y páginas asociadas")
    print("      - Verifica presencia de campañas activas")
    print("")
    print("   3️⃣ Google Ads Transparency Center (20% peso)")
    print("      - Busca anuncios en el centro de transparencia de Google")
    print("      - Verifica actividad publicitaria reciente")
    print("      - Identifica campañas y anunciantes")
    print("")
    print("🎯 INTERPRETACIÓN DE SCORES:")
    print("   🔴 70-100%: ALTA PRIORIDAD - Muy probable que tenga ads activos")
    print("   🟡 30-69%:  PRIORIDAD MEDIA - Probable actividad publicitaria")
    print("   🟢 0-29%:   BAJA PRIORIDAD - Poco probable que tenga ads")
    
    # Datos que tenemos disponibles
    print(f"\n📋 DATOS DISPONIBLES PARA CADA DOMINIO:")
    print("=" * 80)
    print("✅ Datos que SÍ obtenemos:")
    print("   • Score de probabilidad (0-100%)")
    print("   • Detección de tracking pixels (Facebook, Google)")
    print("   • Presencia en bibliotecas públicas de ads")
    print("   • Parámetros de campañas en URLs")
    print("   • Scripts de analytics y remarketing")
    print("   • Estimación de anuncios activos")
    print("   • Nivel de confianza del análisis")
    print("   • Recomendación de priorización")
    print("")
    print("❌ Datos que NO obtenemos (requieren APIs pagadas):")
    print("   • Número exacto de anuncios activos")
    print("   • Presupuesto de campañas")
    print("   • Segmentación demográfica")
    print("   • Performance metrics (CTR, CPC, etc.)")
    print("   • Creatividades y textos de anuncios")
    print("   • Historial completo de campañas")
    
    # Pasos a seguir
    print(f"\n🚀 PASOS A SEGUIR RECOMENDADOS:")
    print("=" * 80)
    print("1️⃣ FILTRADO INICIAL (ESTE API)")
    print("   • Procesa tu base de datos completa")
    print("   • Identifica dominios con score >30%")
    print("   • Prioriza por score: primero >70%, luego 30-70%")
    print("")
    print("2️⃣ VALIDACIÓN CON APIs PAGADAS")
    print("   • Solo para dominios priorizados (ahorro de costos)")
    print("   • Google Ads API para datos exactos de Google")
    print("   • Meta Marketing API para datos exactos de Facebook")
    print("")
    print("3️⃣ ANÁLISIS Y DECISIONES")
    print("   • Combina datos de filtrado + APIs pagadas")
    print("   • Toma decisiones informadas sobre competencia")
    print("   • Optimiza tus propias campañas basándote en insights")
    
    return results

if __name__ == "__main__":
    asyncio.run(analyze_scoring_system())