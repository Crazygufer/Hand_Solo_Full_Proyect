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

# Definir rutas específicas para archivos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
TRANSCRIPCIONES_DIR = os.path.join(BASE_DIR, "transcripciones")

# Crear carpetas si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# URL del servidor Flask (ajusta esto si estás ejecutando Flask en otro host o puerto)
FLASK_URL = 'http://127.0.0.1:5000/update_transcription'

class AudioManager:
    def __init__(self, audio_dir):
        self.audio_dir = audio_dir
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def grabar_audio(self):
        with self.mic as source:
            print("Grabando audio...")
            audio_data = self.recognizer.listen(source, timeout=10)

            # Guardar el audio en un archivo temporal dentro de la carpeta audios
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

    def guardar_transcripcion(self, transcription_text):
        transcriptions_file = os.path.join(self.transcripciones_dir, "transcripciones.json")

        # Crear el archivo si no existe
        if not os.path.exists(transcriptions_file):
            with open(transcriptions_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Cargar las transcripciones existentes
        with open(transcriptions_file, 'r', encoding='utf-8') as f:
            transcriptions = json.load(f)

        # Agregar la nueva transcripción
        transcriptions.append({
            "transcription": transcription_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Guardar nuevamente el archivo con la nueva transcripción
        with open(transcriptions_file, 'w', encoding='utf-8') as f:
            json.dump(transcriptions, f, ensure_ascii=False, indent=4)

        print(f"Transcripción guardada en {transcriptions_file}")

class VoiceAssistant:
    def __init__(self, audio_manager, transcription_manager, flask_url):
        self.audio_manager = audio_manager
        self.transcription_manager = transcription_manager
        self.flask_url = flask_url

    def send_transcription_to_flask(self, transcription):
        data = {
            "transcription": transcription,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            requests.post(self.flask_url, json=data)
            print(f"Transcripción enviada al servidor: {transcription}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la transcripción al servidor: {e}")

    def responder_voz(self, mensaje):
        engine.say(mensaje)
        engine.runAndWait()

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

        # Guardar la transcripción en el archivo JSON
        self.transcription_manager.guardar_transcripcion(transcribed_text)

        # Eliminar el archivo de audio temporal
        self.audio_manager.eliminar_audio(audio_filename)

        print("Transcripción completada, volviendo a escuchar para la wake word 'oye handy'...")
        self.send_transcription_to_flask("Transcripción completada, volviendo a escuchar para la wake word 'oye handy'...")
        self.responder_voz("Transcripción completada...")

# Instanciar las clases
audio_manager = AudioManager(AUDIO_DIR)
transcription_manager = TranscriptionManager(TRANSCRIPCIONES_DIR, whisper.load_model("medium"))
voice_assistant = VoiceAssistant(audio_manager, transcription_manager, FLASK_URL)

# Iniciar la detección de la wake word
voice_assistant.detectar_wake_word()
