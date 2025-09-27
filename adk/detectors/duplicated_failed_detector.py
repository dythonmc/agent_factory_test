from collections import Counter
from adk.detectors.base_detector import BaseDetector
from adk.preparers.cv_preparer import CVPreparer

class DuplicatedAndFailedFileDetector(BaseDetector):
    """
    Detecta archivos duplicados (por flag o por nombre) y archivos fallidos.
    (Versión con logs de depuración y corrección de mayúsculas/minúsculas)
    """
    def detect(self, execution_date: str, cv_preparer: CVPreparer, daily_files: list, last_weekday_files: list) -> list:
        incidents = []
        source_id = cv_preparer.get_metadata().get('resource_id', 'N/A')
        
        print(f"\n--- [DEBUG] Analizando Fuente {source_id} con DuplicatedAndFailedFileDetector ---")
        print(f"Total de archivos (ya filtrados por fecha) a revisar: {len(daily_files)}")

        if not daily_files:
            print("No hay archivos para analizar. Terminando.")
            print("--------------------------------------------------------------------")
            return []

        filenames = [f.get('filename') for f in daily_files if f.get('filename')]
        filename_counts = Counter(filenames)
        duplicates_by_name = {name: count for name, count in filename_counts.items() if count > 1}

        # Usamos .lower() en la comprobación de status para la depuración
        flags_found = [f.get('filename') for f in daily_files if f.get('is_duplicated')]
        stopped_found = [f.get('filename') for f in daily_files if f.get('status', '').lower() == 'stopped']
        
        print(f"Archivos con flag 'is_duplicated=True': {len(flags_found)} -> {flags_found if flags_found else 'Ninguno'}")
        print(f"Archivos con status 'stopped': {len(stopped_found)} -> {stopped_found if stopped_found else 'Ninguno'}")
        print(f"Duplicados por nombre encontrados: {duplicates_by_name if duplicates_by_name else 'Ninguno'}")

        reported_by_name = set()
        for file_info in daily_files:
            filename = file_info.get('filename', 'Nombre de archivo no encontrado')
            if file_info.get('is_duplicated'):
                incidents.append({'source_id': source_id, 'filename': filename, 'type': 'Archivo Duplicado (Flag)', 'severity': 'URGENTE', 'description': f"El archivo '{filename}' está marcado explícitamente como duplicado."})
            
            # --- LÍNEA CORREGIDA ---
            # Convertimos el status a minúsculas antes de comparar
            elif file_info.get('status', '').lower() == 'stopped':
                incidents.append({'source_id': source_id, 'filename': filename, 'type': 'Archivo Fallido', 'severity': 'URGENTE', 'description': f"El procesamiento del archivo '{filename}' falló (status: stopped)."})
            
            if filename in filename_counts and filename_counts[filename] > 1 and filename not in reported_by_name:
                incidents.append({'source_id': source_id, 'filename': filename, 'type': 'Archivo Duplicado (Nombre)', 'severity': 'REQUIERE ATENCIÓN', 'description': f"El nombre de archivo '{filename}' aparece {filename_counts[filename]} veces en la carga del día."})
                reported_by_name.add(filename)
        
        print(f"Veredicto: Se encontraron {len(incidents)} incidencias para esta fuente.")
        print("--------------------------------------------------------------------")
        return incidents