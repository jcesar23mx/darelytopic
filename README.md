# 📚 DarelyTopic: Hub de Modelado Semántico de Literatura

Plataforma analítica interactiva basada en **BERTopic** y **Streamlit**, diseñada especialmente para investigadores, doctorandos y académicos. Permite subir matrices de revisión sistemática de literatura (Excel o CSV), ejecutar análisis temático no supervisado con modelos de *embeddings* multilingües, explorar visualizaciones interactivas y descargar la clasificación enriquecida.

---

## 🌟 Características Principales

* **Carga Flexible:** Soporta hojas de cálculo Excel (`.xlsx`, `.xls`) y archivos delimitados (`.csv`, `.tsv`) con detección automática de codificación (`utf-8`, `latin1`).
* **Filtros Dinámicos:** Permite filtrar subconjuntos antes del análisis (por ejemplo, analizar solo artículos con `Veredicto_Final == 'Include'` o por rangos temporales).
* **Motor BERTopic Multilingüe:** Utiliza modelos de última generación (`paraphrase-multilingual-MiniLM-L12-v2`) optimizados para inferencia rápida en CPU en español e inglés.
* **Visualizaciones Interactivas (Plotly):**
  * Mapa 2D de distancia intertemática.
  * Barras de términos clave representativos (c-TF-IDF).
  * Dendrograma de jerarquía y fusión temática.
  * Matriz de similitud coseno.
* **Exportador de Resultados:** Descarga de Excel (`.xlsx`) con los artículos etiquetados, su ID de tema, nombre del tema, probabilidad y una hoja resumen con las palabras clave.
* **Listo para Producción:** Empaquetado con Docker para despliegue permanente 24/7 en **Coolify**.

---

## 📁 Estructura del Proyecto

```
darelytopic/
├── core/
│   ├── __init__.py
│   ├── data_loader.py    # Lectura, limpieza y filtrado de datos
│   ├── analyzer.py       # Pipeline de BERTopic y embeddings
│   ├── visualizer.py     # Gráficos interactivos Plotly
│   └── exporter.py       # Generación de Excel enriquecido
├── sample_data/
│   └── revision_articulos.tsv # Archivo de ejemplo para pruebas
├── app.py                # Interfaz de usuario Streamlit
├── requirements.txt      # Dependencias de Python
├── Dockerfile            # Imagen optimizada para CPU
├── docker-compose.yml    # Orquestación para Coolify
├── .gitignore
└── README.md
```

---

## 💻 Ejecución Local (Windows)

### 1. Requisitos Previos
* Tener Python 3.10 o superior instalado.

### 2. Pasos de Instalación
Abre una terminal PowerShell en esta carpeta (`C:\dixsys\darelytopic`):

```powershell
# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar la aplicación
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## 🚀 Despliegue Permanente en Coolify (Hostinger VPS)

Dado que cuentas con Coolify sobre tu servidor Ubuntu 24.04:

### Opción 1: Desde un Repositorio GitHub (Recomendada)
1. Sube esta carpeta `darelytopic` a un repositorio en tu cuenta de GitHub (puede ser privado o público).
2. En tu panel de Coolify:
   * Haz clic en **+ New Resource** > **Public / Private Git Repository**.
   * Conecta tu repositorio.
   * Selecciona tipo de compilación: **Dockerfile** o **Docker Compose**.
   * En configuración de red, Coolify detectará el puerto `8501`.
   * Asigna tu dominio o subdominio (ej. `temas.tudominio.com`). Coolify generará automáticamente el certificado SSL (HTTPS).
3. Haz clic en **Deploy**. ¡Listo! La plataforma quedará accesible 24/7 para todos tus compañeros.

### Opción 2: Despliegue Directo vía Docker Compose en Coolify
1. En Coolify: **+ New Resource** > **Docker Compose**.
2. Pega el contenido de `docker-compose.yml`.
3. Ajusta el dominio deseado y presiona **Deploy**.
