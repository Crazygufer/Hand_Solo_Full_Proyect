import requests
import time

# Dirección IP del ESP32
ESP32_IP = "http://192.168.56.46"

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
    return angulo_coppelia

def convertir_grados_coppelia_a_real_gripper(angulo_coppelia):
    return angulo_coppelia

# Función para enviar los ángulos al ESP32
def establecer_angulo(motor, angulo):
    try:
        url = f"{ESP32_IP}/set_angle?motor={motor}&angle={angulo}"
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Ángulo del motor {motor} establecido a {angulo} grados")
        else:
            print(f"Error al establecer ángulo: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error de conexión: {e}")

# Matriz con las posiciones para cada paso
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
    [90, 60, -90, -20, 0, 90]       # Paso 19
]

# Ejecutar cada paso
for i, angulos in enumerate(posiciones):
    print(f"Moviendo a la posición del Paso {i + 1}:")
    establecer_angulo(0, convertir_grados_coppelia_a_real_servo1(angulos[0]))  # Servo 1
    establecer_angulo(1, convertir_grados_coppelia_a_real_servo2(angulos[1]))  # Servo 2
    establecer_angulo(2, convertir_grados_coppelia_a_real_servo3_espejado(angulos[1]))  # Servo 3 en espejo
    establecer_angulo(3, convertir_grados_coppelia_a_real_servo45(angulos[2]))  # Servo 4
    establecer_angulo(4, convertir_grados_coppelia_a_real_servo45(angulos[3]))  # Servo 5
    establecer_angulo(5, convertir_grados_coppelia_a_real_servo6(angulos[4]))  # Servo 6
    establecer_angulo(6, convertir_grados_coppelia_a_real_gripper(angulos[5]))  # Servo 7 (Gripper)
    time.sleep(1)  # Espera 1 segundo entre cada paso
