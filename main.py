from adk.agent import Agent

if __name__ == "__main__":
    # Define la fecha para la cual quieres correr el análisis
    EXECUTION_DATE = '2025-09-12'

    # 1. Crea una instancia del agente para esa fecha
    agent = Agent(execution_date=EXECUTION_DATE)

    # 2. Ejecuta el análisis
    found_incidents = agent.run()

    # 3. Muestra los resultados
    if not found_incidents:
        print("¡Todo bien! No se encontraron incidencias.")
    else:
        print(f"\nResumen: Se encontraron un total de {len(found_incidents)} incidencias.")
        for incident in found_incidents:
            print(f"- {incident}")