"""
Generador de visualizaciones interactivas de BERTopic basadas en Plotly.
Incluye manejo de excepciones para corpus pequeños o modelos con pocos tópicos.
"""

from typing import Optional, Dict, Any
from bertopic import BERTopic
import plotly.graph_objects as go


class TopicVisualizer:
    """Generador de gráficos interactivos para DarelyTopic."""

    @staticmethod
    def plot_intertopic_distance(topic_model: BERTopic) -> Optional[go.Figure]:
        """
        Genera el mapa 2D de distancia intertemática (similar a LDAvis).
        Requiere al menos 2 temas (excluyendo el tema -1 de outliers).
        """
        try:
            info = topic_model.get_topic_info()
            valid_topics = info[info["Topic"] != -1]
            if len(valid_topics) < 2:
                return None
            fig = topic_model.visualize_topics()
            fig.update_layout(title="<b>Mapa 2D de Distancia Intertemática</b>", font=dict(family="Arial", size=12))
            return fig
        except Exception:
            return None

    @staticmethod
    def plot_barchart(topic_model: BERTopic, top_n_topics: int = 8, n_words: int = 5) -> Optional[go.Figure]:
        """
        Genera las gráficas de barras con los términos de mayor c-TF-IDF por tema.
        """
        try:
            info = topic_model.get_topic_info()
            valid_topics = info[info["Topic"] != -1]
            if len(valid_topics) < 1:
                return None
            n_to_show = min(top_n_topics, len(valid_topics))
            fig = topic_model.visualize_barchart(top_n_topics=n_to_show, n_words=n_words)
            fig.update_layout(title="<b>Palabras Clave Representativas por Tema (c-TF-IDF)</b>")
            return fig
        except Exception:
            return None

    @staticmethod
    def plot_hierarchy(topic_model: BERTopic) -> Optional[go.Figure]:
        """
        Genera el dendrograma jerárquico que muestra cómo se agrupan los temas afines.
        """
        try:
            info = topic_model.get_topic_info()
            valid_topics = info[info["Topic"] != -1]
            if len(valid_topics) < 3:
                return None
            fig = topic_model.visualize_hierarchy()
            fig.update_layout(title="<b>Dendrograma de Jerarquía y Fusión de Temas</b>")
            return fig
        except Exception:
            return None

    @staticmethod
    def plot_heatmap(topic_model: BERTopic) -> Optional[go.Figure]:
        """
        Genera la matriz de calor (heatmap) de similitud semántica entre temas.
        """
        try:
            info = topic_model.get_topic_info()
            valid_topics = info[info["Topic"] != -1]
            if len(valid_topics) < 2:
                return None
            fig = topic_model.visualize_heatmap()
            fig.update_layout(title="<b>Matriz de Similitud Coseno entre Temas</b>")
            return fig
        except Exception:
            return None
