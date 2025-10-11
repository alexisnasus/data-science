"""
Script 4: Scraper Múltiples Regiones
Scrapea varias regiones en paralelo y genera un CSV consolidado

Uso:
    python 04_scraper_multiples_regiones.py
    
Output: propiedades_nacional_YYYYMMDD_HHMMSS.csv
"""

import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import importlib.util

# Importar la clase del script 01
spec = importlib.util.spec_from_file_location("scraper", "01_scraper_simple.py")
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)
PortalInmobiliarioScraper = scraper_module.PortalInmobiliarioScraper


# Configuración de regiones a scrapear
REGIONES_CONFIG = [
    {
        'nombre': 'Región Metropolitana',
        'slug': 'santiago-metropolitana',
        'paginas': 5
    },
    {
        'nombre': 'Valparaíso',
        'slug': 'valparaiso',
        'paginas': 3
    },
    {
        'nombre': 'Biobío',
        'slug': 'bio-bio',
        'paginas': 3
    },
    {
        'nombre': 'Maule',
        'slug': 'maule',
        'paginas': 2
    },
]


def scrapear_region(config: dict, tipo_propiedad: str = 'casa') -> pd.DataFrame:
    """Scrapea una región específica"""
    print("\n" + "="*70)
    print(f"  📍 REGIÓN: {config['nombre'].upper()}")
    print("="*70)
    
    url_base = f"https://www.portalinmobiliario.com/arriendo/{tipo_propiedad}/{config['slug']}"
    
    scraper = PortalInmobiliarioScraper()
    propiedades = scraper.scrape_multiples_paginas(url_base, config['paginas'], delay=3)
    
    if propiedades:
        df = pd.DataFrame(propiedades)
        df['region_scraping'] = config['nombre']
        print(f"\n  ✅ {config['nombre']}: {len(df)} propiedades extraídas")
        return df
    else:
        print(f"\n  ⚠️  {config['nombre']}: Sin datos")
        return pd.DataFrame()


def main():
    """Función principal"""
    print("="*70)
    print("  🗺️  SCRAPER MÚLTIPLES REGIONES - DATOS NACIONALES")
    print("="*70)
    
    print(f"\n📋 REGIONES A SCRAPEAR:")
    for i, region in enumerate(REGIONES_CONFIG, 1):
        print(f"  {i}. {region['nombre']} ({region['paginas']} páginas)")
    
    print(f"\n⏱️  Tiempo estimado: ~{sum(r['paginas'] for r in REGIONES_CONFIG) * 3} segundos")
    
    # Preguntar confirmación
    respuesta = input("\n¿Continuar? (s/n): ").lower()
    if respuesta != 's':
        print("❌ Cancelado")
        return
    
    # Scrapear cada región
    todos_df = []
    
    for region in REGIONES_CONFIG:
        try:
            df_region = scrapear_region(region)
            if not df_region.empty:
                todos_df.append(df_region)
        except Exception as e:
            print(f"  ❌ Error en {region['nombre']}: {e}")
    
    if not todos_df:
        print("\n❌ No se extrajeron datos de ninguna región")
        return
    
    # Combinar todos los DataFrames
    print("\n" + "="*70)
    print("  🔄 CONSOLIDANDO DATOS...")
    print("="*70)
    
    df_consolidado = pd.concat(todos_df, ignore_index=True)
    
    # Agregar timestamp
    df_consolidado['fecha_scraping'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Guardar
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_csv = f'propiedades_nacional_{timestamp}.csv'
    df_consolidado.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
    
    # Resumen por región
    print("\n📊 RESUMEN POR REGIÓN:")
    resumen = df_consolidado.groupby('region_scraping').agg({
        'precio': ['count', 'mean', 'min', 'max'],
        'comuna': 'nunique'
    }).round(0)
    
    print(resumen.to_string())
    
    # Resumen general
    print("\n" + "="*70)
    print("  📊 RESUMEN GENERAL")
    print("="*70)
    print(f"  ✅ Total propiedades: {len(df_consolidado)}")
    print(f"  📍 Regiones: {df_consolidado['region_scraping'].nunique()}")
    print(f"  🏘️  Comunas únicas: {df_consolidado['comuna'].nunique()}")
    print(f"  💰 Precio promedio nacional: ${df_consolidado['precio'].mean():,.0f}")
    print(f"  💾 Archivo: {archivo_csv}")
    print("="*70)
    
    print(f"\n✅ ¡Scraping nacional completado!\n")


if __name__ == "__main__":
    main()
