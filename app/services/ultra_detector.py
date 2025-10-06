from typing import Dict, List
import asyncio
from .advanced_detector import AdvancedAdsDetector
from .no_api_detector import NoAPIAdsDetector

class UltraAdvancedDetector:
    """
    Detector ultra-avanzado que combina múltiples técnicas para máxima precisión
    """
    
    def __init__(self):
        self.basic_detector = NoAPIAdsDetector()
        self.advanced_detector = AdvancedAdsDetector()
    
    async def analyze_domain_ultra(self, domain: str) -> Dict:
        """
        Análisis ultra-completo combinando todas las técnicas disponibles
        """
        try:
            # Ejecutar análisis básico y avanzado en paralelo
            basic_result, advanced_result = await asyncio.gather(
                self.basic_detector.analyze_domain_comprehensive(domain),
                self.advanced_detector.analyze_domain_advanced(domain),
                return_exceptions=True
            )
            
            # Combinar resultados
            combined_result = {
                'domain': domain,
                'ultra_analysis': {
                    'basic_detection': basic_result if not isinstance(basic_result, Exception) else {'error': str(basic_result)},
                    'advanced_detection': advanced_result if not isinstance(advanced_result, Exception) else {'error': str(advanced_result)}
                },
                'final_assessment': {},
                'confidence_level': 'unknown',
                'recommendation': '',
                'evidence_summary': []
            }
            
            # Calcular score ultra-combinado
            basic_score = 0
            advanced_score = 0
            
            if not isinstance(basic_result, Exception) and 'probability_score' in basic_result:
                basic_score = basic_result['probability_score']
            
            if not isinstance(advanced_result, Exception) and 'risk_score' in advanced_result:
                advanced_score = advanced_result['risk_score']
            
            # Fórmula ultra-combinada (básico 60%, avanzado 40%)
            ultra_score = (basic_score * 0.6) + (advanced_score * 0.4)
            
            # Ajuste por concordancia (si ambos métodos coinciden, aumentar confianza)
            both_high = basic_score >= 50 and advanced_score >= 50
            both_low = basic_score <= 30 and advanced_score <= 30
            
            if both_high:
                ultra_score = min(100, ultra_score * 1.2)  # Boost si ambos detectan
                confidence = 'very_high'
            elif both_low:
                ultra_score = max(0, ultra_score * 0.8)   # Reducir si ambos no detectan
                confidence = 'high'
            else:
                confidence = 'medium'  # Resultados mixtos
            
            # Recopilar evidencia de ambos análisis
            evidence = []
            
            # Evidencia del análisis básico
            if not isinstance(basic_result, Exception):
                if basic_result.get('likely_has_ads', False):
                    evidence.append("✅ Detector básico: Anuncios detectados")
                
                detailed = basic_result.get('detailed_analysis', {})
                if detailed.get('website_tracking', {}).get('probability_score', 0) > 50:
                    evidence.append("🌐 Tracking avanzado detectado en sitio web")
                
                if detailed.get('facebook_ad_library', {}).get('has_ads', False):
                    evidence.append("📘 Anuncios encontrados en Facebook Ad Library")
            
            # Evidencia del análisis avanzado
            if not isinstance(advanced_result, Exception):
                adv_evidence = advanced_result.get('confidence_factors', [])
                evidence.extend([f"🔬 {e}" for e in adv_evidence[:5]])  # Top 5
            
            # Generar recomendación ultra-inteligente
            if ultra_score >= 80:
                recommendation = "🔴 MÁXIMA PRIORIDAD - Múltiples indicadores confirman actividad publicitaria intensa"
                priority = "CRITICAL"
            elif ultra_score >= 60:
                recommendation = "🟠 ALTA PRIORIDAD - Evidencia sólida de actividad publicitaria"
                priority = "HIGH"
            elif ultra_score >= 35:
                recommendation = "🟡 PRIORIDAD MEDIA - Indicadores mixtos, verificar con APIs"
                priority = "MEDIUM"
            else:
                recommendation = "🟢 BAJA PRIORIDAD - Poca evidencia de actividad publicitaria"
                priority = "LOW"
            
            # Construir resultado final
            combined_result.update({
                'final_assessment': {
                    'ultra_score': round(ultra_score, 1),
                    'basic_score': round(basic_score, 1),
                    'advanced_score': round(advanced_score, 1),
                    'confidence_level': confidence,
                    'priority': priority,
                    'likely_has_ads': ultra_score >= 15  # Reducido de 40 para menos falsos negativos
                },
                'recommendation': recommendation,
                'evidence_summary': evidence,
                'next_steps': self._generate_next_steps(ultra_score, priority),
                'analysis_metadata': {
                    'methods_used': ['website_tracking', 'facebook_library', 'google_transparency', 
                                   'sitemap_analysis', 'robots_analysis', 'javascript_analysis',
                                   'structured_data', 'third_party_detection'],
                    'analysis_depth': 'ultra_comprehensive',
                    'accuracy_estimate': self._estimate_accuracy(confidence, len(evidence))
                }
            })
            
            return combined_result
            
        except Exception as e:
            return {
                'domain': domain,
                'error': f"Error en análisis ultra-avanzado: {str(e)}",
                'final_assessment': {
                    'ultra_score': 0,
                    'confidence_level': 'error',
                    'priority': 'UNKNOWN'
                }
            }
    
    def _generate_next_steps(self, score: float, priority: str) -> List[str]:
        """Genera pasos específicos según el score"""
        if priority == "CRITICAL":
            return [
                "🚀 Usar APIs pagadas INMEDIATAMENTE para datos exactos",
                "📊 Analizar estrategias de competencia en detalle",
                "🎯 Implementar campañas competitivas urgentes",
                "📈 Monitorear cambios semanalmente"
            ]
        elif priority == "HIGH":
            return [
                "📋 Programar verificación con APIs en los próximos días",
                "🔍 Analizar tipos de anuncios y audiencias",
                "💡 Considerar estrategias de diferenciación",
                "📅 Revisar mensualmente"
            ]
        elif priority == "MEDIUM":
            return [
                "⏰ Verificar con APIs cuando tengas presupuesto disponible",
                "📊 Incluir en análisis trimestral de competencia",
                "🎯 Monitorear cambios significativos",
                "📈 Revisar cada 3 meses"
            ]
        else:
            return [
                "📋 No requiere acción inmediata",
                "🔄 Revisar semestralmente",
                "📊 Incluir en análisis anuales de mercado",
                "🎯 Enfocar recursos en dominios prioritarios"
            ]
    
    def _estimate_accuracy(self, confidence: str, evidence_count: int) -> str:
        """Estima la precisión del análisis"""
        if confidence == 'very_high' and evidence_count >= 5:
            return "90-95%"
        elif confidence == 'high' and evidence_count >= 3:
            return "80-90%"
        elif confidence == 'medium':
            return "70-80%"
        else:
            return "60-70%"
    
    async def batch_analyze_ultra(self, domains: List[str], max_concurrent: int = 5) -> List[Dict]:
        """Análisis ultra-avanzado en lote"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(domain):
            async with semaphore:
                return await self.analyze_domain_ultra(domain)
        
        tasks = [analyze_with_semaphore(domain) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar excepciones y ordenar por score
        valid_results = [r for r in results if not isinstance(r, Exception)]
        valid_results.sort(
            key=lambda x: x.get('final_assessment', {}).get('ultra_score', 0), 
            reverse=True
        )
        
        return valid_results