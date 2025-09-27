import re
import pandas as pd
import io
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

class CVPreparer:
    """
    Toma el contenido de texto de una Hoja de Vida (.md) y lo transforma
    en un objeto estructurado y consultable.
    """
    def __init__(self, cv_content: str):
        self.cv_content = cv_content
        self.metadata = {}
        self.file_stats_by_day = pd.DataFrame()
        self.upload_schedule_by_day = pd.DataFrame()
        self.day_of_week_summary = pd.DataFrame() # NUEVO: Para la nueva tabla
        self.parse()

    def _parse_table_after_text(self, landmark_text: str) -> pd.DataFrame:
        try:
            landmark_pos = self.cv_content.find(landmark_text)
            if landmark_pos == -1: return pd.DataFrame()
            search_area = self.cv_content[landmark_pos:]
            table_match = re.search(r"(\|.*?\n)+", search_area)
            if not table_match: return pd.DataFrame()
            table_str = table_match.group(0)
            lines = [line.strip() for line in table_str.strip().split('\n') if '|' in line]
            lines = [line for line in lines if not all(c in '-| ' for c in line)]
            table_io = io.StringIO('\n'.join(lines))
            df = pd.read_csv(table_io, sep='|', skipinitialspace=True)
            df = df.dropna(axis=1, how='all').iloc[1:]
            df.columns = [col.strip() for col in df.columns]
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            df = df.rename(columns=lambda x: x.strip())
            if 'Day' in df.columns: df = df.set_index('Day')
            return df
        except Exception: return pd.DataFrame()

    def parse(self):
        """Orquesta el proceso de parseo."""
        resource_id_match = re.search(r"- \*\*Resource ID\*\*: (\d+)", self.cv_content)
        if resource_id_match: self.metadata['resource_id'] = resource_id_match.group(1)

        self.file_stats_by_day = self._parse_table_after_text("- **File Processing Statistics by Day**:")
        self.upload_schedule_by_day = self._parse_table_after_text("- **Upload Schedule Patterns by Day**:")
        # NUEVO: Leemos la tabla de resumen semanal
        self.day_of_week_summary = self._parse_table_after_text("## **3. Day-of-Week Summary**")
        # Si falla, probamos con otro posible título
        if self.day_of_week_summary.empty:
            self.day_of_week_summary = self._parse_table_after_text("## **4. Day-of-Week Summary (Core Reference)**")

    def get_metadata(self) -> dict:
        return self.metadata

    def get_mean_files(self, day_of_week: str) -> float:
        try:
            return float(self.file_stats_by_day.loc[day_of_week, 'Mean Files'])
        except (KeyError, ValueError): return 0.0

    def get_expected_time_window(self, day_of_week: str) -> str:
        try:
            return self.upload_schedule_by_day.loc[day_of_week, 'Upload Time Window Expected']
        except KeyError: return None

    def get_mean_empty_files(self, day_of_week: str) -> float:
        """
        NUEVO: Extrae la media de archivos vacíos esperados de la celda de texto.
        """
        try:
            # La celda puede contener varias líneas de texto. ej: "• Min: 0<br>• Max: 0<br>• Mean: 0.00"
            cell_text = self.day_of_week_summary.loc[day_of_week, 'Empty Files']
            # Usamos regex para encontrar el número después de "Mean:"
            match = re.search(r"Mean:\s*([\d\.]+)", cell_text, re.IGNORECASE)
            if match:
                return float(match.group(1))
            return 0.0 # Si no encuentra la palabra "Mean", asumimos 0
        except (KeyError, ValueError):
            return 0.0