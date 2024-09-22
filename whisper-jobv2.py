import speech_recognition as sr
import whisper
import os
import json
import time
from datetime import datetime

# Cargar el modelo Whisper
model = whisper.load_model("medium")

# Agregar FFmpeg al PATH
os.environ["PATH"] += os.pathsep + r'C:\webm\bin'  # Ajusta esta ruta a tu instalación de FFmpeg

# Función para detectar la wake word y comenzar a transcribir
def detect_wake_word():
    recognizer = sr.Recognizer()
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

            if "oye handy" in text:
                print("Wake word detectada, comenzando transcripción...")
                transcribe_audio(mic, recognizer)
                break

        except sr.UnknownValueError:
            print("No se entendió el audio.")
        except sr.RequestError as e:
            print(f"Error al conectarse al servicio de reconocimiento de voz; {e}")

# Función para transcribir el audio y guardar los datos en un JSON
def transcribe_audio(mic, recognizer):
    with mic as source:
        print("Grabando audio...")
        audio_data = recognizer.listen(source, timeout=10)  # Graba hasta 10 segundos de audio, ajustable

        # Guardar el audio en un archivo temporal con ruta absoluta
        audio_filename = os.path.abspath("audio_temp.wav")
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
    file_name = "transcripciones.json"

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
