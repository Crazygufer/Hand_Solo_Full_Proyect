import json
import os

class TranscriptionManager:
    def __init__(self, transcripciones_path):
        self.transcripciones_path = transcripciones_path

    def cargar_ultima_transcripcion(self):
        """Carga la última transcripción válida desde el archivo JSON."""
        try:
            with open(self.transcripciones_path, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                if datos:
                    # Filtrar las transcripciones no vacías
                    transcripciones_validas = [t["transcription"] for t in datos if t["transcription"].strip() != ""]
                    if transcripciones_validas:
                        return transcripciones_validas[-1]
                    else:
                        print("No se encontraron transcripciones válidas.")
                        return None
                else:
                    print("El archivo de transcripciones está vacío.")
                    return None
        except FileNotFoundError:
            print(f"Archivo no encontrado: {self.transcripciones_path}")
            return None
        except json.JSONDecodeError:
            print("Error al leer el archivo de transcripciones.")
            return None


class KeywordDetector:
    def __init__(self, acciones_path):
        self.acciones_path = acciones_path
        self.acciones = self.cargar_acciones()

    def cargar_acciones(self):
        """Carga las acciones y palabras clave desde el archivo JSON."""
        try:
            with open(self.acciones_path, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            print(f"Archivo no encontrado: {self.acciones_path}")
            return {}
        except json.JSONDecodeError:
            print("Error al leer el archivo de acciones.")
            return {}

    def detectar_accion(self, transcripcion):
        """Detecta la acción basada en la transcripción."""
        if transcripcion:
            transcripcion_lower = transcripcion.lower()
            for accion, palabras_clave in self.acciones.items():
                if any(palabra in transcripcion_lower for palabra in palabras_clave):
                    print(f"Acción detectada: {accion}")
                    return accion
            print("No se detectaron acciones.")
            return None
        else:
            print("Transcripción vacía o nula.")
            return None


# Punto de entrada para el sistema
if __name__ == "__main__":
    # Rutas de los archivos JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    transcripciones_path = os.path.join(BASE_DIR, "../../transcripciones/transcripciones.json")
    acciones_path = os.path.join(BASE_DIR, "actions.json")

    # Instanciar la clase TranscriptionManager
    transcription_manager = TranscriptionManager(transcripciones_path)

    # Cargar la última transcripción válida
    ultima_transcripcion = transcription_manager.cargar_ultima_transcripcion()

    if ultima_transcripcion:
        print(f"Última transcripción: {ultima_transcripcion}")

        # Instanciar la clase KeywordDetector
        keyword_detector = KeywordDetector(acciones_path)

        # Detectar la acción basada en la última transcripción
        accion_detectada = keyword_detector.detectar_accion(ultima_transcripcion)

        if accion_detectada:
            print(f"Acción detectada correctamente: {accion_detectada}")
        else:
            print("No se detectó ninguna acción.")
    else:
        print("No se pudo cargar la última transcripción.")
