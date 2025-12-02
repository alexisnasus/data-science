# 🏠 Predicción de Precios de Arriendo - Santiago

Modelo de Machine Learning para predecir precios de arriendo en Santiago usando datos de Portal Inmobiliario + variables geográficas y socioeconómicas.

---

## ⚡ Inicio Rápido

### Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv env

# Activar
.\env\Scripts\Activate.ps1      # Windows PowerShell
.\env\Scripts\activate.bat      # Windows CMD
source env/bin/activate         # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar Notebook

```bash
# Abrir VS Code con Jupyter
code Proyecto_Data_Science.ipynb
```

**O usar en Google Colab:**
1. Subir CSVs a Colab
2. Ejecutar celdas secuencialmente

---

### Ejecutar Scraping (Opcional)

```bash
# Scraping básico de Portal Inmobiliario
python scrape_listado.py

# Scraping detallado (características adicionales)
python scrape_detalle.py
```

**Archivos generados:**
- `propiedades_portal_inmobiliario.csv` - Datos básicos
- `propiedades_detalle_caracteristicas.csv` - Características detalladas