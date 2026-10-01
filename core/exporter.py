"""
Generador de archivos Excel enriquecidos para exportación de resultados.
Crea hojas de cálculo limpias con pestañas para artículos y resumen temático.
"""

import io
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


class TopicExporter:
    """Exportador de resultados de BERTopic a Excel (.xlsx)."""

    @staticmethod
    def create_excel_buffer(
        original_df: pd.DataFrame,
        topics: List[int],
        probs: np.ndarray,
        topic_info: pd.DataFrame
    ) -> io.BytesIO:
        """
        Genera un buffer binario en memoria con el archivo Excel final (.xlsx).
        """
        enriched_df = original_df.copy()

        # Asignar tema numérico
        enriched_df["Tema_ID"] = topics

        # Mapear nombres de temas
        topic_name_map = dict(zip(topic_info["Topic"], topic_info["Name"]))
        enriched_df["Tema_Nombre"] = [
            topic_name_map.get(t, f"Tema_{t}") if t != -1 else "No clasificado (Outlier)"
            for t in topics
        ]

        # Extraer probabilidad
        if isinstance(probs, np.ndarray):
            if len(probs.shape) > 1 and probs.shape[1] > 0:
                top_prob = np.max(probs, axis=1)
            else:
                top_prob = probs
            enriched_df["Probabilidad"] = np.round(top_prob, 4)
        else:
            enriched_df["Probabilidad"] = 1.0

        # Formatear la tabla de resumen
        summary_df = topic_info.copy()
        if "Representation" in summary_df.columns:
            summary_df["Palabras_Clave"] = summary_df["Representation"].apply(
                lambda words: ", ".join(words) if isinstance(words, (list, tuple)) else str(words)
            )

        # Escribir en memoria usando openpyxl
        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            enriched_df.to_excel(writer, sheet_name="Articulos_Con_Temas", index=False)
            summary_df.to_excel(writer, sheet_name="Resumen_Temas", index=False)

        output_buffer.seek(0)
        return output_buffer
