import argparse
from adk.agent import Agent

if __name__ == "__main__":
    # 1. Configuramos el lector de argumentos de la línea de comandos
    parser = argparse.ArgumentParser(description="Agente de IA para la detección de incidencias en datos transaccionales.")
    parser.add_argument(
        "--date",
        type=str,
        default='2025-09-12', # Valor por defecto si no se especifica ninguna fecha
        help="La fecha de ejecución para el análisis en formato YYYY-MM-DD."
    )
    args = parser.parse_args()
    
    # Usamos la fecha que se pasó como argumento
    EXECUTION_DATE = args.date

    # 2. El resto del script es igual
    agent = Agent(execution_date=EXECUTION_DATE)
    found_incidents = agent.run()

    if not found_incidents:
        print("¡Todo bien! No se encontraron incidencias.")
    else:
        print(f"\nResumen: Se encontraron un total de {len(found_incidents)} incidencias.")
        for incident in found_incidents:
            # Imprimimos de una forma un poco más legible
            print(f"- Fuente: {incident.get('source_id')}, Tipo: {incident.get('type')}, Severidad: {incident.get('severity')}, Detalles: {incident.get('description')}")