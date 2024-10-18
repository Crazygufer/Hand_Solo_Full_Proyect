import json
import os

# Obtener la ruta del directorio del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ajustamos las rutas correctas
acciones_path = os.path.join(BASE_DIR, "actions.json")  # Para actions.json dentro de detect_action_words
transcripciones_path = os.path.join(BASE_DIR, "../../transcripciones/transcripciones.json")  # Sube dos niveles y entra a transcripciones

# Función para cargar las acciones desde el archivo actions.json
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

# Función para cargar la última transcripción válida desde el archivo transcripciones.json
def cargar_ultima_transcripcion(transcripciones_path):
    try:
        with open(transcripciones_path, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if datos:
                # Filtramos las transcripciones no vacías
                transcripciones_validas = [t["transcription"] for t in datos if t["transcription"].strip() != ""]
                if transcripciones_validas:
                    # Obtener la última transcripción no vacía
                    return transcripciones_validas[-1]
                else:
                    print("No se encontraron transcripciones válidas.")
                    return None
            else:
                print("El archivo de transcripciones está vacío.")
                return None
    except FileNotFoundError:
        print(f"Archivo no encontrado: {transcripciones_path}")
        return None
    except json.JSONDecodeError:
        print("Error al leer el archivo de transcripciones.")
        return None

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

    # Cargar la última transcripción no vacía desde el archivo transcripciones.json
    ultima_transcripcion = cargar_ultima_transcripcion(transcripciones_path)

    if ultima_transcripcion:
        print(f"Última transcripción: {ultima_transcripcion}")
    
        # Detectar la acción basada en la última transcripción
        accion_detectada = detectar_accion(ultima_transcripcion, acciones)

        if accion_detectada:
            print(f"Acción detectada correctamente: {accion_detectada}")
        else:
            print("No se detectó ninguna acción.")
    else:
        print("No se pudo cargar la última transcripción.")
