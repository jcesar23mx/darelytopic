"""
Módulo para carga, validación y filtrado de datos de revisión de literatura.
Soporta archivos Excel (.xlsx, .xls) y CSV con detección automática de codificación.
"""

import io
from typing import List, Tuple, Any, Optional
import pandas as pd


class DataLoader:
    """Gestor de carga y preparación de datos para DarelyTopic."""

    SUPPORTED_EXTENSIONS = [".xlsx", ".xls", ".csv", ".tsv", ".txt"]

    @classmethod
    def load_file(cls, file_source: Any, filename: Optional[str] = None) -> pd.DataFrame:
        """
        Carga un archivo desde una ruta de archivo o un objeto en memoria (Streamlit UploadedFile).
        Aplica múltiples intentos de decodificación para máxima compatibilidad.
        """
        name = filename or getattr(file_source, "name", "")
        name_lower = name.lower()

        if name_lower.endswith((".xlsx", ".xls")):
            return pd.read_excel(file_source, engine="openpyxl" if name_lower.endswith(".xlsx") else None)

        # Para archivos de texto delimitado (CSV/TSV)
        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
        
        # Si es un buffer en memoria, leemos los bytes para poder reintentar
        if hasattr(file_source, "getvalue"):
            raw_bytes = file_source.getvalue()
            for enc in encodings:
                try:
                    return pd.read_csv(
                        io.BytesIO(raw_bytes),
                        sep=None,
                        engine="python",
                        encoding=enc
                    )
                except Exception:
                    continue
            # Fallback final ignorando caracteres problemáticos
            return pd.read_csv(
                io.BytesIO(raw_bytes),
                sep=None,
                engine="python",
                encoding="utf-8",
                errors="replace"
            )
        else:
            # Es una ruta en disco
            for enc in encodings:
                try:
                    return pd.read_csv(
                        file_source,
                        sep=None,
                        engine="python",
                        encoding=enc
                    )
                except Exception:
                    continue
            return pd.read_csv(
                file_source,
                sep=None,
                engine="python",
                encoding="utf-8",
                errors="replace"
            )

    @staticmethod
    def get_text_columns(df: pd.DataFrame) -> List[str]:
        """
        Identifica columnas con contenido textual y prioriza las más relevantes
        (Abstract, Titulo, Resumen, Razon, etc.).
        """
        text_cols = [c for c in df.columns if df[c].dtype == "object" or str(df[c].dtype) == "string"]
        if not text_cols:
            text_cols = list(df.columns)

        # Priorizar palabras clave habituales en revisiones sistemáticas
        priority_keywords = ["abstract", "resumen", "titulo", "title", "razon", "evaluacion", "conclusion", "texto"]
        
        def priority_score(col_name: str) -> int:
            col_lower = str(col_name).lower()
            for idx, kw in enumerate(priority_keywords):
                if kw in col_lower:
                    return idx
            return len(priority_keywords)

        return sorted(text_cols, key=priority_score)

    @staticmethod
    def get_filter_columns(df: pd.DataFrame, max_unique: int = 50) -> List[str]:
        """
        Identifica columnas idóneas para aplicar filtros categóricos
        (ej. Veredicto_Final, Año, Fuente, Tipo, etc.).
        """
        candidate_cols = []
        for c in df.columns:
            n_unique = df[c].nunique(dropna=True)
            if 1 < n_unique <= max_unique:
                candidate_cols.append(c)
        return candidate_cols

    @staticmethod
    def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
        """Retorna los valores únicos ordenados de una columna."""
        if column not in df.columns:
            return []
        vals = df[column].dropna().unique().tolist()
        return sorted([str(v) for v in vals])

    @staticmethod
    def apply_filter(df: pd.DataFrame, column: Optional[str], value: Optional[str]) -> pd.DataFrame:
        """Filtra el DataFrame por un valor específico si aplica."""
        if not column or not value or value == "(Todos)" or column not in df.columns:
            return df
        return df[df[column].astype(str) == str(value)].copy()

    @staticmethod
    def prepare_corpus(df: pd.DataFrame, text_column: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Limpia y extrae la lista de documentos para el análisis.
        Elimina valores nulos o cadenas vacías. Retorna el DataFrame alineado y los textos.
        """
        if text_column not in df.columns:
            raise ValueError(f"La columna '{text_column}' no existe en el archivo.")

        # Filtrar valores no nulos y convertir a string
        clean_df = df.dropna(subset=[text_column]).copy()
        clean_df[text_column] = clean_df[text_column].astype(str).str.strip()
        clean_df = clean_df[clean_df[text_column] != ""].copy()

        docs = clean_df[text_column].tolist()
        return clean_df, docs
