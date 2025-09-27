from abc import ABC, abstractmethod
from adk.preparers.cv_preparer import CVPreparer

class BaseDetector(ABC):
    """
    Clase base abstracta para todos los detectores de incidencias.
    Define el contrato que cada detector debe seguir.
    """

    @abstractmethod
    def detect(self, execution_date: str, cv_preparer: CVPreparer, daily_files: list, last_weekday_files: list) -> list:
        """
        Método principal que ejecuta la lógica de detección.

        Args:
            cv_preparer: Una instancia de CVPreparer con la data del CV ya parseada.
            daily_files: Una lista de diccionarios, cada uno representando un archivo del día actual.
            last_weekday_files: Una lista de diccionarios de archivos del mismo día de la semana anterior.

        Returns:
            Una lista de diccionarios, donde cada diccionario es una incidencia encontrada.
            Si no se encuentran incidencias, devuelve una lista vacía.
        """
        pass