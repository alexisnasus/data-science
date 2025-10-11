"""
Script 5: Validador de Datos
Valida y limpia los CSV generados por los scrapers

Uso:
    python 05_validar_datos.py archivo.csv
    python 05_validar_datos.py propiedades_20251010.csv

Output: archivo_limpio.csv + reporte de validación
"""

import pandas as pd
import sys
from pathlib import Path


def validar_precios(df: pd.DataFrame) -> pd.DataFrame:
    """Valida y limpia precios sospechosos"""
    print("\n🔍 VALIDANDO PRECIOS...")
    
    inicial = len(df)
    
    # Eliminar precios nulos
    df = df[df['precio'].notna()]
    
    # Eliminar precios extremadamente bajos (< $10,000)
    df = df[df['precio'] >= 10000]
    
    # Eliminar precios extremadamente altos (> $50,000,000)
    df = df[df['precio'] <= 50000000]
    
    eliminados = inicial - len(df)
    print(f"  • Registros eliminados: {eliminados}")
    print(f"  • Registros válidos: {len(df)}")
    
    return df


def validar_ubicaciones(df: pd.DataFrame) -> pd.DataFrame:
    """Valida datos de ubicación"""
    print("\n📍 VALIDANDO UBICACIONES...")
    
    inicial = len(df)
    
    # Eliminar registros sin comuna
    df = df[df['comuna'].notna()]
    
    eliminados = inicial - len(df)
    print(f"  • Registros sin comuna eliminados: {eliminados}")
    
    return df


def validar_atributos(df: pd.DataFrame) -> pd.DataFrame:
    """Valida atributos numéricos"""
    print("\n🏠 VALIDANDO ATRIBUTOS...")
    
    # Dormitorios válidos (1-20)
    if 'dormitorios' in df.columns:
        antes = len(df)
        df = df[(df['dormitorios'].isna()) | ((df['dormitorios'] >= 1) & (df['dormitorios'] <= 20))]
        print(f"  • Dormitorios fuera de rango eliminados: {antes - len(df)}")
    
    # Baños válidos (1-15)
    if 'banos' in df.columns:
        antes = len(df)
        df = df[(df['banos'].isna()) | ((df['banos'] >= 1) & (df['banos'] <= 15))]
        print(f"  • Baños fuera de rango eliminados: {antes - len(df)}")
    
    # Superficie válida (10-2000 m²)
    if 'superficie_util' in df.columns:
        antes = len(df)
        df = df[(df['superficie_util'].isna()) | ((df['superficie_util'] >= 10) & (df['superficie_util'] <= 2000))]
        print(f"  • Superficies fuera de rango eliminadas: {antes - len(df)}")
    
    return df


def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina registros duplicados"""
    print("\n🧹 ELIMINANDO DUPLICADOS...")
    
    antes = len(df)
    
    # Por URL (más confiable)
    if 'url' in df.columns:
        df = df.drop_duplicates(subset=['url'], keep='first')
    
    # Por título + precio (fallback)
    else:
        df = df.drop_duplicates(subset=['titulo', 'precio'], keep='first')
    
    eliminados = antes - len(df)
    print(f"  • Duplicados eliminados: {eliminados}")
    
    return df


def generar_reporte(df_original: pd.DataFrame, df_limpio: pd.DataFrame, archivo: str):
    """Genera reporte de validación"""
    print("\n" + "="*70)
    print("  📊 REPORTE DE VALIDACIÓN")
    print("="*70)
    
    print(f"\n📁 Archivo: {archivo}")
    print(f"\n📈 DATOS ORIGINALES:")
    print(f"  • Total registros: {len(df_original)}")
    print(f"  • Columnas: {len(df_original.columns)}")
    
    print(f"\n✅ DATOS LIMPIOS:")
    print(f"  • Total registros: {len(df_limpio)}")
    print(f"  • Registros eliminados: {len(df_original) - len(df_limpio)} ({((len(df_original) - len(df_limpio)) / len(df_original) * 100):.1f}%)")
    
    print(f"\n💰 PRECIOS:")
    print(f"  • Promedio: ${df_limpio['precio'].mean():,.0f}")
    print(f"  • Mediana: ${df_limpio['precio'].median():,.0f}")
    print(f"  • Mínimo: ${df_limpio['precio'].min():,.0f}")
    print(f"  • Máximo: ${df_limpio['precio'].max():,.0f}")
    
    print(f"\n📍 UBICACIONES:")
    print(f"  • Comunas únicas: {df_limpio['comuna'].nunique()}")
    
    if 'region' in df_limpio.columns:
        print(f"  • Regiones únicas: {df_limpio['region'].nunique()}")
    
    print(f"\n❓ VALORES FALTANTES:")
    missing = df_limpio.isnull().sum()
    missing_pct = (missing / len(df_limpio) * 100).round(1)
    
    for col in ['dormitorios', 'banos', 'superficie_util', 'estacionamientos']:
        if col in df_limpio.columns:
            print(f"  • {col}: {missing[col]} ({missing_pct[col]}%)")
    
    print("="*70)


def main():
    """Función principal"""
    print("="*70)
    print("  🔍 VALIDADOR Y LIMPIADOR DE DATOS")
    print("="*70)
    
    # Verificar argumento
    if len(sys.argv) < 2:
        print("\n❌ Error: Debe especificar un archivo CSV")
        print("\nUso: python 05_validar_datos.py archivo.csv")
        print("\nEjemplo: python 05_validar_datos.py propiedades_20251010.csv")
        return
    
    archivo = sys.argv[1]
    
    # Verificar que el archivo existe
    if not Path(archivo).exists():
        print(f"\n❌ Error: El archivo '{archivo}' no existe")
        return
    
    # Cargar datos
    print(f"\n📂 Cargando: {archivo}")
    df_original = pd.read_csv(archivo, encoding='utf-8-sig')
    print(f"  • Registros cargados: {len(df_original)}")
    
    # Crear copia para limpieza
    df_limpio = df_original.copy()
    
    # Aplicar validaciones
    df_limpio = validar_precios(df_limpio)
    df_limpio = validar_ubicaciones(df_limpio)
    df_limpio = validar_atributos(df_limpio)
    df_limpio = eliminar_duplicados(df_limpio)
    
    # Generar reporte
    generar_reporte(df_original, df_limpio, archivo)
    
    # Guardar datos limpios
    archivo_limpio = archivo.replace('.csv', '_limpio.csv')
    df_limpio.to_csv(archivo_limpio, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 Archivo limpio guardado: {archivo_limpio}")
    print(f"\n✅ ¡Validación completada!\n")


if __name__ == "__main__":
    main()
