from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from app import app
from app.utils.function.auth import validar_usuario, usuario_existe, registrar_usuario
from app.utils.kinematics.Kinematics import calculate_transformation_matrix
from app.utils.kinematics.botar_secuencia import ServoController, BotarSecuencia
from app.utils.detect_action_words.detect_action_words import KeywordDetector  
import subprocess
import json
import os
import sys
import time
import requests
import cv2

# Variable global para almacenar el proceso del script
process = None
transcription_data = ""  # Variable global para almacenar la transcripción
current_session_id = None  # Identificador único para la sesión actual
keyword_detected = ""  # Última palabra clave detect
camera = cv2.VideoCapture(0)  # Cambia el índice si tienes múltiples cámaras

ESP32_IP = "http://192.168.9.46"  # Reemplaza con la IP de tu ESP32

servo_controller = ServoController(ESP32_IP)  # Instancia de controlador de servos
secuencia_botar = BotarSecuencia(servo_controller)  # Instancia de la secuencia de botar
# Funciones de conversión para los servos
def convertir_grados_coppelia_a_real_servo1(angulo_coppelia):
    return angulo_coppelia + 90

def convertir_grados_coppelia_a_real_servo2(angulo_coppelia):
    return angulo_coppelia + 90

def convertir_grados_coppelia_a_real_servo3_espejado(angulo_coppelia):
    return 180 - (angulo_coppelia + 90)  # Espejo de Servo 2

def convertir_grados_coppelia_a_real_servo45(angulo_coppelia):
    return -angulo_coppelia + 90

def convertir_grados_coppelia_a_real_servo6(angulo_coppelia):
    return angulo_coppelia  # Sin cambios específicos

def convertir_grados_coppelia_a_real_gripper(angulo_coppelia):
    return angulo_coppelia  # Sin cambios específicos para el gripper

