import time
import requests

ESP32_IP = "http://192.168.9.46"  # Incluye el prefijo http:// aquí

class ServoController:
    """Clase para manejar el envío de ángulos a los servos del ESP32."""

    def __init__(self, esp32_ip):
        self.esp32_ip = esp32_ip

    def convertir_grados(self, servo, angulo):
        """Convierte el ángulo de Coppelia a real dependiendo del servo."""
        conversiones = {
            1: lambda x: x + 90,
            2: lambda x: x + 90,
            3: lambda x: 180 - (x + 90),  # Espejo de Servo 2
            4: lambda x: -x + 90,
            5: lambda x: -x + 90,
            6: lambda x: x,               # Sin cambios específicos
            7: lambda x: x                # Gripper sin cambios específicos
        }
        return conversiones.get(servo, lambda x: x)(angulo)

    def enviar_angulo(self, motor, angulo_convertido):
        """Envía el ángulo al ESP32 para un motor específico."""
        url = f"{self.esp32_ip}/set_angle?motor={motor}&angle={angulo_convertido}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Ángulo del motor {motor} establecido a {angulo_convertido} grados")
            else:
                print(f"Error al establecer ángulo: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error de conexión: {e}")

    def establecer_angulo(self, servo, angulo):
        """Convierte el ángulo y lo envía al ESP32."""
        angulo_convertido = self.convertir_grados(servo, angulo)
        motor = servo - 1  # Ajusta para que el índice de motor coincida con el código funcional inicial
        self.enviar_angulo(motor, angulo_convertido)

class BotarSecuencia:
    """Clase para manejar la secuencia de movimientos del robot."""

    def __init__(self, servo_controller):
        self.servo_controller = servo_controller
        self.posiciones = [
            [0, 0, 0, 0, 90, 90],    # Paso 1
            [-35, 20, -20, -60, 90, 10],    # Paso 2
            [-35, 30, -60, 60, 75, 90],      # Paso 3
            [-35, 60, -60, 60, 75, 90],      # Paso 4
            [-35, 60, -60, 30, 75, 90],      # Paso 5
            [-35, 70, -60, 30, 75, 90],      # Paso 6
            [-35, 70, -70, 30, 75, 90],      # Paso 7
            [-35, 75, -60, 30, 75, 90],      # Paso 8
            [-35, 75, -50, 30, 75, 90],      # Paso 9
            [-35, 80, -50, 30, 75, 90],      # Paso 10
            [-35, 80, -40, 30, 75, 90],      # Paso 11
            [-35, 85, -35, 30, 75, 90],      # Paso 12
            [-35, 85, -30, 25, 75, 90],      # Paso 13
            [-35, 85, -30, 25, 75, 20],      # Paso 14
            [-35, 60, -30, 25, 75, 20],      # Paso 15
            [-35, 0, -30, 0, 75, 20],        # Paso 16
            [-35, 0, -90, -20, 75, 20],      # Paso 17
            [90, 0, -90, -20, 75, 20],       # Paso 18
            [90, 60, -90, -20, 75, 90],      # Paso 19
            [0, 0, -70, -20, 75, 90],       # Paso 20
            [0, 0, 0, 0, 90, 90]            # Paso 21
        ]

    def ejecutar_secuencia(self):
        """Ejecuta la secuencia de movimientos en los servos."""
        for paso, angulos in enumerate(self.posiciones, start=1):
            print(f"\nMoviendo a la posición del Paso {paso}:")
            self.servo_controller.establecer_angulo(1, angulos[0])  # Servo 1 (q1)
            self.servo_controller.establecer_angulo(2, angulos[1])  # Servo 2 (q2.1)
            self.servo_controller.establecer_angulo(3, angulos[1])  # Servo 3 espejado
            self.servo_controller.establecer_angulo(4, angulos[2])  # Servo 4 (q3)
            self.servo_controller.establecer_angulo(5, angulos[3])  # Servo 5 (q4)
            self.servo_controller.establecer_angulo(6, angulos[4])  # Servo 6 (q5)
            self.servo_controller.establecer_angulo(7, angulos[5])  # Servo 7 (gripper)
            time.sleep(1)

if __name__ == "__main__":
    ESP32_IP = "http://192.168.56.46"
    
    # Instanciar controlador de servos y secuencia de botar
    servo_controller = ServoController(ESP32_IP)
    secuencia_botar = BotarSecuencia(servo_controller)
    
    print("Iniciando secuencia de botar...")
    secuencia_botar.ejecutar_secuencia()
