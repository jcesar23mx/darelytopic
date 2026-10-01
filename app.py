"""
DarelyTopic - Plataforma Web de Modelado de Temas con BERTopic
Desarrollada para Revisiones Sistemáticas de Literatura, Investigación Doctoral y Posgrado.
"""

import streamlit as st
import pandas as pd
import numpy as np

from core.data_loader import DataLoader
from core.analyzer import TopicAnalyzer
from core.visualizer import TopicVisualizer
from core.exporter import TopicExporter

# Configuración de página en modo panorámico
st.set_page_config(
    page_title="DarelyTopic | Modelado de Temas",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados sutiles
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# Título y encabezado
st.markdown('<div class="main-title">📚 DarelyTopic</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Hub de Modelado Semántico de Literatura con <b>BERTopic</b> '
    'para Revisiones Sistemáticas de Literatura (RSL) y Tesis Doctorales.</div>',
    unsafe_allow_html=True
)

# Inicializar sesión
if "results" not in st.session_state:
    st.session_state.results = None

# ==========================================
# BARRA LATERAL (CONTROLES Y CONFIGURACIÓN)
# ==========================================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # 1. Carga de archivo
    uploaded_file = st.file_uploader(
        "1. Sube tu archivo (Excel o CSV)",
        type=["xlsx", "xls", "csv", "tsv"],
        help="Sube una matriz de cribado de artículos, resultados de Scopus/WoS o encuestas."
    )

    if uploaded_file is not None:
        try:
            df = DataLoader.load_file(uploaded_file)
            st.success(f"Archivo cargado: **{len(df)}** filas detectadas.")
        except Exception as e:
            st.error(f"Error al leer archivo: {e}")
            df = None
    else:
        df = None

    if df is not None:
        st.divider()
        # 2. Selección de columna de texto
        text_cols = DataLoader.get_text_columns(df)
        selected_text_col = st.selectbox(
            "2. Columna de texto a analizar",
            options=text_cols,
            help="Selecciona la columna con los Abstracts, Títulos o Razones de evaluación."
        )

        # 3. Filtro opcional
        with st.expander("🔍 Filtro opcional por columna", expanded=False):
            filter_cols = DataLoader.get_filter_columns(df)
            selected_filter_col = st.selectbox(
                "Filtrar por columna (ej. Veredicto)",
                options=["(Ninguno)"] + filter_cols
            )

            if selected_filter_col != "(Ninguno)":
                unique_values = DataLoader.get_unique_values(df, selected_filter_col)
                selected_filter_val = st.selectbox(
                    "Valor a analizar (ej. Include)",
                    options=["(Todos)"] + unique_values
                )
            else:
                selected_filter_val = "(Todos)"

        st.divider()
        # 4. Hiperparámetros de BERTopic
        with st.expander("🧠 Parámetros de BERTopic", expanded=True):
            model_lang = st.selectbox(
                "Modelo de Lenguaje (Embeddings)",
                options=list(TopicAnalyzer.MODEL_OPTIONS.keys()),
                help="El modelo Multilingüe funciona excelente tanto en español como en inglés o mixto."
            )
            
            min_topic_size = st.slider(
                "Tamaño mínimo de tema (documentos por grupo)",
                min_value=3,
                max_value=30,
                value=5,
                step=1,
                help="Un valor bajo (3-5) genera temas muy específicos. Un valor mayor (8-15) crea temas más amplios."
            )

            stopwords_lang = st.selectbox(
                "Filtro de Palabras Vacías (Stopwords)",
                options=["Ambos (Español + Inglés)", "Español", "Inglés"]
            )

            reduce_topics = st.checkbox("Reducir a un número fijo de temas", value=False)
            target_topics = None
            if reduce_topics:
                target_topics = st.number_input("Número de temas deseado", min_value=2, max_value=50, value=10)

        # Botón de ejecución
        st.divider()
        execute_btn = st.button("🚀 Ejecutar Análisis", type="primary", use_container_width=True)
    else:
        execute_btn = False

# ==========================================
# CUERPO PRINCIPAL
# ==========================================
if df is None:
    st.info("👋 **¡Bienvenido a DarelyTopic!** Para comenzar, sube una hoja de cálculo (Excel o CSV) desde la barra lateral izquierda.")
    
    st.markdown("""
    ### 📌 ¿Cómo funciona?
    1. **Sube tu archivo:** Puede ser tu matriz de tamizaje PRISMA, exportaciones de Scopus, Web of Science, PubMed o SciELO.
    2. **Elige la columna de texto:** Puedes modelar los **Abstracts**, los **Títulos** o las **Razones de Inclusión/Exclusión**.
    3. **Aplica filtros si lo requieres:** Por ejemplo, analiza únicamente los artículos con `Veredicto_Final == 'Include'` para descubrir las líneas temáticas clave de tu revisión.
    4. **Explora y descarga:** Revisa los mapas interactivos en 2D, las palabras clave por tema y descarga un archivo Excel enriquecido con el tema asignado a cada artículo.
    """)

else:
    # Vista previa de datos cargados
    with st.expander("👀 Vista previa del archivo cargado", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

    # Ejecución del análisis
    if execute_btn:
        # Aplicar filtro si existe
        filtered_df = DataLoader.apply_filter(df, selected_filter_col, selected_filter_val)
        
        try:
            clean_df, docs = DataLoader.prepare_corpus(filtered_df, selected_text_col)
            
            with st.spinner(f"Entrenando BERTopic sobre {len(docs)} documentos... Esto toma unos segundos."):
                analyzer = TopicAnalyzer(model_choice=model_lang)
                topic_model, topics, probs, topic_info = analyzer.fit_model(
                    docs=docs,
                    min_topic_size=min_topic_size,
                    nr_topics=target_topics,
                    language_stop_words=stopwords_lang
                )
                
                # Guardar resultados en session_state
                st.session_state.results = {
                    "clean_df": clean_df,
                    "docs": docs,
                    "topic_model": topic_model,
                    "topics": topics,
                    "probs": probs,
                    "topic_info": topic_info,
                    "text_col": selected_text_col
                }
                st.success("✅ ¡Análisis completado exitosamente!")
        except Exception as e:
            st.error(f"❌ Error durante el procesamiento: {str(e)}")

    # Mostrar resultados si están en sesión
    if st.session_state.results is not None:
        res = st.session_state.results
        clean_df = res["clean_df"]
        topic_model = res["topic_model"]
        topics = res["topics"]
        probs = res["probs"]
        topic_info = res["topic_info"]
        text_col = res["text_col"]

        # Métricas destacadas
        valid_topics = topic_info[topic_info["Topic"] != -1]
        n_topics = len(valid_topics)
        total_docs = len(clean_df)
        outlier_count = int(topic_info[topic_info["Topic"] == -1]["Count"].iloc[0]) if -1 in topic_info["Topic"].values else 0
        outlier_pct = round((outlier_count / total_docs) * 100, 1) if total_docs > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Documentos Analizados", f"{total_docs}")
        with col2:
            st.metric("Temas Identificados", f"{n_topics}")
        with col3:
            st.metric("Documentos Agrupados", f"{total_docs - outlier_count}")
        with col4:
            st.metric("Sin clasificar (Outliers)", f"{outlier_count} ({outlier_pct}%)")

        st.divider()

        # Botón de descarga destacado
        excel_buffer = TopicExporter.create_excel_buffer(
            original_df=clean_df,
            topics=topics,
            probs=probs,
            topic_info=topic_info
        )
        
        st.download_button(
            label="📥 Descargar Excel con Temas Asignados (.xlsx)",
            data=excel_buffer,
            file_name="resultados_bertopic_darelytopic.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

        st.write("")

        # Pestañas de resultados
        tab_summary, tab_explore, tab_intertopic, tab_bars, tab_hierarchy, tab_heatmap = st.tabs([
            "📋 Resumen de Temas",
            "🔍 Explorador de Artículos",
            "🗺️ Mapa 2D Intertemático",
            "📊 Palabras Clave",
            "🌳 Jerarquía (Dendrograma)",
            "🔥 Matriz de Similitud"
        ])

        with tab_summary:
            st.subheader("Estructura Temática Descubierta")
            formatted_info = topic_info.copy()
            if "Representation" in formatted_info.columns:
                formatted_info["Términos_Principales"] = formatted_info["Representation"].apply(
                    lambda words: ", ".join(words[:6]) if isinstance(words, (list, tuple)) else str(words)
                )
                formatted_info = formatted_info.drop(columns=["Representation"])
            st.dataframe(formatted_info, use_container_width=True, hide_index=True)

        with tab_explore:
            st.subheader("Explorador de Artículos por Tema")
            
            # Selector de tema
            topic_options = {
                row["Topic"]: f"Tema {row['Topic']}: {row['Name']} ({row['Count']} docs)"
                for _, row in topic_info.iterrows()
            }
            selected_topic_id = st.selectbox(
                "Selecciona un tema para inspeccionar sus artículos:",
                options=list(topic_options.keys()),
                format_func=lambda tid: topic_options.get(tid, f"Tema {tid}")
            )

            # Filtrar documentos de ese tema
            topic_indices = [i for i, t in enumerate(topics) if t == selected_topic_id]
            topic_docs_df = clean_df.iloc[topic_indices].copy()
            
            # Asignar probabilidad si está disponible
            top_probs = TopicAnalyzer.extract_top_probability(probs)
            topic_docs_df["Probabilidad"] = np.round(top_probs[topic_indices], 4)

            st.write(f"Mostrando **{len(topic_docs_df)}** artículos asignados a este tema:")
            st.dataframe(topic_docs_df, use_container_width=True)

        with tab_intertopic:
            st.subheader("Distancia Semántica entre Temas")
            st.write("Visualiza la cercanía o lejanía conceptual de los temas en un espacio bidimensional.")
            fig_inter = TopicVisualizer.plot_intertopic_distance(topic_model)
            if fig_inter:
                st.plotly_chart(fig_inter, use_container_width=True)
            else:
                st.info("Se requieren al menos 2 temas clasificados para generar el mapa de distancias.")

        with tab_bars:
            st.subheader("Términos más Relevantes por Tema (c-TF-IDF)")
            fig_bars = TopicVisualizer.plot_barchart(topic_model, top_n_topics=8)
            if fig_bars:
                st.plotly_chart(fig_bars, use_container_width=True)
            else:
                st.info("No hay suficientes temas para generar el gráfico de barras.")

        with tab_hierarchy:
            st.subheader("Dendrograma de Jerarquía y Fusión")
            st.write("Muestra cómo se relacionan y subordinan los temas entre sí según su similitud jerárquica.")
            fig_hier = TopicVisualizer.plot_hierarchy(topic_model)
            if fig_hier:
                st.plotly_chart(fig_hier, use_container_width=True)
            else:
                st.info("Se requieren al menos 3 temas para calcular la jerarquía de fusión.")

        with tab_heatmap:
            st.subheader("Matriz de Similitud Coseno")
            fig_heat = TopicVisualizer.plot_heatmap(topic_model)
            if fig_heat:
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("No hay suficientes temas para calcular la matriz de similitud.")
