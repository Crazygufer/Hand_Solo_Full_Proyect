import speech_recognition as sr
import whisper
import os
import json
import time
from datetime import datetime
import sys
import pyttsx3
import requests

# Configuración de pyttsx3 para la respuesta de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Definir rutas específicas para archivos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
TRANSCRIPCIONES_DIR = os.path.join(BASE_DIR, "transcripciones")

# Crear carpetas si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# URLs de Flask
FLASK_URL_TRANSCRIPTION = 'http://127.0.0.1:5000/update_transcription_auto'
FLASK_URL_DETECT_ACTION = 'http://127.0.0.1:5000/detect_action'
FLASK_URL_EXECUTE_BOTAR = 'http://127.0.0.1:5000/ejecutar_botar'

# Obtener el session_id del argumento pasado por `routes.py`
session_id = sys.argv[1] if len(sys.argv) > 1 else str(int(time.time()))

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def grabar_audio(self):
        with self.mic as source:
            print("Grabando audio...")
            audio_data = self.recognizer.listen(source, timeout=10)
            audio_filename = os.path.join(AUDIO_DIR, "audio_temp.wav")
            with open(audio_filename, "wb") as f:
                f.write(audio_data.get_wav_data())
            return audio_filename

    def eliminar_audio(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

class TranscriptionManager:
    def __init__(self, model):
        self.model = model

    def transcribir_audio(self, audio_filename):
        if os.path.exists(audio_filename):
            print(f"Transcribiendo el archivo de audio: {audio_filename}")
            result = self.model.transcribe(audio_filename, language="es")
            return result["text"]
        else:
            print("No se encontró el archivo de audio.")
            return ""

    def guardar_transcripcion(self, transcription_text, session_id):
        transcriptions_file = os.path.join(TRANSCRIPCIONES_DIR, "transcripciones.json")

        if not os.path.exists(transcriptions_file):
            with open(transcriptions_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        with open(transcriptions_file, 'r', encoding='utf-8') as f:
            transcriptions = json.load(f)

        transcriptions.append({
            "session_id": session_id,
            "transcription": transcription_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        with open(transcriptions_file, 'w', encoding='utf-8') as f:
            json.dump(transcriptions, f, ensure_ascii=False, indent=4)

        print(f"Transcripción guardada en {transcriptions_file}")

class VoiceAssistant:
    def __init__(self, audio_manager, transcription_manager, flask_url_transcription, flask_url_detect_action, session_id):
        self.audio_manager = audio_manager
        self.transcription_manager = transcription_manager
        self.flask_url_transcription = flask_url_transcription
        self.flask_url_detect_action = flask_url_detect_action
        self.session_id = session_id

    def responder_voz(self, mensaje):
        engine.say(mensaje)
        engine.runAndWait()

    def send_transcription_to_flask(self, transcription):
        data = {
            "transcription": transcription,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.session_id
        }
        try:
            requests.post(self.flask_url_transcription, json=data)
            print(f"Transcripción enviada al servidor: {transcription}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la transcripción al servidor: {e}")

    def detectar_wake_word(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        print("Esperando la wake word: 'oye handy'...")
        self.send_transcription_to_flask("Esperando la wake word: 'oye handy'...")

        while True:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Escuchando...")
                audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Has dicho: {text}")
                self.send_transcription_to_flask(f"Has dicho: {text}")

                if "oye handy" in text:
                    print("Wake word detectada, comenzando transcripción...")
                    self.send_transcription_to_flask("Wake word detectada, comenzando transcripción...")
                    self.responder_voz("Hola, ¿en qué puedo ayudarte?")
                    self.iniciar_transcripcion()
                    break

            except sr.UnknownValueError:
                print("No se entendió el audio.")
                self.send_transcription_to_flask("No se entendió el audio")
                self.responder_voz("No entendí, ¿Puedes repetirlo por favor?")
            except sr.RequestError as e:
                print(f"Error al conectarse al servicio de reconocimiento de voz: {e}")

    def iniciar_transcripcion(self):
        audio_filename = self.audio_manager.grabar_audio()
        transcribed_text = self.transcription_manager.transcribir_audio(audio_filename)

        # Guardar en JSON después de transcribir
        self.transcription_manager.guardar_transcripcion(transcribed_text, self.session_id)

        # Enviar la transcripción a Flask
        self.send_transcription_to_flask(transcribed_text)

        # Enviar la transcripción a la ruta de detección de palabras clave en Flask
        self.enviar_a_detect_action(transcribed_text)

        # Eliminar el archivo de audio temporal y terminar
        self.audio_manager.eliminar_audio(audio_filename)
        print("Proceso de transcripción completado. Terminando el programa.")

    def enviar_a_detect_action(self, transcription):
        """Envía la transcripción a Flask para la detección de palabras clave."""
        data = {"transcription": transcription, "session_id": self.session_id}
        try:
            response = requests.post(self.flask_url_detect_action, json=data)
            if response.status_code == 200:
                respuesta = response.json()
                print("Transcripción enviada a Flask para detección de palabras clave.")
                
                # Revisar la respuesta de la detección y ejecutar la acción de botar si aplica
                palabra_clave = respuesta.get("keyword")
                if palabra_clave == "botar":
                    self.ejecutar_botar()
            else:
                print(f"Error al enviar transcripción a Flask: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error de conexión con Flask: {e}")

    def ejecutar_botar(self):
        """Envía una solicitud para ejecutar la secuencia de botar en Flask."""
        try:
            response = requests.post(FLASK_URL_EXECUTE_BOTAR)
            if response.status_code == 200:
                print("Secuencia de botar ejecutada exitosamente desde Flask.")
            else:
                print(f"Error en la solicitud de ejecución de botar: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error al conectar con Flask para ejecutar botar: {e}")

# Instanciar las clases
audio_manager = AudioManager()
transcription_manager = TranscriptionManager(whisper.load_model("medium"))
voice_assistant = VoiceAssistant(audio_manager, transcription_manager, FLASK_URL_TRANSCRIPTION, FLASK_URL_DETECT_ACTION, session_id)

# Iniciar la detección de la wake word y ejecutar la transcripción
voice_assistant.detectar_wake_word()
