from datetime import datetime
from adk.detectors.base_detector import BaseDetector
from adk.preparers.cv_preparer import CVPreparer

class MissingFileDetector(BaseDetector):
    """
    Detecta si la cantidad de archivos recibidos en un día es significativamente
    menor que la media esperada para ese día de la semana, según el CV.
    """
    def detect(self, execution_date: str, cv_preparer: CVPreparer, daily_files: list, last_weekday_files: list) -> list:
        incidents = []
        source_id = cv_preparer.get_metadata().get('resource_id', 'N/A')

        # --- INICIO DE LÍNEAS DE DEPURACIÓN ---
        print(f"\n--- Analizando fuente {source_id} con MissingFileDetector ---")
        # --- FIN DE LÍNEAS DE DEPURACIÓN ---
        
        try:
            date_obj = datetime.strptime(execution_date, '%Y-%m-%d')
            day_name = date_obj.strftime('%a')
            expected_mean_files = cv_preparer.get_mean_files(day_name)
            actual_files = len(daily_files)

            # --- INICIO DE LÍNEAS DE DEPURACIÓN ---
            print(f"Día de la semana: {day_name} ({date_obj.strftime('%A')})")
            print(f"Archivos esperados (media del CV): {expected_mean_files}")
            print(f"Archivos reales recibidos: {actual_files}")
            # --- FIN DE LÍNEAS DE DEPURACIÓN ---

            if expected_mean_files > 0 and actual_files < expected_mean_files:
                # --- INICIO DE LÍNEAS DE DEPURACIÓN ---
                print("Veredicto: ¡INCIDENCIA! Se encontraron archivos faltantes.")
                # --- FIN DE LÍNEAS DE DEPURACIÓN ---
                incident = {
                    'source_id': source_id,
                    'filename': 'N/A',
                    'type': 'Archivos Faltantes',
                    'severity': 'REQUIERE ATENCIÓN',
                    'description': (
                        f"Se recibieron {actual_files} archivos, pero se esperaban en promedio "
                        f"{expected_mean_files:.1f} para un {date_obj.strftime('%A')}."
                    )
                }
                incidents.append(incident)
            else:
                # --- INICIO DE LÍNEAS DE DEPURACIÓN ---
                print(f"Veredicto: OK. No se reporta incidencia porque {actual_files} no es menor que {expected_mean_files}.")
                # --- FIN DE LÍNEAS DE DEPURACIÓN ---
                
        except Exception as e:
            print(f"WARN: No se pudo ejecutar MissingFileDetector para la fuente {source_id}. Error: {e}")
            
        return incidents