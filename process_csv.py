#!/usr/bin/env python3
"""
Script para procesar un CSV con dominios y obtener información de ads
No requiere servidor corriendo - procesa todo localmente
"""

import csv
import asyncio
import aiohttp
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import json

# Importar servicios localmente sin necesidad de servidor
sys.path.insert(0, str(Path(__file__).parent))
from app.services.facebook_transparency_advanced import FacebookTransparencyAdvanced
from app.services.tracking_detector import TrackingDetector
from app.services.no_api_detector import NoAPIAdsDetector


class CSVProcessor:
    def __init__(self):
        self.fb_service = FacebookTransparencyAdvanced()
        self.tracking_service = TrackingDetector()
        self.no_api_detector = NoAPIAdsDetector()
        self.results = []
    
    async def analyze_domain(self, domain: str, facebook_url: str = None) -> Dict:
        """Analiza un dominio sin necesidad de APIs"""
        print(f"  📊 Analizando: {domain}...")
        
        try:
            # Análisis completo sin APIs
            result = await self.no_api_detector.analyze_domain_comprehensive(domain)
            
            return {
                "domain": domain,
                "facebook_url": facebook_url or "",
                "has_google_ads": result.get("google_ads", {}).get("has_ads", False),
                "google_confidence": result.get("google_ads", {}).get("confidence", 0),
                "google_tracking": result.get("google_ads", {}).get("tracking_detected", False),
                "has_meta_ads": result.get("meta_ads", {}).get("has_ads", False),
                "meta_ads_count": result.get("meta_ads", {}).get("number_of_ads", 0),
                "meta_page_id": result.get("meta_ads", {}).get("page_id", ""),
                "overall_confidence": result.get("summary", {}).get("total_confidence", 0),
                "likely_has_ads": result.get("summary", {}).get("likely_has_ads", False),
                "platforms": ", ".join(result.get("summary", {}).get("platforms", [])),
                "status": "✅ Completado"
            }
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return {
                "domain": domain,
                "facebook_url": facebook_url or "",
                "has_google_ads": False,
                "google_confidence": 0,
                "google_tracking": False,
                "has_meta_ads": False,
                "meta_ads_count": 0,
                "meta_page_id": "",
                "overall_confidence": 0,
                "likely_has_ads": False,
                "platforms": "",
                "status": f"❌ Error: {str(e)}"
            }
    
    async def process_batch(self, domains: List[Dict], max_concurrent: int = 5):
        """Procesa múltiples dominios concurrentemente"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(item):
            async with semaphore:
                return await self.analyze_domain(
                    item.get("domain"),
                    item.get("facebook_url")
                )
        
        tasks = [process_with_semaphore(item) for item in domains]
        results = await asyncio.gather(*tasks)
        return results
    
    def read_csv(self, input_file: str) -> List[Dict]:
        """Lee el CSV de entrada"""
        domains = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Detectar columnas
            fieldnames = reader.fieldnames
            domain_col = None
            fb_col = None
            
            # Buscar columna de dominio (priorizar "domain" exacto)
            for field in fieldnames:
                if field.lower() == 'domain':
                    domain_col = field
                    break
            
            # Si no se encontró "domain" exacto, buscar variantes
            if not domain_col:
                for field in fieldnames:
                    field_lower = field.lower()
                    if field_lower in ['website', 'site', 'company_domain', 'url'] and 'facebook' not in field_lower:
                        domain_col = field
                        break
            
            # Buscar columna de Facebook (pero no la misma que domain)
            for field in fieldnames:
                if field == domain_col:
                    continue
                field_lower = field.lower()
                if any(word in field_lower for word in ['facebook', 'fb']) or field_lower == 'meta':
                    fb_col = field
                    break
            
            if not domain_col:
                print("❌ Error: No se encontró columna de dominio")
                print(f"Columnas disponibles: {', '.join(fieldnames)}")
                sys.exit(1)
            
            print(f"✅ Columna de dominio detectada: '{domain_col}'")
            if fb_col:
                print(f"✅ Columna de Facebook detectada: '{fb_col}'")
            
            # Leer datos
            for row in reader:
                domain = row.get(domain_col, "").strip()
                if domain:
                    domains.append({
                        "domain": domain,
                        "facebook_url": row.get(fb_col, "").strip() if fb_col else None
                    })
        
        return domains
    
    def write_csv(self, output_file: str):
        """Escribe los resultados a un CSV"""
        if not self.results:
            print("❌ No hay resultados para guardar")
            return
        
        fieldnames = [
            "domain",
            "facebook_url",
            "has_google_ads",
            "google_confidence",
            "google_tracking",
            "has_meta_ads",
            "meta_ads_count",
            "meta_page_id",
            "overall_confidence",
            "likely_has_ads",
            "platforms",
            "status"
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"✅ Resultados guardados en: {output_file}")


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Procesa un CSV con dominios y analiza sus anuncios',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Procesar un CSV simple
  python process_csv.py input.csv

  # Especificar archivo de salida
  python process_csv.py input.csv -o resultados.csv

  # Procesar con más concurrencia (más rápido pero más intensivo)
  python process_csv.py input.csv -c 10

Formato del CSV de entrada:
  - Debe tener una columna con dominios (puede llamarse: domain, website, url, site)
  - Opcionalmente puede tener una columna de Facebook (facebook_url, fb, meta)

Ejemplo:
  domain,facebook_url
  nike.com,https://facebook.com/nike
  adidas.com,
  puma.com,https://facebook.com/puma
        """
    )
    
    parser.add_argument('input', help='Archivo CSV de entrada')
    parser.add_argument('-o', '--output', help='Archivo CSV de salida (default: input_results.csv)')
    parser.add_argument('-c', '--concurrent', type=int, default=5, 
                       help='Número de requests concurrentes (default: 5)')
    
    args = parser.parse_args()
    
    # Validar archivo de entrada
    if not Path(args.input).exists():
        print(f"❌ Error: Archivo '{args.input}' no encontrado")
        sys.exit(1)
    
    # Generar nombre de archivo de salida
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = f"{input_path.stem}_results{input_path.suffix}"
    
    print("=" * 70)
    print("🚀 Procesador de CSV - Ads Checker")
    print("=" * 70)
    print(f"📄 Archivo de entrada: {args.input}")
    print(f"💾 Archivo de salida: {output_file}")
    print(f"⚡ Concurrencia: {args.concurrent} requests simultáneos")
    print("=" * 70)
    print()
    
    processor = CSVProcessor()
    
    # Leer CSV
    print("📖 Leyendo CSV...")
    domains = processor.read_csv(args.input)
    print(f"✅ {len(domains)} dominios encontrados")
    print()
    
    # Procesar
    print(f"⚙️  Procesando {len(domains)} dominios...")
    print()
    
    start_time = datetime.now()
    processor.results = await processor.process_batch(domains, args.concurrent)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    
    # Guardar resultados
    print()
    print("💾 Guardando resultados...")
    processor.write_csv(output_file)
    
    # Estadísticas
    print()
    print("=" * 70)
    print("📊 Estadísticas")
    print("=" * 70)
    
    total = len(processor.results)
    with_google = sum(1 for r in processor.results if r["has_google_ads"])
    with_meta = sum(1 for r in processor.results if r["has_meta_ads"])
    with_any = sum(1 for r in processor.results if r["likely_has_ads"])
    errors = sum(1 for r in processor.results if "Error" in r["status"])
    
    print(f"Total procesados: {total}")
    print(f"Con Google Ads: {with_google} ({with_google/total*100:.1f}%)")
    print(f"Con Meta Ads: {with_meta} ({with_meta/total*100:.1f}%)")
    print(f"Con algún tipo de ads: {with_any} ({with_any/total*100:.1f}%)")
    print(f"Errores: {errors}")
    print(f"Tiempo total: {duration:.1f} segundos")
    print(f"Promedio: {duration/total:.1f} seg/dominio")
    print()
    print(f"✅ Proceso completado - Resultados en: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
