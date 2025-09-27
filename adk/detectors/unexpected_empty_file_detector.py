from datetime import datetime
from adk.detectors.base_detector import BaseDetector
from adk.preparers.cv_preparer import CVPreparer

class UnexpectedEmptyFileDetector(BaseDetector):
    """
    Detecta archivos con 0 filas, pero solo si no es un patrón esperado
    según la Hoja de Vida (CV) para ese día de la semana.
    """
    def detect(self, execution_date: str, cv_preparer: CVPreparer, daily_files: list, last_weekday_files: list) -> list:
        incidents = []
        source_id = cv_preparer.get_metadata().get('resource_id', 'N/A')

        try:
            date_obj = datetime.strptime(execution_date, '%Y-%m-%d')
            day_name = date_obj.strftime('%a')

            # 1. Consultar el CV para ver si se esperan archivos vacíos hoy.
            mean_empty_files_expected = cv_preparer.get_mean_empty_files(day_name)
            
            # 2. Si la media esperada de archivos vacíos es mayor a 0, significa
            #    que es un comportamiento normal y no debemos reportarlo como incidencia.
            if mean_empty_files_expected > 0:
                return []

            # 3. Si la media esperada es 0, entonces ningún archivo debería llegar vacío.
            #    Procedemos a revisar cada archivo.
            for file_info in daily_files:
                rows = file_info.get('rows', -1) # Usamos -1 para diferenciar de un 0 real

                if rows == 0:
                    incident = {
                        'source_id': source_id,
                        'filename': file_info.get('filename', 'N/A'),
                        'type': 'Archivo Vacío Inesperado',
                        'severity': 'REQUIERE ATENCIÓN',
                        'description': (
                            f"El archivo '{file_info.get('filename', 'N/A')}' tiene 0 filas, "
                            f"pero el patrón histórico para un {date_obj.strftime('%A')} indica que no se esperan archivos vacíos."
                        )
                    }
                    incidents.append(incident)

        except Exception as e:
            print(f"WARN: No se pudo ejecutar UnexpectedEmptyFileDetector para la fuente {source_id}. Error: {e}")
            
        return incidents