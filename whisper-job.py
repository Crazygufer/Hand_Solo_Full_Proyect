import os
import whisper

# Agregar FFmpeg al PATH
os.environ["PATH"] += os.pathsep + r'C:\webm\bin'  # Ajusta esta ruta a tu instalación de FFmpeg

# Cargar el modelo Whisper
model = whisper.load_model("medium")

# Definir las rutas de las carpetas
audio_folder = "audios"
transcription_folder = "transcripciones"

# Asegurarse de que la carpeta de transcripciones exista, si no, se crea
if not os.path.exists(transcription_folder):
    os.makedirs(transcription_folder)

# Función para procesar archivos de audio y generar transcripciones
def transcribe_audio_files():
    # Listar todos los archivos en la carpeta de audios
    for audio_file in os.listdir(audio_folder):
        # Verificar que sea un archivo de audio válido (.ogg, .mp3, .wav)
        if audio_file.endswith(('.ogg', '.mp3', '.wav')):
            audio_path = os.path.join(audio_folder, audio_file)
            print(f"Procesando archivo: {audio_path}")

            # Usar Whisper para transcribir el archivo de audio
            result = model.transcribe(audio_path, language="es")  # Cambia el idioma si es necesario
            transcribed_text = result['text']

            # Crear el archivo de transcripción con el mismo nombre que el audio
            transcription_file = os.path.join(transcription_folder, f"{os.path.splitext(audio_file)[0]}.txt")
            with open(transcription_file, 'w', encoding='utf-8') as f:
                f.write(transcribed_text)

            print(f"Transcripción guardada en: {transcription_file}")

# Ejecutar la función para transcribir los archivos
transcribe_audio_files()
