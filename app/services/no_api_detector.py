from typing import Dict, List
from .tracking_detector import TrackingDetector
from .public_scrapers import FacebookAdLibraryScraper, GoogleTransparencyScraper
import asyncio


class NoAPIAdsDetector:
    """Detector de anuncios sin usar APIs, combinando múltiples métodos"""
    
    def __init__(self):
        self.tracking_detector = TrackingDetector()
        self.facebook_scraper = FacebookAdLibraryScraper()
        self.google_scraper = GoogleTransparencyScraper()
    
    async def analyze_domain_comprehensive(self, domain: str) -> Dict:
        """Análisis completo de un dominio usando todos los métodos sin API"""
        
        # Ejecutar todos los análisis en paralelo
        results = await asyncio.gather(
            self.tracking_detector.analyze_website(domain),
            self.facebook_scraper.search_advertiser(domain),
            self.google_scraper.search_advertiser(domain),
            return_exceptions=True
        )
        
        tracking_result = results[0] if not isinstance(results[0], Exception) else None
        facebook_result = results[1] if not isinstance(results[1], Exception) else None
        google_result = results[2] if not isinstance(results[2], Exception) else None
        
        # Calcular score combinado
        combined_score = self.calculate_combined_score(tracking_result, facebook_result, google_result)
        
        # Determinar probabilidad final
        has_ads_probability = combined_score['final_score']
        likely_has_ads = has_ads_probability >= 40  # Umbral del 40%
        
        return {
            'domain': domain,
            'likely_has_ads': likely_has_ads,
            'probability_score': has_ads_probability,
            'confidence_level': self.get_confidence_level(has_ads_probability),
            'recommendation': self.get_recommendation(has_ads_probability),
            'detailed_analysis': {
                'website_tracking': tracking_result,
                'facebook_ad_library': facebook_result,
                'google_transparency': google_result
            },
            'summary': combined_score,
            'next_steps': self.get_next_steps(has_ads_probability)
        }
    
    def calculate_combined_score(self, tracking_result: Dict, facebook_result: Dict, google_result: Dict) -> Dict:
        """Calcula un score combinado de todos los métodos de detección"""
        
        scores = {
            'tracking_score': 0,
            'facebook_score': 0,
            'google_score': 0,
            'final_score': 0
        }
        
        weights = {
            'tracking': 0.5,    # 50% - Más confiable porque analiza el sitio real
            'facebook': 0.3,    # 30% - Biblioteca pública
            'google': 0.2       # 20% - Menos información disponible públicamente
        }
        
        # Score del tracking detector
        if tracking_result and tracking_result.get('probability_score'):
            scores['tracking_score'] = tracking_result['probability_score']
        
        # Score de Facebook Ad Library
        if facebook_result and facebook_result.get('has_ads'):
            base_score = 60 if facebook_result.get('advertiser_found') else 40
            confidence_bonus = facebook_result.get('confidence', 0) * 0.4
            scores['facebook_score'] = min(base_score + confidence_bonus, 100)
        
        # Score de Google Transparency
        if google_result and google_result.get('has_ads'):
            base_score = 50 if google_result.get('advertiser_found') else 30
            confidence_bonus = google_result.get('confidence', 0) * 0.3
            scores['google_score'] = min(base_score + confidence_bonus, 100)
        
        # Calcular score final ponderado
        final_score = (
            scores['tracking_score'] * weights['tracking'] +
            scores['facebook_score'] * weights['facebook'] +
            scores['google_score'] * weights['google']
        )
        
        scores['final_score'] = round(final_score, 1)
        
        # Información adicional
        scores['methods_detected'] = sum([
            1 if scores['tracking_score'] > 30 else 0,
            1 if scores['facebook_score'] > 0 else 0,
            1 if scores['google_score'] > 0 else 0
        ])
        
        scores['strongest_indicator'] = max(scores.keys(), key=lambda k: scores[k] if k != 'final_score' and k != 'methods_detected' else 0)
        
        return scores
    
    def get_confidence_level(self, score: float) -> str:
        """Devuelve el nivel de confianza basado en el score"""
        if score >= 80:
            return "Muy Alta"
        elif score >= 60:
            return "Alta"
        elif score >= 40:
            return "Media"
        elif score >= 20:
            return "Baja"
        else:
            return "Muy Baja"
    
    def get_recommendation(self, score: float) -> str:
        """Devuelve una recomendación basada en el score"""
        if score >= 70:
            return "🟢 ALTA PRIORIDAD - Muy probable que tenga anuncios activos. Usar APIs para obtener detalles."
        elif score >= 50:
            return "🟡 PRIORIDAD MEDIA - Probable actividad publicitaria. Verificar con APIs."
        elif score >= 30:
            return "🟠 PRIORIDAD BAJA - Posible actividad publicitaria. Considerar verificación manual."
        else:
            return "🔴 NO PRIORITARIO - Poco probable que tenga anuncios activos."
    
    def get_next_steps(self, score: float) -> List[str]:
        """Sugiere próximos pasos basados en el score"""
        steps = []
        
        if score >= 70:
            steps.extend([
                "Usar Google Ads API para obtener detalles de anuncios",
                "Usar Meta Marketing API para información de Facebook/Instagram ads",
                "Analizar competencia directa",
                "Monitorear cambios en actividad publicitaria"
            ])
        elif score >= 50:
            steps.extend([
                "Verificar manualmente en Facebook Ad Library",
                "Buscar en Google Ads Transparency Center",
                "Considerar usar APIs si el dominio es estratégico",
                "Revisar presencia en redes sociales"
            ])
        elif score >= 30:
            steps.extend([
                "Verificación manual recomendada",
                "Revisar sitio web para cambios en tracking",
                "Monitorear durante un período más largo",
                "Analizar contexto de la industria"
            ])
        else:
            steps.extend([
                "No requiere acción inmediata",
                "Revisar periódicamente",
                "Enfocar recursos en dominios con mayor probabilidad"
            ])
        
        return steps
    
    async def batch_analyze_domains(self, domains: List[str], max_concurrent: int = 5) -> List[Dict]:
        """Analiza múltiples dominios en lotes para evitar sobrecarga"""
        
        results = []
        
        # Procesar en lotes
        for i in range(0, len(domains), max_concurrent):
            batch = domains[i:i + max_concurrent]
            
            batch_results = await asyncio.gather(
                *[self.analyze_domain_comprehensive(domain) for domain in batch],
                return_exceptions=True
            )
            
            # Filtrar excepciones y agregar resultados válidos
            for result in batch_results:
                if not isinstance(result, Exception):
                    results.append(result)
                else:
                    # Crear resultado de error
                    results.append({
                        'domain': 'unknown',
                        'likely_has_ads': False,
                        'probability_score': 0,
                        'error': str(result)
                    })
            
            # Pequeña pausa entre lotes
            await asyncio.sleep(1)
        
        return results
    
    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """Genera un reporte resumen de múltiples análisis"""
        
        total_domains = len(results)
        high_priority = len([r for r in results if r.get('probability_score', 0) >= 70])
        medium_priority = len([r for r in results if 50 <= r.get('probability_score', 0) < 70])
        low_priority = len([r for r in results if 30 <= r.get('probability_score', 0) < 50])
        no_priority = len([r for r in results if r.get('probability_score', 0) < 30])
        
        # Dominios de alta prioridad para APIs
        api_candidates = [r for r in results if r.get('probability_score', 0) >= 50]
        api_candidates.sort(key=lambda x: x.get('probability_score', 0), reverse=True)
        
        return {
            'total_domains_analyzed': total_domains,
            'priority_distribution': {
                'high_priority': high_priority,
                'medium_priority': medium_priority,
                'low_priority': low_priority,
                'no_priority': no_priority
            },
            'api_candidates': api_candidates[:20],  # Top 20 candidatos
            'estimated_api_calls_needed': len(api_candidates),
            'potential_savings': f"{((total_domains - len(api_candidates)) / total_domains * 100):.1f}% menos llamadas API"
        }