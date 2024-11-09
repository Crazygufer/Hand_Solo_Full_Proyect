import speech_recognition as sr
import whisper
import os
import json
import time
from datetime import datetime
import sys
import pyttsx3
import requests

# Configurar pyttsx3 para la respuesta de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Ajusta la velocidad de la voz
engine.setProperty('volume', 0.9)  # Ajusta el volumen (0.0 a 1.0)

# Definir rutas específicas para archivos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
TRANSCRIPCIONES_DIR = os.path.join(BASE_DIR, "transcripciones")

# Crear carpetas si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# URL del servidor Flask
FLASK_URL = 'http://127.0.0.1:5000/update_transcription_auto'

# Obtener el session_id del argumento pasado por `routes.py`
if len(sys.argv) > 1:
    session_id = sys.argv[1]
else:
    session_id = str(int(time.time()))  # Genera un session_id si no se pasa

class AudioManager:
    def __init__(self, audio_dir):
        self.audio_dir = audio_dir
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def grabar_audio(self):
        with self.mic as source:
            print("Grabando audio...")
            audio_data = self.recognizer.listen(source, timeout=10)
            audio_filename = os.path.join(self.audio_dir, "audio_temp.wav")
            with open(audio_filename, "wb") as f:
                f.write(audio_data.get_wav_data())
            return audio_filename

    def eliminar_audio(self, filename):
        if os.path.exists(filename):
            os.remove(filename)

class TranscriptionManager:
    def __init__(self, transcripciones_dir, model):
        self.transcripciones_dir = transcripciones_dir
        self.model = model

    def transcribir_audio(self, audio_filename):
        if os.path.exists(audio_filename):
            print(f"Archivo de audio encontrado: {audio_filename}, iniciando transcripción...")
            result = self.model.transcribe(audio_filename, language="es")
            return result["text"]
        else:
            print("No se encontró el archivo de audio.")
            return ""

    def guardar_transcripcion(self, transcription_text, session_id):
        transcriptions_file = os.path.join(self.transcripciones_dir, "transcripciones.json")

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
    def __init__(self, audio_manager, transcription_manager, flask_url, session_id):
        self.audio_manager = audio_manager
        self.transcription_manager = transcription_manager
        self.flask_url = flask_url
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
            requests.post(self.flask_url, json=data)
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
                self.send_transcription_to_flask("Escuchando...")
                audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Has dicho: {text}")
                self.send_transcription_to_flask(f"Has dicho: {text}")

                if "oye handy salir" in text:
                    print("Frase de salida detectada: 'oye handy salir'. Terminando programa...")
                    self.send_transcription_to_flask("Frase de salida detectada: 'oye handy salir'. Terminando Programa...")
                    self.responder_voz("Adiós, hasta la próxima.")
                    sys.exit()

                if "oye handy" in text:
                    print("Wake word detectada, comenzando transcripción...")
                    self.send_transcription_to_flask("Wake word detectada, comenzando transcripción...")
                    self.responder_voz("Hola, ¿en qué puedo ayudarte?")
                    self.iniciar_transcripcion()

            except sr.UnknownValueError:
                print("No se entendió el audio.")
                self.send_transcription_to_flask("No se entendió el audio")
                self.responder_voz("No entendí, ¿Puedes repetirlo por favor?")
            except sr.RequestError as e:
                print(f"Error al conectarse al servicio de reconocimiento de voz: {e}")

    def iniciar_transcripcion(self):
        audio_filename = self.audio_manager.grabar_audio()
        transcribed_text = self.transcription_manager.transcribir_audio(audio_filename)

        # Enviar la transcripción a Flask
        self.send_transcription_to_flask(transcribed_text)

        # Guardar la transcripción en el archivo JSON con el session_id
        self.transcription_manager.guardar_transcripcion(transcribed_text, self.session_id)

        # Eliminar el archivo de audio temporal
        self.audio_manager.eliminar_audio(audio_filename)

# Instanciar las clases
audio_manager = AudioManager(AUDIO_DIR)
transcription_manager = TranscriptionManager(TRANSCRIPCIONES_DIR, whisper.load_model("medium"))
voice_assistant = VoiceAssistant(audio_manager, transcription_manager, FLASK_URL, session_id)

# Iniciar la detección de la wake word
voice_assistant.detectar_wake_word()
