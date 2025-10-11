"""
Script 1: Scraper Simple
Extrae datos de Portal Inmobiliario y genera CSV

Uso:
    python 01_scraper_simple.py

Output: propiedades_YYYYMMDD_HHMMSS.csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime
from typing import List, Dict, Optional

class PortalInmobiliarioScraper:
    """Scraper para Portal Inmobiliario"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-CL,es;q=0.9',
        })
    
    def extraer_precio(self, precio_text: str) -> Optional[float]:
        """Extrae el precio numérico del texto"""
        try:
            precio_limpio = re.sub(r'[^\d]', '', precio_text)
            return float(precio_limpio) if precio_limpio else None
        except:
            return None
    
    def extraer_superficie(self, texto: str) -> Optional[float]:
        """Extrae superficie del texto"""
        try:
            match = re.search(r'([\d.,]+)\s*m[²2]', texto)
            if match:
                superficie = match.group(1).replace('.', '').replace(',', '.')
                return float(superficie)
        except:
            pass
        return None
    
    def extraer_numero(self, texto: str) -> Optional[int]:
        """Extrae el primer número del texto"""
        try:
            match = re.search(r'\d+', texto)
            return int(match.group()) if match else None
        except:
            return None
    
    def extraer_comuna_region(self, ubicacion_text: str) -> tuple:
        """Extrae comuna y región de la ubicación"""
        try:
            partes = ubicacion_text.split(',')
            if len(partes) >= 2:
                comuna = partes[-2].strip()
                region = partes[-1].strip()
                return comuna, region
            return ubicacion_text.strip(), "Región Metropolitana"
        except:
            return None, None
    
    def extraer_datos_propiedad(self, listado) -> Optional[Dict]:
        """Extrae datos de una propiedad"""
        propiedad = {
            'titulo': None, 'precio': None, 'precio_texto': None,
            'ubicacion': None, 'comuna': None, 'region': None,
            'dormitorios': None, 'banos': None,
            'superficie_total': None, 'superficie_util': None,
            'estacionamientos': None, 'url': None, 'vendedor': None
        }
        
        try:
            # Título
            titulo_elem = listado.find('a', class_='poly-component__title')
            if titulo_elem:
                propiedad['titulo'] = titulo_elem.get_text(strip=True)
                propiedad['url'] = titulo_elem.get('href')
            
            # Precio
            precio_elem = listado.find('span', class_='andes-money-amount__fraction')
            if precio_elem:
                precio_texto = precio_elem.get_text(strip=True)
                propiedad['precio_texto'] = f"${precio_texto}"
                propiedad['precio'] = self.extraer_precio(precio_texto)
            
            # Ubicación
            ubicacion_elem = listado.find('span', class_='poly-component__location')
            if ubicacion_elem:
                ubicacion = ubicacion_elem.get_text(strip=True)
                propiedad['ubicacion'] = ubicacion
                comuna, region = self.extraer_comuna_region(ubicacion)
                propiedad['comuna'] = comuna
                propiedad['region'] = region
            
            # Vendedor
            vendedor_elem = listado.find('span', class_='poly-component__seller')
            if vendedor_elem:
                propiedad['vendedor'] = vendedor_elem.get_text(strip=True).replace('Por ', '')
            
            # Atributos
            atributos = listado.find_all('li', class_='poly-attributes_list__item')
            for atributo in atributos:
                texto = atributo.get_text(strip=True).lower()
                
                if 'dorm' in texto or 'habitac' in texto:
                    propiedad['dormitorios'] = self.extraer_numero(texto)
                elif 'baño' in texto:
                    propiedad['banos'] = self.extraer_numero(texto)
                elif 'm²' in texto or 'm2' in texto:
                    if 'total' in texto:
                        propiedad['superficie_total'] = self.extraer_superficie(texto)
                    elif 'útil' in texto or 'util' in texto:
                        propiedad['superficie_util'] = self.extraer_superficie(texto)
                    else:
                        if not propiedad['superficie_util']:
                            propiedad['superficie_util'] = self.extraer_superficie(texto)
                elif 'estacionamiento' in texto:
                    propiedad['estacionamientos'] = self.extraer_numero(texto)
            
            if propiedad['titulo'] and propiedad['precio']:
                return propiedad
            
        except Exception as e:
            pass
        
        return None
    
    def scrape_pagina(self, url: str) -> List[Dict]:
        """Extrae propiedades de una página"""
        print(f"  📍 Scrapeando: {url}")
        propiedades_pagina = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            listados = soup.find_all('li', class_='ui-search-layout__item')
            
            print(f"     Encontrados: {len(listados)} listados")
            
            for listado in listados:
                propiedad = self.extraer_datos_propiedad(listado)
                if propiedad:
                    propiedades_pagina.append(propiedad)
            
            print(f"     ✅ Extraídas: {len(propiedades_pagina)} propiedades")
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        return propiedades_pagina
    
    def scrape_multiples_paginas(self, url_base: str, num_paginas: int = 3, delay: int = 3) -> List[Dict]:
        """Scrapea múltiples páginas"""
        print(f"\n🚀 Iniciando scraping de {num_paginas} páginas\n")
        todas_propiedades = []
        
        for pagina in range(1, num_paginas + 1):
            if pagina == 1:
                url = url_base
            else:
                offset = (pagina - 1) * 48 + 1
                url = f"{url_base}_Desde_{offset}"
            
            print(f"📄 Página {pagina}/{num_paginas}")
            propiedades = self.scrape_pagina(url)
            todas_propiedades.extend(propiedades)
            
            if pagina < num_paginas:
                print(f"  ⏳ Esperando {delay} segundos...\n")
                time.sleep(delay)
        
        print(f"\n✅ Total extraído: {len(todas_propiedades)} propiedades\n")
        return todas_propiedades


def main():
    """Función principal"""
    print("="*70)
    print("  🏠 SCRAPER PORTAL INMOBILIARIO - SCRIPT SIMPLE")
    print("="*70)
    
    # Configuración
    URL_BASE = "https://www.portalinmobiliario.com/arriendo/casa/santiago-metropolitana"
    NUM_PAGINAS = 5  # Puedes cambiar esto
    DELAY = 3
    
    print(f"\n📋 CONFIGURACIÓN:")
    print(f"  • URL: {URL_BASE}")
    print(f"  • Páginas: {NUM_PAGINAS}")
    print(f"  • Delay: {DELAY}s entre páginas")
    
    # Crear scraper y ejecutar
    scraper = PortalInmobiliarioScraper()
    propiedades = scraper.scrape_multiples_paginas(URL_BASE, NUM_PAGINAS, DELAY)
    
    if not propiedades:
        print("❌ No se extrajeron propiedades")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(propiedades)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_csv = f'propiedades_{timestamp}.csv'
    
    # Guardar CSV
    df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
    
    print("="*70)
    print("  📊 RESUMEN")
    print("="*70)
    print(f"  ✅ Propiedades extraídas: {len(df)}")
    print(f"  💾 Archivo guardado: {archivo_csv}")
    print(f"  📏 Columnas: {len(df.columns)}")
    print(f"  💰 Rango de precios: ${df['precio'].min():,.0f} - ${df['precio'].max():,.0f}")
    print(f"  📍 Comunas únicas: {df['comuna'].nunique()}")
    print("="*70)
    
    print(f"\n✅ ¡Listo! Usa el archivo '{archivo_csv}' para análisis\n")


if __name__ == "__main__":
    main()
