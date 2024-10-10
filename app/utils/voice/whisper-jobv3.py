import speech_recognition as sr
import whisper
import os
import json
import time
from datetime import datetime
import sys
import pyttsx3  # Importar pyttsx3 para generar voz

# Configurar pyttsx3 para la respuesta de voz
engine = pyttsx3.init()

# Cargar el modelo Whisper
model = whisper.load_model("medium")

# Definir rutas específicas para archivos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Directorio base donde se encuentra este archivo
AUDIO_DIR = os.path.join(BASE_DIR, "audios")  # Carpeta audios
TRANSCRIPCIONES_DIR = os.path.join(BASE_DIR, "transcripciones")  # Carpeta transcripciones

# Crear carpetas si no existen
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPCIONES_DIR, exist_ok=True)

# Función para generar la respuesta de voz
def responder_voz(mensaje):
    engine.say(mensaje)
    engine.runAndWait()

# Función para detectar la wake word y comenzar a transcribir
def detect_wake_word():
    recognizer = sr.Recognizer()
    # Para usar en notebook
    mic = sr.Microphone()

    print("Esperando la wake word: 'oye handy'...")

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Escuchando...")
            audio = recognizer.listen(source)

        try:
            # Usar reconocimiento de Google para detectar la wake word
            text = recognizer.recognize_google(audio, language="es-ES").lower()
            print(f"Has dicho: {text}")

            if "oye handy salir" in text:
                print("Frase de salida detectada: 'oye handy salir'. Terminando programa...")
                responder_voz("Adiós, hasta la próxima.")
                sys.exit()  # Terminar el programa

            if "oye handy" in text:
                print("Wake word detectada, comenzando transcripción...")
                responder_voz("Hola, ¿en qué puedo ayudarte?")
                transcribe_audio(mic, recognizer)

        except sr.UnknownValueError:
            print("No se entendió el audio.")
        except sr.RequestError as e:
            print(f"Error al conectarse al servicio de reconocimiento de voz; {e}")

# Función para transcribir el audio y guardar los datos en un JSON
def transcribe_audio(mic, recognizer):
    with mic as source:
        print("Grabando audio...")
        audio_data = recognizer.listen(source, timeout=10)  # Graba hasta 10 segundos de audio, ajustable
        print("Audio Grabado...")

        # Guardar el audio en un archivo temporal dentro de la carpeta audios
        audio_filename = os.path.join(AUDIO_DIR, "audio_temp.wav")
        with open(audio_filename, "wb") as f:
            f.write(audio_data.get_wav_data())

        # Verificar si el archivo existe antes de transcribir
        while not os.path.exists(audio_filename):
            print(f"Esperando que el archivo de audio {audio_filename} esté disponible...")
            time.sleep(1)

        # Usar Whisper para transcribir el archivo de audio
        print(f"Archivo de audio encontrado: {audio_filename}, iniciando transcripción...")
        result = model.transcribe(audio_filename, language="es")
        transcribed_text = result["text"]

        # Obtener duración del audio (en segundos)
        duration = get_audio_duration(audio_filename)

        # Guardar la transcripción y otros datos en un JSON
        save_transcription_json(transcribed_text, duration)

        # Eliminar el archivo de audio temporal
        os.remove(audio_filename)

        # Volver a escuchar después de la transcripción
        print("Volviendo a escuchar para la wake word 'oye handy'...")

# Función para obtener la duración del archivo de audio
def get_audio_duration(audio_file):
    import wave
    with wave.open(audio_file, 'rb') as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        duration = frames / float(rate)
        return duration

# Función para guardar los datos en un archivo JSON
def save_transcription_json(transcription, audio_duration):
    file_name = os.path.join(TRANSCRIPCIONES_DIR, "transcripciones.json")

    # Si ya existe el archivo, carga los datos existentes
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    # Determinar el próximo ID de interacción
    interaction_id = len(data) + 1

    # Agregar la nueva transcripción con fecha, hora, y duración
    data.append({
        "interaction_id": interaction_id,
        "transcription": transcription,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "audio_duration": f"{audio_duration:.1f} segundos"
    })

    # Guardar en el archivo JSON
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Transcripción guardada en {file_name}")

# Iniciar la detección de la wake word
detect_wake_word()
