from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from app.utils.function.auth import validar_usuario, usuario_existe, registrar_usuario
import subprocess
import json
from app import app, socketio


# Variable global para almacenar el proceso del script
process = None

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

# Ruta para iniciar la escucha del script
@app.route('/start_listening', methods=['GET'])
def start_listening_route():
    global process
    if process is None:
        # Ejecuta el script de escucha como un proceso independiente
        process = subprocess.Popen(["python", "app/utils/voice/whisper-jobv3.py"])
        #process = subprocess.Popen(["python", "app/utils/voice/whisper-jobv3-adaptacionPC.py"])
        return jsonify({"status": "Escucha iniciada"})
    else:
        return jsonify({"status": "La escucha ya está en curso"})

# Ruta para detener la escucha del script
@app.route('/stop_listening', methods=['GET'])
def stop_listening_route():
    global process
    if process is not None:
        # Termina el proceso si está corriendo
        process.terminate()
        process = None
        return jsonify({"status": "Escucha detenida"})
    else:
        return jsonify({"status": "No hay escucha en curso"})

# Ruta para obtener la transcripción más reciente
@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    try:
        with open('app/utils/voice/transcripciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            last_transcription = data[-1] if data else {"transcription": "No hay transcripciones disponibles."}
    except FileNotFoundError:
        last_transcription = {"transcription": "No se encontró el archivo de transcripciones."}

    return jsonify(last_transcription)

# Rutas para otras funciones
@app.route('/palabras_clave')
def palabras_clave():
    return render_template('palabras_clave.html')

@app.route('/vision_artificial')
def vision_artificial():
    return render_template('vision_artificial.html')

@app.route('/cinematica_directa')
def cinematica_directa():
    return render_template('cinematica_directa.html')

@app.route('/cinematica_inversa')
def cinematica_inversa():
    return render_template('cinematica_inversa.html')

@app.route('/modo_automatico')
def modo_automatico():
    return render_template('modo_automatico.html')

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    socketio.emit('log', {'message': 'Conexión establecida con el servidor'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

