
"""
Script 3: Scraper Incremental
Scrapea datos periódicamente y los agrega a un archivo CSV histórico

Uso:
    python 03_scraper_incremental.py
    
Output: propiedades_historico.csv (se va actualizando)
"""

import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import sys
import importlib.util

# Importar la clase del script 01
spec = importlib.util.spec_from_file_location("scraper", "01_scraper_simple.py")
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)
PortalInmobiliarioScraper = scraper_module.PortalInmobiliarioScraper


def cargar_datos_existentes(archivo: str) -> pd.DataFrame:
    """Carga datos existentes o retorna DataFrame vacío"""
    if os.path.exists(archivo):
        print(f"📂 Cargando datos existentes: {archivo}")
        df = pd.read_csv(archivo, encoding='utf-8-sig')
        print(f"   Registros anteriores: {len(df)}")
        return df
    else:
        print("📝 Archivo no existe, se creará uno nuevo")
        return pd.DataFrame()


def limpiar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina propiedades duplicadas por URL"""
    antes = len(df)
    df = df.drop_duplicates(subset=['url'], keep='last')
    despues = len(df)
    eliminados = antes - despues
    
    if eliminados > 0:
        print(f"🧹 Eliminados {eliminados} duplicados")
    
    return df


def main():
    """Función principal"""
    print("="*70)
    print("  🏠 SCRAPER INCREMENTAL - ACTUALIZACIÓN DE DATOS HISTÓRICOS")
    print("="*70)
    
    # Configuración
    URL_BASE = "https://www.portalinmobiliario.com/arriendo/casa/santiago-metropolitana"
    NUM_PAGINAS = 5
    DELAY = 3
    ARCHIVO_HISTORICO = 'propiedades_historico.csv'
    
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"  • URL: {URL_BASE}")
    print(f"  • Páginas por actualización: {NUM_PAGINAS}")
    print(f"  • Archivo histórico: {ARCHIVO_HISTORICO}")
    
    # Cargar datos existentes
    df_existente = cargar_datos_existentes(ARCHIVO_HISTORICO)
    
    # Scrapear nuevos datos
    print("\n🚀 Iniciando scraping...")
    scraper = PortalInmobiliarioScraper()
    propiedades_nuevas = scraper.scrape_multiples_paginas(URL_BASE, NUM_PAGINAS, DELAY)
    
    if not propiedades_nuevas:
        print("❌ No se extrajeron propiedades nuevas")
        return
    
    # Crear DataFrame de nuevos datos
    df_nuevos = pd.DataFrame(propiedades_nuevas)
    
    # Agregar timestamp de scraping
    df_nuevos['fecha_scraping'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n📊 Nuevos datos:")
    print(f"   Propiedades extraídas: {len(df_nuevos)}")
    
    # Combinar con datos existentes
    if not df_existente.empty:
        df_combinado = pd.concat([df_existente, df_nuevos], ignore_index=True)
    else:
        df_combinado = df_nuevos
    
    # Limpiar duplicados
    df_final = limpiar_duplicados(df_combinado)
    
    # Guardar
    df_final.to_csv(ARCHIVO_HISTORICO, index=False, encoding='utf-8-sig')
    
    # Crear también backup con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_backup = f'backup_propiedades_{timestamp}.csv'
    df_final.to_csv(archivo_backup, index=False, encoding='utf-8-sig')
    
    # Resumen
    print("\n" + "="*70)
    print("  📊 RESUMEN")
    print("="*70)
    print(f"  📂 Registros anteriores: {len(df_existente)}")
    print(f"  ➕ Nuevos registros: {len(df_nuevos)}")
    print(f"  📊 Total en histórico: {len(df_final)}")
    print(f"  💾 Archivo principal: {ARCHIVO_HISTORICO}")
    print(f"  💾 Backup: {archivo_backup}")
    print("="*70)
    
    # Estadísticas
    print(f"\n📈 ESTADÍSTICAS DEL HISTÓRICO:")
    print(f"  • Precio promedio: ${df_final['precio'].mean():,.0f}")
    print(f"  • Precio mínimo: ${df_final['precio'].min():,.0f}")
    print(f"  • Precio máximo: ${df_final['precio'].max():,.0f}")
    print(f"  • Comunas únicas: {df_final['comuna'].nunique()}")
    print(f"  • Propiedades únicas: {df_final['url'].nunique()}")
    
    if 'fecha_scraping' in df_final.columns:
        fechas_unicas = df_final['fecha_scraping'].nunique()
        print(f"  • Actualizaciones realizadas: {fechas_unicas}")
    
    print(f"\n✅ ¡Actualización completada!\n")


if __name__ == "__main__":
    main()
