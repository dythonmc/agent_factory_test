import os
import json
import pandas as pd

# Definimos la ruta base donde se encuentran nuestras carpetas de datos.
BASE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

def load_daily_files(execution_date: str) -> dict:
    """Carga el archivo files.json para una fecha de ejecución específica."""
    folder_name = f"{execution_date}_20_00_UTC"
    file_path = os.path.join(BASE_DATA_PATH, folder_name, 'files.json')

    print(f"Intentando cargar: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("¡Éxito! Archivo 'files.json' cargado.")
        return data
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo {file_path} no es un JSON válido.")
        return {}

def load_last_weekday_files(execution_date: str) -> dict:
    """Carga el archivo files_last_weekday.json para una fecha de ejecución específica."""
    folder_name = f"{execution_date}_20_00_UTC"
    file_path = os.path.join(BASE_DATA_PATH, folder_name, 'files_last_weekday.json')

    print(f"\nIntentando cargar: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("¡Éxito! Archivo 'files_last_weekday.json' cargado.")
        return data
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo {file_path} no es un JSON válido.")
        return {}

def load_all_cvs() -> dict:
    """Carga todas las Hojas de Vida (CVs) desde la carpeta datasource_cvs."""
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

# --- NUEVA FUNCIÓN ---
def load_feedback_data() -> pd.DataFrame:
    """
    Carga el archivo de feedback de los stakeholders desde el archivo Excel.
    
    Returns:
        Un DataFrame de pandas con los datos del feedback.
    """
    feedback_file_path = os.path.join(BASE_DATA_PATH, 'Feedback - week 9 sept.xlsx')
    print(f"\nIntentando cargar: {feedback_file_path}")
    try:
        # Leemos el archivo excel, especificando la hoja que nos indicaste
        df = pd.read_excel(feedback_file_path, sheet_name='Feedback - week 9 sept')
        print("¡Éxito! Archivo de Feedback cargado.")
        return df
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de feedback en: {feedback_file_path}")
        return pd.DataFrame() # Devolvemos un DataFrame vacío en caso de error
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo Excel: {e}")
        return pd.DataFrame()


# --- Bloque de Prueba (ACTUALIZADO) ---
if __name__ == "__main__":
    
    test_date = '2025-09-12'

    daily_files_data = load_daily_files(test_date)
    if daily_files_data:
        print(f"IDs de fuentes de datos para el {test_date}: {list(daily_files_data.keys())[:5]}...")
        
    last_weekday_data = load_last_weekday_files(test_date)
    if last_weekday_data:
        print(f"IDs de fuentes de datos de la semana pasada: {list(last_weekday_data.keys())[:5]}...")

    cvs = load_all_cvs()
    if cvs:
        first_cv_filename = list(cvs.keys())[0]
        print(f"\n--- Muestra de la Hoja de Vida '{first_cv_filename}' ---")
        print(cvs[first_cv_filename][:300] + "...")
        
    # Prueba de la nueva función de feedback
    feedback_df = load_feedback_data()
    if not feedback_df.empty:
        print("\n--- Muestra del archivo de Feedback ---")
        # .head() nos muestra las primeras 5 filas del archivo
        print(feedback_df.head())