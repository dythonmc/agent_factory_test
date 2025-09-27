import os
import importlib
import inspect

from loader import load_daily_files, load_last_weekday_files, load_all_cvs
from adk.preparers.cv_preparer import CVPreparer
from adk.detectors.base_detector import BaseDetector

class Agent:
    def __init__(self, execution_date: str):
        self.execution_date = execution_date
        self.detectors = []
        self._load_detectors()

    def _load_detectors(self):
        """
        Descubre e carga dinámicamente todas las clases de detectores
        que se encuentren en la carpeta 'adk/detectors'.
        """
        detectors_path = os.path.join(os.path.dirname(__file__), 'detectors')
        for filename in os.listdir(detectors_path):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base_detector.py']:
                module_name = f"adk.detectors.{filename[:-3]}"
                module = importlib.import_module(module_name)

                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, BaseDetector) and cls is not BaseDetector:
                        self.detectors.append(cls)
                        print(f"Detector '{cls.__name__}' cargado exitosamente.")

    def run(self) -> list:
        """
        Orquesta todo el proceso de detección de incidencias.
        """
        print(f"\n--- Iniciando ejecución del Agente para la fecha: {self.execution_date} ---")

        # 1. Cargar todos los datos necesarios
        daily_files_by_source = load_daily_files(self.execution_date)
        last_weekday_files_by_source = load_last_weekday_files(self.execution_date)
        all_cvs_content = load_all_cvs()

        # Mapear resource_id a contenido de CV para fácil acceso
        cv_by_resource_id = {}
        for filename, content in all_cvs_content.items():
            resource_id = filename.split('_')[0]
            cv_by_resource_id[resource_id] = content

        all_incidents = []

        # 2. Iterar por cada fuente de datos encontrada en el día
        for source_id, daily_files in daily_files_by_source.items():
            print(f"\nAnalizando fuente de datos ID: {source_id}...")

            if source_id not in cv_by_resource_id:
                print(f"Advertencia: No se encontró Hoja de Vida para la fuente {source_id}. Saltando.")
                continue

            # 3. Preparar los datos para esta fuente
            cv_content = cv_by_resource_id[source_id]
            cv_preparer = CVPreparer(cv_content)
            last_weekday_files = last_weekday_files_by_source.get(source_id, [])

            # 4. Ejecutar cada detector para esta fuente
            for detector_class in self.detectors:
                detector_instance = detector_class() # Creamos una instancia del detector
                incidents = detector_instance.detect(cv_preparer, daily_files, last_weekday_files)

                if incidents:
                    print(f"  -> Detector '{detector_class.__name__}' encontró {len(incidents)} incidencia(s).")
                    all_incidents.extend(incidents)

        print("\n--- Análisis completado ---")
        return all_incidents