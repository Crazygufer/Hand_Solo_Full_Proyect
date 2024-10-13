import speech_recognition as sr
import whisper
import os
import json
import time
from datetime import datetime
import sys
import pyttsx3
import requests  # Para hacer POST requests a Flask

# Configurar pyttsx3 para la respuesta de voz
engine = pyttsx3.init()

# Cargar el modelo Whisper
model = whisper.load_model("medium")

# Definir rutas específicas para archivos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
TRANSCRIPCIONES_DIR = os.path.join(BASE_DIR, "transcripciones")

# Crear carpetas si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# URL del servidor Flask (ajusta esto si estás ejecutando Flask en otro host o puerto)
FLASK_URL = 'http://127.0.0.1:5000/update_transcription'

# Función para enviar la transcripción al servidor Flask
def send_transcription_to_flask(transcription):
    data = {
        "transcription": transcription,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        requests.post(FLASK_URL, json=data)
        print(f"Transcripción enviada al servidor: {transcription}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la transcripción al servidor: {e}")

# Función para generar la respuesta de voz
def responder_voz(mensaje):
    engine.say(mensaje)
    engine.runAndWait()

def detect_wake_word():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Esperando la wake word: 'oye handy'...")
    send_transcription_to_flask("Esperando la wake word: 'oye handy'...")
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Escuchando...")
            send_transcription_to_flask("Escuchando...")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language="es-ES").lower()
            print(f"Has dicho: {text}")
            send_transcription_to_flask(f"Has dicho: {text}")

            if "oye handy salir" in text:
                print("Frase de salida detectada: 'oye handy salir'. Terminando programa...")
                send_transcription_to_flask("Frase de salida detectada: 'oye handy salir'. Terminando Programa...")
                responder_voz("Adiós, hasta la próxima.")
                sys.exit()

            if "oye handy" in text:
                print("Wake word detectada, comenzando transcripción...")
                send_transcription_to_flask("Wake word detectada, comenzando transcripción...")
                responder_voz("Hola, ¿en qué puedo ayudarte?")
                transcribe_audio(mic, recognizer)

        except sr.UnknownValueError:
            print("No se entendió el audio.")
            send_transcription_to_flask("No se entendió el audio")
            responder_voz("No entendí, ¿Puedes repetirlo por favor?")
        except sr.RequestError as e:
            print(f"Error al conectarse al servicio de reconocimiento de voz: {e}")

# Función para transcribir el audio y enviar la transcripción a Flask y al archivo JSON
def transcribe_audio(mic, recognizer):
    with mic as source:
        print("Grabando audio...")
        send_transcription_to_flask("Grabando audio...")
        audio_data = recognizer.listen(source, timeout=10)

        # Guardar el audio en un archivo temporal dentro de la carpeta audios
        audio_filename = os.path.join(AUDIO_DIR, "audio_temp.wav")
        with open(audio_filename, "wb") as f:
            f.write(audio_data.get_wav_data())

        # Verificar si el archivo existe antes de transcribir
        while not os.path.exists(audio_filename):
            print(f"Esperando que el archivo de audio {audio_filename} esté disponible...")
            send_transcription_to_flask(f"Esperando que el archivo de audio {audio_filename} esté disponible...")
            time.sleep(1)

        # Usar Whisper para transcribir el archivo de audio
        print(f"Archivo de audio encontrado: {audio_filename}, iniciando transcripción...")
        send_transcription_to_flask(f"Archivo de audio encontrado, iniciando transcripción...")
        result = model.transcribe(audio_filename, language="es")
        transcribed_text = result["text"]

        # Enviar la transcripción a Flask
        send_transcription_to_flask(transcribed_text)

        # Guardar la transcripción en el archivo JSON
        save_transcription_json(transcribed_text)

        # Eliminar el archivo de audio temporal
        os.remove(audio_filename)

        print("Transcripción completada, volviendo a escuchar para la wake word 'oye handy'...")
        send_transcription_to_flask("Transcripción completada, volviendo a escuchar para la wake word 'oye handy'...")
        responder_voz("Transcripción completada...")

# Función para guardar la transcripción en un archivo JSON
def save_transcription_json(transcription_text):
    transcriptions_file = os.path.join(TRANSCRIPCIONES_DIR, "transcripciones.json")

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

detect_wake_word()
