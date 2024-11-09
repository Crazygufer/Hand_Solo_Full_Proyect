import time
import requests

# Dirección IP del ESP32
ESP32_IP = "192.168.56.46"  # Solo la IP, sin http://

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

# Función para enviar el ángulo al ESP32
def enviar_angulo_al_esp32(servo, angulo_convertido):
    url = f"http://{ESP32_IP}/set_angle?motor={servo}&angle={angulo_convertido}"  # Concatenar http:// correctamente
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Ángulo del motor {servo} establecido a {angulo_convertido} grados")
        else:
            print(f"Error al establecer ángulo: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")

# Función para aplicar la lógica de set_angle
def establecer_angulo(servo, angulo):
    if servo == 1:
        angulo_convertido = convertir_grados_coppelia_a_real_servo1(angulo)
        enviar_angulo_al_esp32(0, angulo_convertido)
    elif servo == 2:
        angulo_convertido = convertir_grados_coppelia_a_real_servo2(angulo)
        enviar_angulo_al_esp32(1, angulo_convertido)  # Servo 2
        enviar_angulo_al_esp32(2, convertir_grados_coppelia_a_real_servo3_espejado(angulo))  # Servo 3 espejado
    elif servo == 4:
        angulo_convertido = convertir_grados_coppelia_a_real_servo45(angulo)
        enviar_angulo_al_esp32(3, angulo_convertido)
    elif servo == 5:
        angulo_convertido = convertir_grados_coppelia_a_real_servo45(angulo)
        enviar_angulo_al_esp32(4, angulo_convertido)
    elif servo == 6:
        angulo_convertido = convertir_grados_coppelia_a_real_servo6(angulo)
        enviar_angulo_al_esp32(5, angulo_convertido)
    elif servo == 7:
        angulo_convertido = convertir_grados_coppelia_a_real_gripper(angulo)
        enviar_angulo_al_esp32(6, angulo_convertido)
    else:
        print(f"Servo {servo} no reconocido.")

# Lista de posiciones para los primeros 6 pasos
# Cada sublista corresponde a una posición en formato [servo1, servo2, servo4, servo5, servo6, servo7]
posiciones = [
    [0, 0, 0, 0, 90, 90],    # Paso 1
    [-35, 20, -20, -60, 90, 10],    # Paso 2
    [-35, 30, -60, 60, 0, 90],      # Paso 3
    [-35, 60, -60, 60, 0, 90],      # Paso 4
    [-35, 60, -60, 30, 0, 90],      # Paso 5
    [-35, 70, -60, 30, 0, 90],      # Paso 6
    [-35, 70, -70, 30, 0, 90],      # Paso 7
    [-35, 75, -60, 30, 0, 90],      # Paso 8
    [-35, 75, -50, 30, 0, 90],      # Paso 9
    [-35, 80, -50, 30, 0, 90],      # Paso 10
    [-35, 80, -40, 30, 0, 90],      # Paso 11
    [-35, 85, -35, 30, 0, 90],      # Paso 12
    [-35, 85, -30, 25, 0, 90],      # Paso 13
    [-35, 85, -30, 25, 0, 20],      # Paso 14
    [-35, 60, -30, 25, 0, 20],      # Paso 15
    [-35, 0, -30, 0, 0, 20],        # Paso 16
    [-35, 0, -90, -20, 0, 20],      # Paso 17
    [90, 0, -90, -20, 0, 20],       # Paso 18
    [90, 60, -90, -20, 0, 90],      # Paso 19
    [0, 0, 0, 0, 90, 90]            # Paso 20
]

# Iterar sobre cada posición y aplicar los ángulos a los servos
for paso, angulos in enumerate(posiciones, start=1):
    print(f"\nMoviendo a la posición del Paso {paso}:")
    
    # Enviar el ángulo correspondiente a cada servo usando la función establecer_angulo
    establecer_angulo(1, angulos[0])  # Servo 1 (q1)
    establecer_angulo(2, angulos[1])  # Servo 2 (q2.1) y Servo 3 (q2.2 espejado)
    establecer_angulo(4, angulos[2])  # Servo 4 (q3)
    establecer_angulo(5, angulos[3])  # Servo 5 (q4)
    establecer_angulo(6, angulos[4])  # Servo 6 (q5)
    establecer_angulo(7, angulos[5])  # Servo 7 (gripper)
    
    # Esperar 1 segundo antes de pasar a la siguiente posición
    time.sleep(1)
