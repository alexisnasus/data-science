"""
Script 2: Scraper con Configuración Personalizada
Permite configurar parámetros desde la línea de comandos

Uso:
    python 02_scraper_configurable.py
    python 02_scraper_configurable.py --paginas 10 --delay 5
    python 02_scraper_configurable.py --tipo departamento --region valparaiso

Output: propiedades_[tipo]_[region]_YYYYMMDD_HHMMSS.csv
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import importlib.util

# Importar la clase del script 01
spec = importlib.util.spec_from_file_location("scraper", "01_scraper_simple.py")
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)
PortalInmobiliarioScraper = scraper_module.PortalInmobiliarioScraper

import pandas as pd
from datetime import datetime


# Mapeo de regiones disponibles
REGIONES = {
    'metropolitana': 'santiago-metropolitana',
    'valparaiso': 'valparaiso',
    'biobio': 'bio-bio',
    'maule': 'maule',
    'ohiggins': 'libertador-general-bernardo-ohiggins',
}

# Tipos de propiedad disponibles
TIPOS_PROPIEDAD = {
    'casa': 'casa',
    'departamento': 'departamento',
    'oficina': 'oficina',
    'local': 'local-comercial',
}


def crear_url(tipo_propiedad: str, region: str) -> str:
    """Crea la URL base según tipo y región"""
    tipo = TIPOS_PROPIEDAD.get(tipo_propiedad.lower(), 'casa')
    reg = REGIONES.get(region.lower(), 'santiago-metropolitana')
    return f"https://www.portalinmobiliario.com/arriendo/{tipo}/{reg}"


def main():
    """Función principal con argumentos configurables"""
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='🏠 Scraper Portal Inmobiliario - Versión Configurable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python 02_scraper_configurable.py
  python 02_scraper_configurable.py --paginas 10
  python 02_scraper_configurable.py --tipo departamento --region valparaiso
  python 02_scraper_configurable.py --paginas 5 --delay 2 --output mis_datos.csv
        """
    )
    
    parser.add_argument(
        '--tipo',
        type=str,
        default='casa',
        choices=['casa', 'departamento', 'oficina', 'local'],
        help='Tipo de propiedad (default: casa)'
    )
    
    parser.add_argument(
        '--region',
        type=str,
        default='metropolitana',
        choices=['metropolitana', 'valparaiso', 'biobio', 'maule', 'ohiggins'],
        help='Región (default: metropolitana)'
    )
    
    parser.add_argument(
        '--paginas',
        type=int,
        default=5,
        help='Número de páginas a scrapear (default: 5)'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=3,
        help='Segundos de espera entre páginas (default: 3)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Nombre del archivo CSV de salida (opcional)'
    )
    
    args = parser.parse_args()
    
    # Mostrar banner
    print("="*70)
    print("  🏠 SCRAPER PORTAL INMOBILIARIO - VERSIÓN CONFIGURABLE")
    print("="*70)
    
    # Crear URL
    url_base = crear_url(args.tipo, args.region)
    
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"  • Tipo: {args.tipo.upper()}")
    print(f"  • Región: {args.region.upper()}")
    print(f"  • Páginas: {args.paginas}")
    print(f"  • Delay: {args.delay}s")
    print(f"  • URL: {url_base}")
    
    # Ejecutar scraping
    scraper = PortalInmobiliarioScraper()
    propiedades = scraper.scrape_multiples_paginas(url_base, args.paginas, args.delay)
    
    if not propiedades:
        print("❌ No se extrajeron propiedades")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(propiedades)
    
    # Nombre de archivo
    if args.output:
        archivo_csv = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_csv = f'propiedades_{args.tipo}_{args.region}_{timestamp}.csv'
    
    # Guardar
    df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
    
    # Resumen
    print("="*70)
    print("  📊 RESUMEN")
    print("="*70)
    print(f"  ✅ Propiedades: {len(df)}")
    print(f"  💾 Archivo: {archivo_csv}")
    print(f"  💰 Rango precios: ${df['precio'].min():,.0f} - ${df['precio'].max():,.0f}")
    print(f"  📍 Comunas: {df['comuna'].nunique()}")
    print(f"  🛏️  Dormitorios promedio: {df['dormitorios'].mean():.1f}")
    print("="*70)
    
    print(f"\n✅ ¡Listo! Archivo guardado: {archivo_csv}\n")


if __name__ == "__main__":
    main()
