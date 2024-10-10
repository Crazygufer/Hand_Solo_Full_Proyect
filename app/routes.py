from flask import render_template, request, redirect, url_for, flash
from app import app
from app.utils.function.auth import validar_usuario, usuario_existe, registrar_usuario

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

@app.route('/transcripcion')
def transcripcion():
    return render_template('transcripcion.html')

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

