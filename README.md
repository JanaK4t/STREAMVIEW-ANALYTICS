# STREAMVIEW-ANALYTICS
Este repositorio contiene el código fuente y la documentación del proyecto de visualización de datos para **Streamviews**. La solución implementa un ecosistema analítico híbrido diseñado para apoyar la toma de decisiones de inversión, crecimiento y adquisición de licencias en la plataforma.

## Objetivo del Proyecto

Desarrollar herramientas de inteligencia de negocios adaptadas a diferentes audiencias dentro de la compañía:
1. **Dashboard Ejecutivo (Power BI):** Orientado al Directorio y Gerencia General. Permite comprender rápidamente el estado global del catálogo, su evolución histórica y la huella geográfica de las producciones.
2. **Dashboard Analítico (Streamlit):** Orientado a la Gerencia de Contenidos y Adquisición. Proporciona una exploración profunda mediante el cruce de variables de popularidad y calificación.
3. **Módulo Financiero a Medida (D3.js):** Renderizado directamente en el navegador, aísla interactivamente los éxitos de taquilla con presupuestos reducidos y calcula métricas de ROI.

## Tecnologías y Arquitectura

* **Procesamiento de Datos:** Python (Pandas)
* **Frontend Analítico:** Streamlit
* **Frontend Financiero:** D3.js, Vanilla JavaScript, HTML5, CSS3
* **Visualización Ejecutiva:** Microsoft Power BI
* **Control de Versiones:** Git, implementando metodologías **Gitflow / GitHub Flow**.

## Instalación y Ejecución Local

Para visualizar los módulos desarrollados en código (Streamlit y D3.js), sigue estas instrucciones:

### 1. Clonar el repositorio

```bash
git clone https://github.com/JanaK4t/STREAMVIEW-ANALYTICS.git
cd STREAMVIEW-ANALYTICS
```
### 2. Ejecutar el Módulo Analítico (Streamlit)
Asegúrate de tener Python instalado y ejecuta:
```bash
# Instalar dependencias
pip install -r requirements.txt

# Levantar el servidor de Streamlit
streamlit run app.py
```

# Levantar servidor HTTP con Python
python -m http.server 8000
