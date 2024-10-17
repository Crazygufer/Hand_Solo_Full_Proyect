import json

# Simulamos el archivo de acciones que contiene las palabras clave
acciones_path = "Hand_Solo_Full_Proyect/app/utils/detect_action_words/actions.json"

# Función para cargar las acciones desde el archivo JSON
def cargar_acciones(acciones_path):
    try:
        with open(acciones_path, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print(f"Archivo no encontrado: {acciones_path}")
        return {}
    except json.JSONDecodeError:
        print("Error al leer el archivo de acciones.")
        return {}

# Función para detectar si alguna palabra clave está presente en la transcripción
def detectar_accion(transcripcion, acciones):
    if transcripcion:
        transcripcion_lower = transcripcion.lower()
        for accion, palabras_clave in acciones.items():
            if any(palabra in transcripcion_lower for palabra in palabras_clave):
                print(f"Acción detectada: {accion}")
                return accion
        print("No se detectaron acciones.")
        return None
    else:
        print("Transcripción vacía o nula.")
        return None

if __name__ == "__main__":
    # Cargar las acciones desde el archivo JSON
    acciones = cargar_acciones(acciones_path)

    # Simulamos una transcripción para probar
    transcripcion_prueba = "Handi debería comenzar a bailar ahora."

    print(f"Transcripción de prueba: {transcripcion_prueba}")
    
    # Detectar la acción basada en la transcripción de prueba
    accion_detectada = detectar_accion(transcripcion_prueba, acciones)

    if accion_detectada:
        print(f"Acción detectada correctamente: {accion_detectada}")
    else:
        print("No se detectó ninguna acción.")
