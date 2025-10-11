# 🏠 Scraping Portal Inmobiliario

Extrae datos de propiedades en arriendo de Portal Inmobiliario.

---

## ⚡ Inicio Rápido

```bash

#Entorno virtual
python -m venv env
.\env\Scripts\Activate.ps1 #source env/bin/activate (mac/linux)

# 1. instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar scraper
python 01_scraper_simple.py

# 3. Validar datos
python 05_validar_datos.py propiedades_*.csv

# 4. Usar CSV limpio para análisis
```

---

## 📜 Scripts Disponibles

| Script | Uso | Output |
|--------|-----|--------|
| `01_scraper_simple.py` | Scraping básico (5 páginas) | `propiedades_YYYYMMDD.csv` |
| `02_scraper_configurable.py` | Personalizable por región/tipo | `propiedades_[tipo]_[region].csv` |
| `03_scraper_incremental.py` | Actualización histórica | `propiedades_historico.csv` |
| `04_scraper_multiples_regiones.py` | Scraping nacional | `propiedades_nacional.csv` |
| `05_validar_datos.py` | Limpieza y validación | `archivo_limpio.csv` |

---

## � Ejemplos de Uso

### Scraping simple
```bash
python 01_scraper_simple.py
```

### Scraping personalizado
```bash
python 02_scraper_configurable.py --tipo departamento --region valparaiso --paginas 10
```

### Validar datos
```bash
python 05_validar_datos.py propiedades_20251010.csv
```

---

## 📊 Flujo de Trabajo

```
1. Scrapear localmente (PC)
   python 01_scraper_simple.py

2. Validar datos
   python 05_validar_datos.py archivo.csv

3. Subir CSV limpio a Google Colab

4. Analizar con Portal_Inmobiliario_Colab.ipynb
```

---

## ⚙️ Opciones de `02_scraper_configurable.py`

```bash
--tipo       casa | departamento | oficina | local
--region     metropolitana | valparaiso | biobio | maule
--paginas    Número de páginas (default: 5)
--delay      Segundos entre páginas (default: 3)
--output     Nombre del archivo CSV
```

---

## ✅ Tips

- ⏱️ Mantén delay ≥ 3 segundos para evitar bloqueos
- 🔄 Usa `03_scraper_incremental.py` para ejecución periódica
- ✓ Valida siempre con `05_validar_datos.py` antes de analizar
- ❌ NO ejecutes scraping en Google Colab (usa localmente)

---

## 📁 Archivos Generados

```
propiedades_*.csv              → Datos crudos
propiedades_*_limpio.csv       → Datos validados
propiedades_historico.csv      → Histórico acumulado
backup_propiedades_*.csv       → Backups automáticos
```

---

**✅ Ejecuta `python 01_scraper_simple.py` para empezar**
