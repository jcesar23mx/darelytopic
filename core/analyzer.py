"""
Motor analítico de modelado de temas basado en BERTopic.
Integra modelos de Sentence Transformers para generación de embeddings,
reducción de dimensión con UMAP, agrupamiento con HDBSCAN y extracción c-TF-IDF.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer


class TopicAnalyzer:
    """Clase controladora del pipeline de BERTopic."""

    MODEL_OPTIONS = {
        "Multilingüe (Español / Inglés / Mixto)": "paraphrase-multilingual-MiniLM-L12-v2",
        "Inglés Rápido (Solo literatura en inglés)": "all-MiniLM-L6-v2"
    }

    # Palabras vacías en español combinadas para revisiones de literatura
    SPANISH_STOPWORDS = [
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para",
        "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este",
        "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta",
        "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni",
        "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
        "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho",
        "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo",
        "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus", "ellas", "nosotras", "vosostros",
        "vosostras", "os", "mío", "mía", "míos", "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo",
        "suya", "suyos", "suyas", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra",
        "vuestros", "vuestras", "esos", "esas", "estoy", "estás", "está", "estamos", "estáis", "están",
        "esté", "estés", "estemos", "estéis", "estén", "esté", "estuviera", "estuviese", "estudiar",
        "analisis", "investigacion", "articulo", "estudio", "resultados", "proceso", "procesos"
    ]

    def __init__(self, model_choice: str = "Multilingüe (Español / Inglés / Mixto)"):
        self.model_name = self.MODEL_OPTIONS.get(model_choice, "paraphrase-multilingual-MiniLM-L12-v2")
        self.embedding_model = None
        self.topic_model: Optional[BERTopic] = None

    def _load_embedding_model(self):
        """Carga el modelo de embeddings en memoria."""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(self.model_name)
        return self.embedding_model

    def fit_model(
        self,
        docs: List[str],
        min_topic_size: int = 5,
        nr_topics: Optional[int] = None,
        language_stop_words: str = "Ambos (Español + Inglés)"
    ) -> Tuple[BERTopic, List[int], np.ndarray, pd.DataFrame]:
        """
        Ajusta y entrena el modelo BERTopic sobre la lista de documentos.
        Retorna la tupla: (modelo, lista_temas, probabilidades, topic_info_df).
        """
        if len(docs) < 10:
            raise ValueError(
                f"El corpus contiene únicamente {len(docs)} documentos válidos. "
                "BERTopic requiere al menos 10-15 textos para generar clusters estadísticamente significativos."
            )

        embed_model = self._load_embedding_model()

        # Construir lista de palabras vacías
        if language_stop_words == "Español":
            stop_words_list = self.SPANISH_STOPWORDS
        elif language_stop_words == "Inglés":
            stop_words_list = "english"
        else:
            # Combinación de ambos
            from sklearn.feature_extraction import text
            stop_words_list = list(text.ENGLISH_STOP_WORDS.union(set(self.SPANISH_STOPWORDS)))

        vectorizer_model = CountVectorizer(
            stop_words=stop_words_list,
            min_df=2 if len(docs) >= 30 else 1,
            ngram_range=(1, 2)
        )

        topic_model_params = {
            "embedding_model": embed_model,
            "vectorizer_model": vectorizer_model,
            "min_topic_size": int(min_topic_size),
            "calculate_probabilities": True,
            "verbose": False
        }

        if nr_topics and nr_topics > 0:
            topic_model_params["nr_topics"] = int(nr_topics)

        self.topic_model = BERTopic(**topic_model_params)
        topics, probs = self.topic_model.fit_transform(docs)

        topic_info = self.topic_model.get_topic_info()
        return self.topic_model, topics, probs, topic_info

    @staticmethod
    def extract_top_probability(probs: np.ndarray) -> np.ndarray:
        """
        Extrae la probabilidad más alta de pertenencia a un tema para cada documento.
        """
        if isinstance(probs, np.ndarray):
            if len(probs.shape) > 1 and probs.shape[1] > 0:
                return np.max(probs, axis=1)
            return probs
        return np.array([1.0] * len(probs))
