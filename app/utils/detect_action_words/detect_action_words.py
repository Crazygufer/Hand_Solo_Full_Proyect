import json
import os
import subprocess
import requests
import sys

# Usar el intérprete del entorno virtual
subprocess.run([sys.executable, 'C:/sers/enfparedes/Contacts/Hand_Solo_Full_Proyect/app/utils/kinematics/botar_secuencia.py'])


class TranscriptionManager:
    def __init__(self, transcripciones_path):
        self.transcripciones_path = transcripciones_path

    def cargar_ultima_transcripcion(self):
        """Carga la última transcripción válida desde el archivo JSON."""
        try:
            with open(self.transcripciones_path, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                if datos:
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
                    
                    # Si se detecta la acción "botar", ejecutar la secuencia de botar
                    if accion == "botar":
                        self.ejecutar_botar_secuencia()
                    
                    return accion
            print("No se detectaron acciones.")
            return None
        else:
            print("Transcripción vacía o nula.")
            return None
        
    def ejecutar_botar_secuencia(self):
        """Ejecuta el script de la secuencia de botar."""
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        botar_script_path = os.path.join(BASE_DIR, "../kinematics/botar_secuencia.py")

        try:
            # Ejecutar el script de secuencia
            subprocess.Popen(["python", botar_script_path])
            print("Secuencia de botar iniciada.")
        except Exception as e:
            print(f"Error al iniciar la secuencia de botar: {e}")

def guardar_resultado_accion(accion):
    """Guarda la acción detectada en un archivo JSON para que Flask pueda leerlo."""
    resultado = {
        "keyword": accion or "Ninguna palabra clave detectada",
        "action": f"Ejecutar acción: {accion}" if accion else "Esperando comandos..."
    }
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    resultado_path = os.path.join(BASE_DIR, "../../transcripciones/resultados_palabras_clave.json")
    
    with open(resultado_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

# Punto de entrada para el sistema
if __name__ == "__main__":
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

        # Guardar la acción detectada en un archivo JSON para que Flask la lea
        guardar_resultado_accion(accion_detectada)
    else:
        print("No se pudo cargar la última transcripción.")
