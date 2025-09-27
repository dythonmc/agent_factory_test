import re
import pandas as pd
import io
import sys
import os

# Añadimos la ruta raíz del proyecto para que podamos importar nuestro 'loader'
# Esto es un truco para que Python encuentre nuestros otros archivos
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from loader import load_all_cvs

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
        
        # Al crear un objeto de esta clase, se parsea automáticamente.
        self.parse()

    def _parse_table_from_markdown(self, section_title: str) -> pd.DataFrame:
        """
        Helper para encontrar una tabla markdown bajo un título y convertirla a DataFrame.
        """
        try:
            # Usamos expresiones regulares para encontrar el contenido de la tabla
            # Busca el título, luego captura todo hasta la siguiente sección (##) o el final del archivo
            pattern = re.compile(rf"## \*\*{re.escape(section_title)}\*\*.*?\n(\|.*?\n)+", re.DOTALL)
            match = pattern.search(self.cv_content)
            
            if not match:
                 # Intenta con un patrón alternativo si el primero falla (ej. títulos sin negrita)
                 pattern = re.compile(rf"#{2,4} {re.escape(section_title)}.*?\n(\|.*?\n)+", re.DOTALL)
                 match = pattern.search(self.cv_content)
                 if not match:
                    return pd.DataFrame()

            table_str = match.group(0)
            
            # Limpiamos la tabla para que pandas la pueda leer
            lines = [line.strip() for line in table_str.strip().split('\n') if '|' in line]
            # Nos aseguramos de remover la línea de separador de markdown (e.g., |---|---|)
            lines = [line for line in lines if not all(c in '-| ' for c in line)]
            
            # Unimos las líneas limpias y usamos pandas para leerlas como un CSV, usando '|' como separador
            table_io = io.StringIO('\n'.join(lines))
            df = pd.read_csv(table_io, sep='|', skipinitialspace=True)
            
            # Limpiamos el DataFrame resultante
            df = df.dropna(axis=1, how='all').iloc[1:] # Elimina la primera fila vacía y la fila de cabecera de guiones
            df.columns = [col.strip() for col in df.columns]
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            df = df.rename(columns=lambda x: x.strip()) # Limpia espacios en los nombres de las columnas
            
            # La primera columna suele ser el índice (ej. 'Day')
            if df.columns[0] == 'Day':
                df.set_index('Day', inplace=True)

            return df
        except Exception as e:
            print(f"Error parseando la tabla '{section_title}': {e}")
            return pd.DataFrame()

    def parse(self):
        """
        Orquesta el proceso de parseo para extraer toda la información relevante.
        """
        # Parsear Metadata
        resource_id_match = re.search(r"- \*\*Resource ID\*\*: (\d+)", self.cv_content)
        if resource_id_match:
            self.metadata['resource_id'] = resource_id_match.group(1)

        # Parsear las tablas principales
        self.file_stats_by_day = self._parse_table_from_markdown("2. Upload Schedule and File Processing Patterns")
        self.upload_schedule_by_day = self._parse_table_from_markdown("Upload Schedule Patterns by Day") # Puede estar dentro de la sección 2

    # --- Métodos de Consulta (Getters) ---
    # Estos métodos nos darán una interfaz limpia para que los detectores obtengan datos.
    
    def get_metadata(self) -> dict:
        return self.metadata

    def get_mean_files(self, day_of_week: str) -> float:
        """Obtiene el número medio de archivos esperados para un día de la semana (Mon, Tue, Wed...)."""
        try:
            # Asegúrate de que 'Mean Files' sea el nombre exacto de la columna
            return float(self.file_stats_by_day.loc[day_of_week, 'Mean Files'])
        except (KeyError, ValueError):
            # Si el día o la columna no existen, o el valor no es un número, devuelve 0.0
            return 0.0

# --- Bloque de Prueba ---
if __name__ == "__main__":
    print("Ejecutando prueba del CVPreparer...")
    
    # 1. Cargamos todas las hojas de vida usando nuestro loader
    all_cvs = load_all_cvs()
    
    if all_cvs:
        # 2. Elegimos una para la prueba (la primera que encontremos)
        sample_cv_filename = list(all_cvs.keys())[0]
        sample_cv_content = all_cvs[sample_cv_filename]
        
        print(f"\n--- Probando con la Hoja de Vida: {sample_cv_filename} ---")
        
        # 3. Creamos una instancia de nuestro preparador
        preparer = CVPreparer(sample_cv_content)
        
        # 4. Verificamos la información parseada
        print("\nMetadata extraída:")
        print(preparer.get_metadata())
        
        print("\nTabla de Estadísticas de Archivos por Día:")
        # .head() muestra las primeras filas del DataFrame
        print(preparer.file_stats_by_day.head())
        
        # 5. Probamos uno de nuestros métodos de consulta
        day_to_test = "Tue"
        mean_files_tuesday = preparer.get_mean_files(day_to_test)
        print(f"\nConsulta: ¿Cuál es la media de archivos para un {day_to_test}?")
        print(f"Respuesta: {mean_files_tuesday}")