import os
import json
import pandas as pd
# Ya no necesitamos timedelta, así que lo quitamos para mayor limpieza
from datetime import datetime

BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

def load_daily_files(execution_date: str) -> dict:
    """
    Carga y filtra files.json para incluir solo archivos cuyo 'uploaded_at' 
    corresponde a la fecha de ejecución.
    """
    folder_name = f"{execution_date}_20_00_UTC"
    file_path = os.path.join(BASE_DATA_PATH, folder_name, 'files.json')

    print(f"Intentando cargar: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Filtrando 'daily_files' para que 'uploaded_at' coincida con la fecha: {execution_date}")
        filtered_data = {}
        total_files_before = sum(len(files) for files in data.values())
        
        for source_id, files in data.items():
            filtered_files_for_source = [
                file_info for file_info in files 
                if file_info.get('uploaded_at', '').startswith(execution_date)
            ]
            if filtered_files_for_source:
                filtered_data[source_id] = filtered_files_for_source
        
        total_files_after = sum(len(files) for files in filtered_data.values())
        print(f"Filtrado completo. Archivos antes: {total_files_before}, Archivos después: {total_files_after}")
        return filtered_data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error al cargar o procesar {file_path}: {e}")
        return {}

def load_last_weekday_files(execution_date: str) -> dict:
    """
    Carga el archivo files_last_weekday.json. 
    Se asume que este archivo ya está pre-filtrado con los datos correctos.
    """
    folder_name = f"{execution_date}_20_00_UTC"
    file_path = os.path.join(BASE_DATA_PATH, folder_name, 'files_last_weekday.json')

    print(f"\nIntentando cargar: {file_path} (sin filtro adicional)")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("¡Éxito! Archivo 'files_last_weekday.json' cargado.")
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error al cargar o procesar {file_path}: {e}")
        return {}

# --- Las demás funciones no cambian ---
def load_all_cvs() -> dict:
    cvs_path = os.path.join(BASE_DATA_PATH, 'datasource_cvs')
    cv_data = {}
    print(f"\nCargando Hojas de Vida desde: {cvs_path}")
    try:
        for filename in os.listdir(cvs_path):
            if filename.endswith('_native.md'):
                file_path = os.path.join(cvs_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    cv_data[filename] = f.read()
        print(f"¡Éxito! Se cargaron {len(cv_data)} Hojas de Vida.")
        return cv_data
    except FileNotFoundError:
        print(f"Error: No se encontró la carpeta de Hojas de Vida en: {cvs_path}")
        return {}

def load_feedback_data() -> pd.DataFrame:
    feedback_file_path = os.path.join(BASE_DATA_PATH, 'Feedback - week 9 sept.xlsx')
    print(f"\nIntentando cargar: {feedback_file_path}")
    try:
        df = pd.read_excel(feedback_file_path, sheet_name='Feedback - week 9 sept')
        print("¡Éxito! Archivo de Feedback cargado.")
        return df
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo Excel: {e}")
        return pd.DataFrame()