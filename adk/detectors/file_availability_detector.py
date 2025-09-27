from datetime import datetime, timedelta
from adk.detectors.base_detector import BaseDetector
from adk.preparers.cv_preparer import CVPreparer

class FileAvailabilityDetector(BaseDetector):
    """
    Detector que verifica la disponibilidad de archivos puntuales.
    (Versión con logs de depuración)
    """
    def detect(self, execution_date: str, cv_preparer: CVPreparer, daily_files: list, last_weekday_files: list) -> list:
        incidents = []
        source_id = cv_preparer.get_metadata().get('resource_id', 'N/A')
        
        # --- INICIO DE LOGS DE DEPURACIÓN ---
        print(f"\n--- [DEBUG] Analizando Fuente {source_id} con FileAvailabilityDetector ---")
        # --- FIN DE LOGS DE DEPURACIÓN ---
        
        try:
            date_obj = datetime.strptime(execution_date, '%Y-%m-%d')
            day_name = date_obj.strftime('%a')
            expected_mean_files = cv_preparer.get_mean_files(day_name)
            time_window_str = cv_preparer.get_expected_time_window(day_name)
            actual_total_files = len(daily_files)

            # --- INICIO DE LOGS DE DEPURACIÓN ---
            print(f"Día de la semana: {day_name} ({date_obj.strftime('%A')})")
            print(f"Archivos esperados (media del CV): {expected_mean_files}")
            print(f"Ventana de tiempo esperada (del CV): {time_window_str}")
            print(f"Archivos reales recibidos (total filtrado): {actual_total_files}")
            # --- FIN DE LOGS DE DEPURACIÓN ---

            if expected_mean_files == 0:
                print("Veredicto: OK. No se esperaban archivos.")
                print("--------------------------------------------------------------------")
                return []
            
            if not time_window_str or '–' not in time_window_str:
                print("Veredicto: OK. No hay ventana de tiempo en el CV para comparar la puntualidad.")
                print("--------------------------------------------------------------------")
                return []

            start_time_str, end_time_str = time_window_str.replace(' UTC', '').split('–')
            expected_start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
            expected_end_time_obj = datetime.strptime(end_time_str, '%H:%M:%S')
            flexible_end_time = (expected_end_time_obj + timedelta(hours=4)).time()
            
            on_time_files = 0
            for file_info in daily_files:
                uploaded_at_str = file_info.get('uploaded_at')
                if uploaded_at_str:
                    upload_time = datetime.fromisoformat(uploaded_at_str).time()
                    if expected_start_time <= upload_time <= flexible_end_time:
                        on_time_files += 1

            # --- INICIO DE LOGS DE DEPURACIÓN ---
            print(f"Archivos puntuales contados: {on_time_files} (dentro de {expected_start_time} - {flexible_end_time})")
            # --- FIN DE LOGS DE DEPURACIÓN ---

            if on_time_files < expected_mean_files:
                print(f"Veredicto: ¡INCIDENCIA! {on_time_files} es menor que los {expected_mean_files} esperados.")
                incidents.append({'source_id': source_id, 'filename': 'N/A', 'type': 'Disponibilidad de Archivos', 'severity': 'REQUIERE ATENCIÓN', 'description': f"Se recibieron {on_time_files} archivos a tiempo, pero se esperaban en promedio {expected_mean_files:.1f} para un {date_obj.strftime('%A')} en la ventana horaria."})
            else:
                print(f"Veredicto: OK. {on_time_files} archivos puntuales >= {expected_mean_files} esperados.")
            
            print("--------------------------------------------------------------------")
            
        except Exception as e:
            print(f"WARN: No se pudo ejecutar FileAvailabilityDetector para la fuente {source_id}. Error: {e}")
            print("--------------------------------------------------------------------")
            
        return incidents