# Ruta para la página principal (index)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el registro de nuevos usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario ya existe
        if usuario_existe(username):
            error = 'El nombre de usuario ya está registrado. Elige otro.'
            return render_template('register.html', error=error)

        # Guardar el nuevo usuario en el archivo CSV
        registrar_usuario(username, password)
        flash('Usuario registrado con éxito. Por favor, inicia sesión.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar usuario en el archivo CSV
        if validar_usuario(username, password):
            return redirect(url_for('panel'))  # Redirigir al panel
        else:
            error = 'Nombre de usuario o contraseña incorrectos'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Ruta para el panel después del login
@app.route('/panel')
def panel():
    return render_template('panel.html')

# Ruta para la página de transcripción
@app.route('/transcripcion')
def transcripcion():
    return render_template('transcripcion.html')

# Ruta para iniciar el proceso de escucha
@app.route('/start_listening', methods=['GET'])
def start_listening_route():
    global process
    if process is None:
        # Ejecuta el script de escucha como un proceso independiente usando el nuevo whisper_post_transcribe con POO
        process = subprocess.Popen([sys.executable, "app/utils/voice/whisper_post_transcribe.py"])
        return jsonify({"status": "Escucha iniciada"})
    else:
        return jsonify({"status": "La escucha ya está en curso"})

# Ruta para detener el proceso de escucha
@app.route('/stop_listening', methods=['GET'])
def stop_listening_route():
    global process
    if process is not None:
        process.terminate()
        process = None
        return jsonify({"status": "Escucha detenida"})
    else:
        return jsonify({"status": "No hay escucha en curso"})

# Ruta para recibir las transcripciones desde el script
@app.route('/update_transcription', methods=['POST'])
def update_transcription():
    global transcription_data
    transcription_data = request.json.get('transcription', '')
    return jsonify({"status": "Transcripción recibida"})

# Ruta para obtener la última transcripción desde el archivo transcripciones.json
@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    transcriptions_file = os.path.join('app', 'transcripciones', 'transcripciones.json')

    try:
        # Leer el archivo transcripciones.json
        with open(transcriptions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                last_transcription = data[-1]  # Obtener la última transcripción
                return jsonify({
                    "transcription": f"Última transcripción realizada: {last_transcription['transcription']}",
                    "timestamp": last_transcription['timestamp']
                })
            else:
                return jsonify({"transcription": "No hay transcripciones disponibles."})
    except FileNotFoundError:
        return jsonify({"transcription": "El archivo transcripciones.json no se encontró."})
    except json.JSONDecodeError:
        return jsonify({"transcription": "Error al leer el archivo transcripciones.json."})

# Ruta para obtener el estado (logs) desde el script
@app.route('/get_state', methods=['GET'])
def get_state():
    global transcription_data  # Aquí se almacenan los mensajes de estado
    return jsonify({"state": transcription_data or "Esperando activación..."})

# Rutas para otras funciones
@app.route('/palabras_clave')
def palabras_clave():
    return render_template('palabras_clave.html')

#@app.route('/vision_artificial')
#def vision_artificial():
#    return render_template('vision_artificial.html')

@app.route('/cinematica_directa')
def cinematica_directa():
    return render_template('cinematica_directa.html')

@app.route('/cinematica_inversa')
def cinematica_inversa():
    return render_template('cinematica_inversa.html')

#@app.route('/Kinematics')
#def kinematics():
#    return render_template('kinematics.html')

@app.route('/Kinematics', methods=['GET', 'POST'])
def kinematics():
    if request.method == 'POST':
        # Obtener los datos enviados en la solicitud
        data = request.json
        q1 = data.get('q1', 0)
        q2 = data.get('q2', 0)
        q3 = data.get('q3', 0)
        q4 = data.get('q4', 0)
        q5 = data.get('q5', 0)

        # Calcular la matriz de transformación y valores adicionales
        result, error = calculate_transformation_matrix(q1, q2, q3, q4, q5)

        # Manejar la respuesta según si hubo un error
        if error:
            return jsonify({"error": error}), 500

        # Si el cálculo fue exitoso, devolver la matriz de transformación y valores adicionales
        return jsonify({
            "matrix": str(result["matrix"]),
            "Px": result["Px"],
            "Py": result["Py"],
            "Pz": result["Pz"],
            "a": result["a"],
            "b": result["b"],
            "g": result["g"]
        })

    # Renderizar la página de cinemáticas en caso de una solicitud GET
    return render_template('kinematics.html')

@app.route('/modo_automatico')
def modo_automatico():
    return render_template('modo_automatico.html')


@app.route('/automatic_mode/start_listening', methods=['GET'])
def automatic_mode_start_listening():
    global process, current_session_id, transcription_data, keyword_detected
    if process is None:
        # Genera un identificador de sesión único
        current_session_id = str(int(time.time()))
        
        # Limpia los datos de la última transcripción y palabra clave
        transcription_data = ""
        keyword_detected = ""

        # Ejecuta el script de escucha como proceso independiente, pasando el session_id
        process = subprocess.Popen([sys.executable, "app/utils/voice/whisper_post_transcribe.py", current_session_id])
        return jsonify({"status": "Modo Automático - Escucha iniciada", "session_id": current_session_id})
    else:
        return jsonify({"status": "Modo Automático - La escucha ya está en curso"})


@app.route('/automatic_mode/stop_listening', methods=['GET'])
def automatic_mode_stop_listening():
    global process, transcription_data, keyword_detected, current_session_id
    if process is not None:
        process.terminate()
        process = None
        transcription_data = ""  # Restablece transcripción
        keyword_detected = ""  # Restablece palabra clave
        current_session_id = None  # Restablece session_id
        return jsonify({"status": "Modo Automático - Escucha detenida"})
    else:
        return jsonify({"status": "Modo Automático - No hay escucha en curso"})

# Endpoint para obtener el estado actual en modo automático
@app.route('/automatic_mode/get_state', methods=['GET'])
def automatic_mode_get_state():
    global transcription_data
    return jsonify({"state": transcription_data or "Esperando activación en Modo Automático..."})

# Endpoint para obtener la última transcripción en modo automático
@app.route('/automatic_mode/get_transcription', methods=['GET'])
def automatic_mode_get_transcription():
    transcriptions_file = os.path.join('app', 'transcripciones', 'transcripciones.json')

    try:
        with open(transcriptions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                last_transcription = data[-1]
                return jsonify({
                    "transcription": f"Última transcripción en Modo Automático: {last_transcription['transcription']}",
                    "timestamp": last_transcription['timestamp']
                })
            else:
                return jsonify({"transcription": "No hay transcripciones disponibles en Modo Automático."})
    except FileNotFoundError:
        return jsonify({"transcription": "El archivo de transcripciones no se encontró en Modo Automático."})
    except json.JSONDecodeError:
        return jsonify({"transcription": "Error al leer el archivo de transcripciones en Modo Automático."})

@app.route('/update_transcription_auto', methods=['POST'])
def update_transcription_auto():
    global transcription_data, keyword_detected, current_session_id

    # Obtiene el identificador de sesión desde la solicitud
    session_id = request.json.get('session_id')
    
    # Verifica si la transcripción pertenece a la sesión actual
    if session_id == current_session_id:
        transcription_data = request.json.get('transcription', '')
        keyword_detected = request.json.get('keyword', '')
        return jsonify({"status": "Transcripción recibida para la sesión actual"})
    else:
        return jsonify({"status": "Transcripción ignorada (sesión antigua)"})

# Endpoint para obtener la última transcripción en modo automático
@app.route('/automatic_mode/get_transcription', methods=['GET'])
def get_last_transcription():
    transcriptions_file = os.path.join('app', 'transcripciones', 'transcripciones.json')

    try:
        with open(transcriptions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                last_transcription = data[-1]
                transcription_text = last_transcription.get("transcription", "Aquí aparecerá la transcripción...")
                return jsonify({
                    "transcription": transcription_text,
                    "timestamp": last_transcription.get("timestamp", "")
                })
            else:
                return jsonify({"transcription": "No hay transcripciones disponibles.", "timestamp": ""})
    except FileNotFoundError:
        return jsonify({"transcription": "El archivo transcripciones.json no se encontró.", "timestamp": ""})
    except json.JSONDecodeError:
        return jsonify({"transcription": "Error al leer el archivo de transcripciones.", "timestamp": ""})

# Endpoint para obtener la palabra clave detectada y la acción del robot en modo automático
@app.route('/automatic_mode/get_keyword', methods=['GET'])
def get_detected_keyword():
    result_file = os.path.join('app', 'transcripciones', 'resultados_palabras_clave.json')

    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({
            "keyword": "Ninguna palabra clave detectada aún.",
            "action": "Esperando comandos..."
        })
    except json.JSONDecodeError:
        return jsonify({
            "keyword": "Error al leer el archivo de resultados.",
            "action": "Esperando comandos..."
        })
    
# Endpoint para recibir y procesar el ángulo
@app.route('/set_angle', methods=['POST'])
def set_angle():
    data = request.get_json()
    servo = data.get('motor')
    angulo = data.get('angle')

    # Validar que el ángulo esté en el rango permitido (-90 a 90)
    if angulo < -90 or angulo > 90:
        return jsonify({"error": f"Ángulo {angulo} fuera del rango permitido (-90 a 90)."}), 400

    # Aplicar la conversión de acuerdo al servo
    if servo == 1:  # Servo 1 corresponde a q1
        angulo_convertido = convertir_grados_coppelia_a_real_servo1(angulo)
        enviar_angulo_al_esp32(0, angulo_convertido)
    elif servo == 2:  # Servo 2 corresponde a q2.1, Servo 3 en espejo
        angulo_convertido = convertir_grados_coppelia_a_real_servo2(angulo)
        enviar_angulo_al_esp32(1, angulo_convertido)  # Enviar para Servo 2
        enviar_angulo_al_esp32(2, convertir_grados_coppelia_a_real_servo3_espejado(angulo))  # Enviar espejado para Servo 3
    elif servo == 4:  # Servo 4 corresponde a q3
        angulo_convertido = convertir_grados_coppelia_a_real_servo45(angulo)
        enviar_angulo_al_esp32(3, angulo_convertido)
    elif servo == 5:  # Servo 5 corresponde a q4
        angulo_convertido = convertir_grados_coppelia_a_real_servo45(angulo)
        enviar_angulo_al_esp32(4, angulo_convertido)
    elif servo == 6:  # Servo 6 corresponde a q5
        angulo_convertido = convertir_grados_coppelia_a_real_servo6(angulo)
        enviar_angulo_al_esp32(5, angulo_convertido)
    elif servo == 7:  # Servo 7 corresponde al gripper (efector)
        angulo_convertido = convertir_grados_coppelia_a_real_gripper(angulo)
        print("el angulo convertido es: ", angulo_convertido)
        enviar_angulo_al_esp32(6, angulo_convertido)
    else:
        return jsonify({"error": f"Servo {servo} no reconocido."}), 400

    return jsonify({"message": f"Ángulo del servo {servo} establecido a {angulo} grados (convertido a {angulo_convertido})"}), 200

# Función auxiliar para enviar ángulos al ESP32
def enviar_angulo_al_esp32(servo, angulo_convertido):
    esp32_url = f"{ESP32_IP}/set_angle?motor={servo}&angle={angulo_convertido}"
    try:
        response = requests.get(esp32_url)
        if response.status_code != 200:
            print(f"Error al establecer ángulo para servo {servo}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error de conexión al ESP32 para servo {servo}: {e}")

# Ruta para ejecutar la secuencia de botar
@app.route('/ejecutar_botar', methods=['POST'])
def ejecutar_botar():
    try:
        # Ejecuta la secuencia de botar usando el método de la clase BotarSecuencia
        secuencia_botar.ejecutar_secuencia()
        return jsonify({"message": "Secuencia de botar ejecutada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al ejecutar secuencia de botar: {e}"}), 500
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    



# Ruta para recibir la transcripción y detectar palabras clave
@app.route('/detect_action', methods=['POST'])
def detect_action():
    data = request.get_json()
    transcription_text = data.get("transcription", "")
    
    # Define la ruta correcta para el archivo actions.json
    acciones_path = r"C:\Users\enfparedes\Contacts\Hand_Solo_Full_Proyect\app\utils\detect_action_words\actions.json"
    keyword_detector = KeywordDetector(acciones_path)
    
    # Detecta la acción basada en la transcripción recibida
    accion_detectada = keyword_detector.detectar_accion(transcription_text)
    
    if accion_detectada:
        return jsonify({"status": "Acción detectada", "keyword": accion_detectada}), 200
    else:
        return jsonify({"status": "Sin acción detectada"}), 200
    
@app.route('/vision_artificial')
def vision_artificial():
    return render_template('VisionArtificial.html')

def generate_video_feed():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convertir el frame a JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')