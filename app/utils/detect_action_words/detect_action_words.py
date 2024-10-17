import json

class KeywordDetector:
    def __init__(self, transcripcion_path, keywords):
        """
        Constructor para la clase KeywordDetector.
        :param transcripcion_path: Ruta al archivo JSON con las transcripciones.
        :param keywords: Lista de palabras clave para detectar.
        """
        self.transcripcion_path = transcripcion_path
        self.keywords = keywords
    
    def cargar_ultima_transcripcion(self):
        """
        Carga la última transcripción desde el archivo JSON.
        :return: Última transcripción o None si no hay transcripciones.
        """
        try:
            with open(self.transcripcion_path, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                if datos and "transcripciones" in datos:
                    ultima_transcripcion = datos["transcripciones"][-1]["text"]
                    return ultima_transcripcion
                else:
                    print("No se encontraron transcripciones en el archivo.")
                    return None
        except FileNotFoundError:
            print(f"Archivo no encontrado: {self.transcripcion_path}")
            return None
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
            return None
    
    def detectar_palabra_clave(self, transcripcion):
        """
        Detecta si alguna palabra clave está presente en la transcripción.
        :param transcripcion: Texto de la transcripción.
        :return: Palabra clave encontrada o None si no hay coincidencia.
        """
        if transcripcion:
            transcripcion_lower = transcripcion.lower()
            for palabra in self.keywords:
                if palabra in transcripcion_lower:
                    print(f"Palabra clave detectada: {palabra}")
                    return palabra
            print("No se detectaron palabras clave.")
            return None
        else:
            print("Transcripción vacía o nula.")
            return None
