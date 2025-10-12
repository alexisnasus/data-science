# ml_search_listado.py
import time
import random
import requests
import pandas as pd

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
SEARCH_URL = "https://api.mercadolibre.com/sites/MLC/search"

# Palabras clave para cubrir RM (agrega/remueve a gusto)
QUERIES = [
    "departamento santiago", "departamento providencia", "departamento ñuñoa",
    "departamento las condes", "departamento vitacura", "departamento la reina",
    "departamento macul", "departamento independencia", "departamento recoleta",
    "departamento maipú", "departamento peñalolén", "departamento la florida",
    "departamento san miguel", "departamento san joaquín", "departamento quinta normal",
    "departamento estación central", "departamento la cisterna", "departamento huechuraba",
    "departamento cerrillos", "departamento conchalí", "departamento lo prado",
    "departamento lo barnechea", "departamento puente alto"
]

def buscar_items_por_query(query: str, max_items:int=1000, page_size:int=50):
    """
    Usa la API de búsqueda de ML (MLC) para traer resultados por 'q'.
    Pagina con offset de 'page_size' hasta 'max_items' o hasta que no haya más.
    Devuelve lista de dicts con link/titulo/precio/moneda.
    """
    out = []
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json"})

    offset = 0
    while offset < max_items:
        params = {
            "q": query,
            "offset": offset,
            "limit": page_size
        }
        r = session.get(SEARCH_URL, params=params, timeout=20)
        if r.status_code != 200:
            print(f"[{query}] API {r.status_code} en offset {offset}")
            break

        data = r.json()
        results = data.get("results", [])
        if not results:
            break

        for it in results:
            # Campos típicos disponibles en search:
            permalink = it.get("permalink")
            title = it.get("title")
            price = it.get("price")
            currency = it.get("currency_id")
            if permalink:
                out.append({
                    "link": permalink,
                    "titulo": title,
                    "precio": price,
                    "moneda": currency
                })

        offset += page_size
        # pequeño respiro para la API
        time.sleep(random.uniform(0.25, 0.6))

    return out

def main(output_csv="propiedades_portal_inmobiliario.csv"):
    all_rows = []
    for q in QUERIES:
        print(f"Buscando: {q}")
        rows = buscar_items_por_query(q, max_items=1000, page_size=50)
        print(f"  {len(rows)} items")
        all_rows.extend(rows)

    # De-duplicar por link (a veces el mismo item aparece con distintas queries)
    if all_rows:
        df = pd.DataFrame(all_rows)
        df = df.drop_duplicates(subset=["link"]).reset_index(drop=True)
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"\nCSV generado: {output_csv}  ({len(df)} enlaces únicos)")
    else:
        print("No se obtuvieron items. Ajusta las QUERIES o vuelve a intentar.")

if __name__ == "__main__":
    main()
