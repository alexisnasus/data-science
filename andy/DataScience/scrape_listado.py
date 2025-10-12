# scrape_listado.py
import pandas as pd
from bs4 import BeautifulSoup
from throttle_utils import build_session, Throttler, fetch

def scrape_portal_inmobiliario():
    base_url = "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/metropolitana/_Desde_{}_NoIndex_True"
    all_properties = []

    # Session + Throttler configurados para bajar el ritmo
    session = build_session(total_retries=4, backoff_factor=1.0)
    throttler = Throttler(
        min_delay=4.0,
        max_delay=10.0,
        long_pause_every=30,
        long_pause_min=90.0,
        long_pause_max=180.0
    )

    for page_num in range(1, 43):
        item_offset = (page_num - 1) * 48 + 1

        if page_num == 1:
            url = "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/metropolitana/_NoIndex_True"
        else:
            url = base_url.format(item_offset)

        print(f"Scraping página {page_num}: {url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            response = fetch(url, session=session, throttler=throttler, headers=headers, timeout=25)
            response.raise_for_status()

            # Usa lxml si está disponible (más sólido)
            soup = BeautifulSoup(response.content, 'lxml')

            listings = soup.select('li.ui-search-layout__item')
            if not listings:
                print(f"No se encontraron propiedades en la página {page_num}. Puede que la paginación haya terminado.")
                break

            for item in listings:
                property_data = {'link': None, 'titulo': None, 'precio': None, 'moneda': None}

                title_tag = item.select_one('.poly-component__title')
                if not title_tag:
                    continue

                property_data['titulo'] = title_tag.get_text(strip=True)

                link_tag = title_tag.find_parent('a')
                if link_tag and link_tag.has_attr('href'):
                    property_data['link'] = link_tag['href']
                else:
                    fallback_link_tag = item.select_one('a[href]')
                    if fallback_link_tag:
                        property_data['link'] = fallback_link_tag['href']

                price_container = item.select_one('.poly-price__current')
                if price_container:
                    price_tag = price_container.select_one('.andes-money-amount__fraction')
                    currency_tag = price_container.select_one('.andes-money-amount__currency-symbol')
                    if price_tag:
                        property_data['precio'] = price_tag.get_text(strip=True).replace('.', '')
                    if currency_tag:
                        property_data['moneda'] = currency_tag.get_text(strip=True)

                if property_data['link']:
                    all_properties.append(property_data)

        except Exception as e:
            print(f"Error en página {page_num}: {e}")
            continue

    if all_properties:
        df = pd.DataFrame(all_properties)
        df.to_csv('propiedades_portal_inmobiliario.csv', index=False, encoding='utf-8-sig')
        print(f"\n¡Scraping completado! Se encontraron {len(all_properties)} propiedades.")
        print("Datos guardados en 'propiedades_portal_inmobiliario.csv'")
    else:
        print("\nNo se pudo extraer ninguna propiedad.")

if __name__ == '__main__':
    scrape_portal_inmobiliario()
