import json
import os
import requests

class TranscriptionManager:
    """Maneja la carga y obtención de la última transcripción válida."""
    
    def __init__(self, transcripciones_path):
        self.transcripciones_path = transcripciones_path

    def cargar_ultima_transcripcion(self):
        """Carga la última transcripción válida desde el archivo JSON."""
        try:
            with open(self.transcripciones_path, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                transcripciones_validas = [
                    t["transcription"] for t in datos if t["transcription"].strip()
                ]
                return transcripciones_validas[-1] if transcripciones_validas else None
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error al cargar la transcripción: {e}")
            return None


class KeywordDetector:
    """Maneja la carga y detección de palabras clave en las transcripciones."""
    
    def __init__(self, acciones_path):
        self.acciones_path = acciones_path
        self.acciones = self.cargar_acciones()

    def cargar_acciones(self):
        """Carga las acciones y palabras clave desde el archivo JSON."""
        try:
            with open(self.acciones_path, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error al cargar acciones: {e}")
            return {}

    def detectar_accion(self, transcripcion):
        """Detecta la acción basada en la transcripción y devuelve la acción."""
        if transcripcion:
            transcripcion_lower = transcripcion.lower()
            for accion, palabras_clave in self.acciones.items():
                if any(palabra in transcripcion_lower for palabra in palabras_clave):
                    print(f"Acción detectada: {accion}")
                    return accion
        print("No se detectaron acciones.")
        return None


class ActionManager:
    """Gestiona la ejecución de acciones detectadas."""
    
    def __init__(self, flask_url):
        self.flask_url = flask_url

    def ejecutar_accion(self, accion):
        """Ejecuta la acción si es 'botar', enviando la solicitud correspondiente."""
        if accion == "botar":
            print("Enviando solicitud para iniciar secuencia de botar...")
            self.enviar_solicitud_botar()

    def enviar_solicitud_botar(self):
        """Envía una solicitud POST a Flask para iniciar la secuencia de botar."""
        try:
            response = requests.post(self.flask_url)
            if response.status_code == 200:
                print("Secuencia de botar iniciada exitosamente desde Flask.")
            else:
                print(f"Error en la solicitud: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error al conectar con Flask: {e}")


class ResultLogger:
    """Guarda el resultado de la detección de palabras clave en un archivo JSON."""
    
    @staticmethod
    def guardar_resultado_accion(accion, resultado_path):
        """Guarda la acción detectada en un archivo JSON."""
        resultado = {
            "keyword": accion or "Ninguna palabra clave detectada",
            "action": f"Ejecutar acción: {accion}" if accion else "Esperando comandos..."
        }
        with open(resultado_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    transcripciones_path = os.path.join(BASE_DIR, "../../transcripciones/transcripciones.json")
    acciones_path = os.path.join(BASE_DIR, "actions.json")
    resultado_path = os.path.join(BASE_DIR, "../../transcripciones/resultados_palabras_clave.json")
    flask_url = "http://127.0.0.1:5000/ejecutar_botar"

    # Instanciar las clases
    transcription_manager = TranscriptionManager(transcripciones_path)
    keyword_detector = KeywordDetector(acciones_path)
    action_manager = ActionManager(flask_url)

    # Procesar la última transcripción
    ultima_transcripcion = transcription_manager.cargar_ultima_transcripcion()
    if ultima_transcripcion:
        print(f"Última transcripción: {ultima_transcripcion}")
        accion_detectada = keyword_detector.detectar_accion(ultima_transcripcion)
        action_manager.ejecutar_accion(accion_detectada)
        ResultLogger.guardar_resultado_accion(accion_detectada, resultado_path)
    else:
        print("No se pudo cargar la última transcripción.")
