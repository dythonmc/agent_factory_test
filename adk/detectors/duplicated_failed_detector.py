from collections import Counter
from adk.detectors.base_detector import BaseDetector
from adk.preparers.cv_preparer import CVPreparer

class DuplicatedAndFailedFileDetector(BaseDetector):
    """
    Detecta archivos duplicados (por flag o por nombre) y archivos fallidos.
    Esta versión mejorada cumple con la definición completa del problema.
    """
    def detect(self, execution_date: str, cv_preparer: CVPreparer, daily_files: list, last_weekday_files: list) -> list:

        incidents = []
        source_id = cv_preparer.get_metadata().get('resource_id', 'N/A')
        
        # Paso 1: Contar la frecuencia de cada nombre de archivo para detectar duplicados por nombre.
        filenames = [f.get('filename') for f in daily_files if f.get('filename')]
        filename_counts = Counter(filenames)
        
        # Usamos un set para reportar solo una vez los duplicados por nombre
        reported_by_name = set()

        for file_info in daily_files:
            filename = file_info.get('filename', 'Nombre de archivo no encontrado')

            # Condición 1: Detectar por el flag is_duplicated = True
            if file_info.get('is_duplicated'):
                incident = {
                    'source_id': source_id,
                    'filename': filename,
                    'type': 'Archivo Duplicado (Flag)',
                    'severity': 'URGENTE',
                    'description': f"El archivo '{filename}' está marcado explícitamente como duplicado."
                }
                incidents.append(incident)

            # Condición 2: Detectar por el status de fallo
            # Usamos 'elif' para no reportar un archivo fallido si ya fue reportado como duplicado por flag
            elif file_info.get('status') == 'STOPPED':
                incident = {
                    'source_id': source_id,
                    'filename': filename,
                    'type': 'Archivo Fallido',
                    'severity': 'URGENTE',
                    'description': f"El procesamiento del archivo '{filename}' falló (status: STOPPED)."
                }
                incidents.append(incident)

            # Condición 3: Detectar por nombre de archivo repetido
            if filename in filename_counts and filename_counts[filename] > 1 and filename not in reported_by_name:
                incident = {
                    'source_id': source_id,
                    'filename': filename,
                    'type': 'Archivo Duplicado (Nombre)',
                    'severity': 'REQUIERE ATENCIÓN', # Podría ser menos crítico que un flag explícito
                    'description': f"El nombre de archivo '{filename}' aparece {filename_counts[filename]} veces en la carga del día."
                }
                incidents.append(incident)
                reported_by_name.add(filename) # Lo añadimos para no volver a reportarlo

        return incidents