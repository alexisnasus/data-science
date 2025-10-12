# scrape_detalle.py
import os
import pandas as pd
from bs4 import BeautifulSoup
from throttle_utils import build_session, Throttler, fetch

def scrape_property_characteristics(input_csv, output_csv, resume=True, checkpoint_every=100):
    # Cargar los enlaces base
    df = pd.read_csv(input_csv, encoding='utf-8-sig')

    session = build_session(total_retries=4, backoff_factor=1.0)
    throttler = Throttler(
        min_delay=4.0,
        max_delay=10.0,
        long_pause_every=30,
        long_pause_min=90.0,
        long_pause_max=180.0
    )

    # Reanudar si ya existe output previo
    done_links = set()
    all_details = []
    if resume and os.path.exists(output_csv):
        prev = pd.read_csv(output_csv, encoding='utf-8-sig')
        if "link" in prev.columns:
            done_links = set(prev["link"].dropna().astype(str))
        all_details = prev.to_dict("records")
        print(f"[Resume] Cargando {len(done_links)} links ya procesados desde '{output_csv}'")

    processed_since_checkpoint = 0

    for index, row in df.iterrows():
        property_url = str(row.get('link', '')).strip()
        if not property_url:
            continue
        if resume and property_url in done_links:
            continue

        print(f"Procesando {index+1}/{len(df)}: {property_url}")

        record = {
            'link': property_url,
            'superficie_util': None,
            'superficie_total': None,
            'dormitorios': None,
            'banos': None
        }

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            }
            response = fetch(property_url, session=session, throttler=throttler, headers=headers, timeout=25)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Recorremos filas: <tr> con <th> y <td>
            for tr in soup.select('tr.andes-table__row'):
                th = tr.find('th')
                td = tr.find('td')
                if not th or not td:
                    continue

                key = th.get_text(strip=True).lower()
                val_tag = td.select_one('.andes-table__column--value') or td
                val = val_tag.get_text(strip=True) if val_tag else None
                if not val:
                    continue

                if 'superficie útil' in key:
                    record['superficie_util'] = val
                elif 'superficie total' in key:
                    record['superficie_total'] = val
                elif 'dormitorios' in key:
                    record['dormitorios'] = val
                elif 'baños' in key:
                    record['banos'] = val

        except Exception as e:
            print(f"Error al acceder a {property_url}: {e}")

        all_details.append(record)
        processed_since_checkpoint += 1

        if checkpoint_every and processed_since_checkpoint >= checkpoint_every:
            pd.DataFrame(all_details).to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"[Checkpoint] Guardadas {len(all_details)} filas en '{output_csv}'")
            processed_since_checkpoint = 0

    # Guardado final
    pd.DataFrame(all_details).to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n¡Listo! Guardadas {len(all_details)} filas en '{output_csv}'")

if __name__ == '__main__':
    # Cambia rutas si usas otro nombre de CSV
    input_csv = 'propiedades_portal_inmobiliario.csv'
    output_csv = 'propiedades_detalle_caracteristicas.csv'
    scrape_property_characteristics(input_csv, output_csv, resume=True, checkpoint_every=100)
